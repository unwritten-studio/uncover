#!/usr/bin/env python3
"""Ingest a new version of Bernd's manuscript PDF.

Usage:
    python3 werkzeuge/einpflegen.py PFAD/ZUM/MANUSKRIPT.pdf [--datum JJJJ-MM-TT]

Steps (see docs/EINPFLEGEN.md):
    1. extract   text blocks from the PDF via `pdftotext -bbox-layout`
    2. segment   blocks into passages, page furniture removed
    3. match     against the previous version, so passage IDs stay stable
    4. impact    which cards (zettelkasten/) and scenes (roman/) are affected
    5. report    quellen/berichte/<datum>.md

The PDF itself is never copied into the repository; only the extracted text
and a checksum land in quellen/bernd/<datum>/.

Requires poppler (`pdftotext`, `pdfinfo`). Standard library only otherwise.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import html
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUELLEN = REPO / "quellen" / "bernd"
BERICHTE = REPO / "quellen" / "berichte"
ZETTELKASTEN = REPO / "zettelkasten"
ROMAN = REPO / "roman"

# Two passages count as "the same, edited" above this word-level similarity.
# 0.6 still catches a paragraph split in two (each half scores ~0.67 against
# the original), but not unrelated paragraphs that share common phrases.
AEHNLICHKEIT = 0.6

PASSAGE_ID = re.compile(r"\bp[0-9a-f]{6,40}\b")
SENTENCE_END = tuple('.!?:…"“”»«)')


# --------------------------------------------------------------------------
# Data


@dataclass
class Passage:
    nr: int  # position in this version, 1-based
    seite: int  # page on which the passage starts
    art: str  # "ueberschrift" or "absatz"
    text: str
    id: str = ""
    status: str = ""  # unveraendert | verschoben | bearbeitet | neu
    vorher: str = ""  # previous text, for edited passages
    aehnlichkeit: float = 1.0

    def as_json(self) -> dict:
        return {"id": self.id, "nr": self.nr, "seite": self.seite, "art": self.art, "text": self.text}


@dataclass
class Abgleich:
    passagen: list[Passage]
    entfallen: list[dict] = field(default_factory=list)


# --------------------------------------------------------------------------
# 1. Extract


def run_pdftotext(pdf: Path) -> str:
    return subprocess.run(
        ["pdftotext", "-bbox-layout", str(pdf), "-"], check=True, capture_output=True, text=True
    ).stdout


def pdf_creation_date(pdf: Path) -> str | None:
    out = subprocess.run(["pdfinfo", "-isodates", str(pdf)], check=True, capture_output=True, text=True).stdout
    m = re.search(r"^CreationDate:\s+(\d{4}-\d{2}-\d{2})", out, re.M)
    return m.group(1) if m else None


def parse_bbox(xhtml: str) -> list[list[list[str]]]:
    """Return pages → blocks → lines (each line a string of its words)."""
    pages = []
    for page in re.findall(r"<page\b[^>]*>(.*?)</page>", xhtml, re.S):
        blocks = []
        for block in re.findall(r"<block\b[^>]*>(.*?)</block>", page, re.S):
            lines = []
            for line in re.findall(r"<line\b[^>]*>(.*?)</line>", block, re.S):
                words = [html.unescape(w) for w in re.findall(r"<word\b[^>]*>(.*?)</word>", line, re.S)]
                if words:
                    lines.append(" ".join(words))
            if lines:
                blocks.append(lines)
        pages.append(blocks)
    return pages


# --------------------------------------------------------------------------
# 2. Segment


def join_lines(lines: list[str]) -> str:
    text = ""
    for line in lines:
        line = line.strip()
        if not text:
            text = line
        # Soft hyphenation at line end: "Wort-" + "ende". Keep the hyphen for
        # enumerations like "Nord- und Südseite".
        elif re.search(r"[a-zäöüß]-$", text) and re.match(r"[a-zäöüß]", line) and not re.match(
            r"(und|oder|bis|sowie)\b", line
        ):
            text = text[:-1] + line
        else:
            text += " " + line
    return re.sub(r"\s+", " ", text).strip()


def is_page_number(lines: list[str]) -> bool:
    return len(lines) == 1 and re.fullmatch(r"\d{1,4}", lines[0].strip()) is not None


TOC_LEADER = re.compile(r"(\.{2,}|…)\s*\d{1,3}\s*$")


def is_toc_page(blocks: list[list[str]]) -> bool:
    """Table-of-contents page: several lines end in leader dots + page number.

    Checked per page, not per block, because the PDF export scatters the TOC
    into fragments ("1.", "Prolog: Die Schwelle", "…6") that are meaningless
    on their own. Leader dots before a number practically never occur in
    running text. Dropping the TOC keeps page renumbering out of the report.
    """
    return sum(1 for b in blocks for l in b if TOC_LEADER.search(l)) >= 4


def is_heading(lines: list[str]) -> bool:
    # Headings in the manuscript are single-line blocks without closing
    # punctuation. Short dialogue lines („Und dann?“) end in a quote mark.
    text = lines[0].strip()
    return (
        len(lines) == 1
        and len(text) <= 90
        and not text.endswith(SENTENCE_END[:4])
        and not text.endswith(("“", '"', "”", "«", "»"))
        and not re.search(r"[.!?] ", text)
    )


def segment(pages: list[list[list[str]]]) -> list[Passage]:
    passagen: list[Passage] = []
    for seite, blocks in enumerate(pages, start=1):
        if is_toc_page(blocks):
            continue
        for i, lines in enumerate(blocks):
            if is_page_number(lines):
                continue
            text = join_lines(lines)
            if not text:
                continue
            art = "ueberschrift" if is_heading(lines) else "absatz"
            prev = passagen[-1] if passagen else None
            # A paragraph running across a page break: the previous page ended
            # mid-sentence and this page continues in lower case.
            if (
                i == 0
                and prev is not None
                and prev.art == "absatz"
                and prev.seite < seite
                and not prev.text.endswith(SENTENCE_END)
                and re.match(r"[a-zäöüß]", text)
            ):
                prev.text = join_lines([prev.text, text])
                continue
            passagen.append(Passage(nr=len(passagen) + 1, seite=seite, art=art, text=text))
    return passagen


# --------------------------------------------------------------------------
# 3. Match


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[„“”\"»«]", '"', text)
    text = re.sub(r"[‚‘’'›‹]", "'", text)
    text = re.sub(r"[–—]", "-", text)
    text = text.replace("...", "…")
    return re.sub(r"\s+", " ", text).strip()


def new_id(text: str, taken: set[str]) -> str:
    digest = hashlib.sha1(normalize(text).encode()).hexdigest()
    for length in range(6, 41):
        candidate = "p" + digest[:length]
        if candidate not in taken:
            taken.add(candidate)
            return candidate
    # Identical text appearing more than once: disambiguate by counter.
    n = 2
    while f"p{digest[:6]}{n:x}" in taken:
        n += 1
    taken.add(f"p{digest[:6]}{n:x}")
    return f"p{digest[:6]}{n:x}"


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalize(a).split(), normalize(b).split(), autojunk=False).ratio()


def longest_increasing(seq: list[int]) -> set[int]:
    """Indices into `seq` forming a longest strictly increasing subsequence."""
    if not seq:
        return set()
    tails: list[int] = []  # index into seq of the smallest tail per length
    parent = [-1] * len(seq)
    for i, v in enumerate(seq):
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if seq[tails[mid]] < v:
                lo = mid + 1
            else:
                hi = mid
        if lo > 0:
            parent[i] = tails[lo - 1]
        if lo == len(tails):
            tails.append(i)
        else:
            tails[lo] = i
    keep, k = set(), tails[-1]
    while k != -1:
        keep.add(k)
        k = parent[k]
    return keep


def match(neu: list[Passage], alt: list[dict]) -> Abgleich:
    """Assign IDs to `neu`, inheriting them from `alt` where passages match.

    Exact matches (after normalization) are paired first, in order. The rest
    are paired greedily by descending similarity above AEHNLICHKEIT. Matched
    passages whose relative order changed are marked as moved.
    """
    taken = {p["id"] for p in alt}
    pair: dict[int, int] = {}  # index in neu -> index in alt

    by_text: dict[str, list[int]] = {}
    for j, p in enumerate(alt):
        by_text.setdefault(normalize(p["text"]), []).append(j)
    for i, p in enumerate(neu):
        candidates = by_text.get(normalize(p.text))
        if candidates:
            pair[i] = candidates.pop(0)

    rest_neu = [i for i in range(len(neu)) if i not in pair]
    used = set(pair.values())
    rest_alt = [j for j in range(len(alt)) if j not in used]
    scored = []
    for i in rest_neu:
        # seq2 is fixed per new passage (difflib caches its index); seq1 varies.
        sm = difflib.SequenceMatcher(None, b=normalize(neu[i].text).split(), autojunk=False)
        for j in rest_alt:
            sm.set_seq1(normalize(alt[j]["text"]).split())
            if sm.real_quick_ratio() < AEHNLICHKEIT or sm.quick_ratio() < AEHNLICHKEIT:
                continue
            r = sm.ratio()
            if r >= AEHNLICHKEIT:
                scored.append((r, i, j))
    for r, i, j in sorted(scored, reverse=True):
        if i in pair or j in used:
            continue
        pair[i] = j
        used.add(j)
        neu[i].status = "bearbeitet"
        neu[i].vorher = alt[j]["text"]
        neu[i].aehnlichkeit = round(r, 3)

    order = sorted(pair)  # neu indices in reading order
    in_order = longest_increasing([pair[i] for i in order])
    for k, i in enumerate(order):
        neu[i].id = alt[pair[i]]["id"]
        if not neu[i].status:
            neu[i].status = "unveraendert" if k in in_order else "verschoben"
    for i, p in enumerate(neu):
        if i not in pair:
            p.id = new_id(p.text, taken)
            p.status = "neu"

    entfallen = [alt[j] for j in range(len(alt)) if j not in used]
    return Abgleich(passagen=neu, entfallen=entfallen)


# --------------------------------------------------------------------------
# 4. Impact


def card_sources(zettelkasten: Path) -> dict[str, set[str]]:
    """Card (file stem) → passage IDs it cites."""
    if not zettelkasten.is_dir():
        return {}
    return {f.stem: set(PASSAGE_ID.findall(f.read_text())) for f in sorted(zettelkasten.rglob("*.md"))}


def impact(betroffen: set[str], zettelkasten: Path, roman: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Return (card → affected passages, scene → affected cards)."""
    karten = {k: q & betroffen for k, q in card_sources(zettelkasten).items() if q & betroffen}
    szenen: dict[str, set[str]] = {}
    if karten and roman.is_dir():
        for f in sorted(roman.rglob("*.md")):
            text = f.read_text()
            hits = {k for k in karten if re.search(rf"\b{re.escape(k)}\b", text)}
            if hits:
                szenen[str(f.relative_to(roman))] = hits
    return karten, szenen


# --------------------------------------------------------------------------
# 5. Write


def word_count(passagen: list[Passage]) -> int:
    return sum(len(p.text.split()) for p in passagen)


def write_version(ziel: Path, passagen: list[Passage], manifest: dict) -> None:
    ziel.mkdir(parents=True)
    md = []
    for p in passagen:
        md.append(f"## {p.text}" if p.art == "ueberschrift" else p.text)
    (ziel / "manuskript.md").write_text("\n\n".join(md) + "\n")
    with (ziel / "passagen.jsonl").open("w") as f:
        for p in passagen:
            f.write(json.dumps(p.as_json(), ensure_ascii=False) + "\n")
    (ziel / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def excerpt(text: str, n: int = 160) -> str:
    text = text.replace("|", "\\|")
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def report(datum: str, manifest: dict, abgleich: Abgleich, karten: dict, szenen: dict) -> str:
    ps = abgleich.passagen
    count = {s: sum(1 for p in ps if p.status == s) for s in ("unveraendert", "verschoben", "bearbeitet", "neu")}
    out = [f"# Fassung vom {datum}", ""]
    out += [
        f"- Eingegangen: {manifest['eingegangen']}",
        f"- Vorgänger: {manifest['vorgaenger'] or '– (erste Fassung, Grundlage)'}",
        f"- Seiten: {manifest['seiten']} · Wörter: {manifest['woerter']} · Passagen: {manifest['passagen']}",
        "",
    ]
    if not manifest["vorgaenger"]:
        out += ["Erste Fassung. Alle Passagen haben ihre Kennung erhalten; es gibt nichts abzugleichen.", ""]
        return "\n".join(out)

    out += [
        "## Überblick",
        "",
        "| unverändert | verschoben | bearbeitet | neu | entfallen |",
        "|---|---|---|---|---|",
        f"| {count['unveraendert']} | {count['verschoben']} | {count['bearbeitet']} | {count['neu']} | {len(abgleich.entfallen)} |",
        "",
    ]
    changed = count["bearbeitet"] + count["neu"] + len(abgleich.entfallen)
    if ps and changed > len(ps) / 2:
        out += [
            "> **Achtung:** Mehr als die Hälfte der Passagen hat sich geändert. Entweder hat Bernd das Buch",
            "> grundlegend umgebaut, oder der PDF-Export hat sich verändert. Vor jeder Entscheidung prüfen.",
            "",
        ]

    out += ["## Auswirkung", ""]
    if not karten:
        out += ["Keine Karte und keine Szene betroffen.", ""]
    else:
        out += ["| Karte | betroffene Passagen |", "|---|---|"]
        out += [f"| `{k}` | {', '.join(f'`{p}`' for p in sorted(v))} |" for k, v in sorted(karten.items())]
        out += [""]
        if szenen:
            out += ["| Szene | über Karten |", "|---|---|"]
            out += [f"| `{s}` | {', '.join(f'`{k}`' for k in sorted(v))} |" for s, v in sorted(szenen.items())]
            out += [""]

    out += [
        "## Entscheidungen",
        "",
        "Pro Änderung: **ignorieren**, **Karte anpassen** oder **Szene überarbeiten**. Offen, bis eingetragen.",
        "",
    ]
    sections = [
        ("Bearbeitet", [p for p in ps if p.status == "bearbeitet"]),
        ("Neu", [p for p in ps if p.status == "neu"]),
    ]
    for title, items in sections:
        out += [f"### {title} ({len(items)})", ""]
        if not items:
            out += ["–", ""]
            continue
        out += ["| Kennung | S. | Text | Entscheidung |", "|---|---|---|---|"]
        for p in items:
            text = excerpt(p.text)
            if p.status == "bearbeitet":
                text = f"{text}<br>*vorher ({int(p.aehnlichkeit * 100)} %):* {excerpt(p.vorher)}"
            out.append(f"| `{p.id}` | {p.seite} | {text} | offen |")
        out += [""]
    out += [f"### Entfallen ({len(abgleich.entfallen)})", ""]
    if abgleich.entfallen:
        out += ["| Kennung | Text | Entscheidung |", "|---|---|---|"]
        out += [f"| `{p['id']}` | {excerpt(p['text'])} | offen |" for p in abgleich.entfallen]
    else:
        out += ["–"]
    out += [""]
    moved = [p for p in ps if p.status == "verschoben"]
    out += [f"### Verschoben ({len(moved)})", "", "Nur zur Kenntnis, keine Entscheidung nötig.", ""]
    if moved:
        out += [f"- `{p.id}` S. {p.seite}: {excerpt(p.text, 90)}" for p in moved]
        out += [""]
    return "\n".join(out)


# --------------------------------------------------------------------------
# Pipeline


def previous_version(datum: str) -> str | None:
    if not QUELLEN.is_dir():
        return None
    earlier = sorted(d.name for d in QUELLEN.iterdir() if d.is_dir() and d.name < datum)
    return earlier[-1] if earlier else None


def load_passages(datum: str) -> list[dict]:
    with (QUELLEN / datum / "passagen.jsonl").open() as f:
        return [json.loads(line) for line in f if line.strip()]


def known_checksums() -> dict[str, str]:
    sums = {}
    if QUELLEN.is_dir():
        for m in QUELLEN.glob("*/manifest.json"):
            sums[json.loads(m.read_text())["sha256"]] = m.parent.name
    return sums


def ingest(pdf: Path, datum: str | None = None) -> Path:
    sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if sha in known_checksums():
        sys.exit(f"Dieses PDF ist bereits eingepflegt als Fassung {known_checksums()[sha]}.")
    datum = datum or pdf_creation_date(pdf) or dt.date.today().isoformat()
    if (QUELLEN / datum).exists():
        sys.exit(f"Fassung {datum} existiert bereits. Anderes Datum mit --datum angeben.")

    pages = parse_bbox(run_pdftotext(pdf))
    passagen = segment(pages)
    vorgaenger = previous_version(datum)
    abgleich = match(passagen, load_passages(vorgaenger) if vorgaenger else [])

    betroffen = {p.id for p in abgleich.passagen if p.status == "bearbeitet"} | {p["id"] for p in abgleich.entfallen}
    karten, szenen = impact(betroffen, ZETTELKASTEN, ROMAN)

    manifest = {
        "fassung": datum,
        "eingegangen": dt.date.today().isoformat(),
        "vorgaenger": vorgaenger,
        "sha256": sha,
        "seiten": len(pages),
        "woerter": word_count(passagen),
        "passagen": len(passagen),
    }
    write_version(QUELLEN / datum, abgleich.passagen, manifest)
    BERICHTE.mkdir(parents=True, exist_ok=True)
    bericht = BERICHTE / f"{datum}.md"
    bericht.write_text(report(datum, manifest, abgleich, karten, szenen))
    return bericht


def main() -> None:
    ap = argparse.ArgumentParser(description="Neue Fassung von Bernds Manuskript einpflegen.")
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--datum", help="Fassungsdatum JJJJ-MM-TT (Standard: Erstellungsdatum des PDFs)")
    args = ap.parse_args()
    if not args.pdf.is_file():
        sys.exit(f"Datei nicht gefunden: {args.pdf}")
    bericht = ingest(args.pdf, args.datum)
    print(f"Bericht: {bericht.relative_to(REPO)}")


if __name__ == "__main__":
    main()
