"""Tests for einpflegen.py. Run: python3 -m unittest discover werkzeuge"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import einpflegen as e  # noqa: E402


def bbox(pages: list[list[list[str]]]) -> str:
    """Build minimal `pdftotext -bbox-layout` output from pages → blocks → lines."""
    out = ["<doc>"]
    for blocks in pages:
        out.append('<page width="595" height="842"><flow>')
        for lines in blocks:
            out.append("<block>")
            for line in lines:
                words = "".join(f"<word>{w}</word>" for w in line.split())
                out.append(f"<line>{words}</line>")
            out.append("</block>")
        out.append("</flow></page>")
    out.append("</doc>")
    return "\n".join(out)


A = "Sie steht vor der Tür. Die Hand auf dem Griff, das Gewicht nach vorn verlagert."
B = "Nürnberg ist keine Tech-Metropole vom Schlage San Franciscos oder Shenzhens."
C = "Zweitausendzweiundzwanzig ist diese Welt erschöpft. Die Lockdowns haben Lesungen ausgelöscht."
D = "Die Geburtsstunde von Unwritten schlug auf einem KI-Meetup namens Betreute Intelligenz."
E = "Frank stellte die entscheidende Frage, was der Buchhandel damit anfangen soll."


def passages(*texts: str) -> list[e.Passage]:
    return [e.Passage(nr=i + 1, seite=1, art="absatz", text=t) for i, t in enumerate(texts)]


def baseline(*texts: str) -> list[dict]:
    return [p.as_json() for p in e.match(passages(*texts), []).passagen]


class Extract(unittest.TestCase):
    def test_blocks_lines_words(self):
        pages = e.parse_bbox(bbox([[["Kapitel eins"], ["Erste Zeile", "zweite Zeile."]]]))
        self.assertEqual(pages, [[["Kapitel eins"], ["Erste Zeile", "zweite Zeile."]]])

    def test_entities_unescaped(self):
        pages = e.parse_bbox("<page><block><line><word>&quot;Hallo&quot;</word><word>&amp;</word></line></block></page>")
        self.assertEqual(pages[0][0], ['"Hallo" &'])


class Segment(unittest.TestCase):
    def test_page_numbers_dropped(self):
        ps = e.segment([[["Ein Satz."], ["7"]]])
        self.assertEqual([p.text for p in ps], ["Ein Satz."])

    def test_toc_page_dropped_even_when_fragmented(self):
        toc = [["Inhaltsverzeichnis"], ["Vorwort – Am Anfang"], ["... 5"], ["1. Prolog: Die Schwelle …6"],
               ["2. Das begehbare Buch"], ["...7"], ["3. Verlag und Algorithmus ... 8"]]
        ps = e.segment([toc, [["Vorwort"], ["Der Text beginnt."]]])
        self.assertEqual([p.text for p in ps], ["Vorwort", "Der Text beginnt."])

    def test_body_page_with_numbers_is_not_toc(self):
        body = [["Wir schreiben das Jahr 2022."], ["Drei Monate später waren es 12"], ["Kapitel"], ["Ende."], ["Gut."]]
        self.assertFalse(e.is_toc_page(body))

    def test_heading_vs_paragraph(self):
        ps = e.segment([[["Verlag und Algorithmus"], ["Wann wussten wir, dass es gut wird?"]]])
        self.assertEqual([p.art for p in ps], ["ueberschrift", "absatz"])

    def test_dialogue_is_not_heading(self):
        for line in ["„Interessant. Und dann?“", "Stefan lacht. „Großartige Idee. Vielleicht beide.“"]:
            self.assertFalse(e.is_heading([line]), line)

    def test_paragraph_across_page_break_is_joined(self):
        ps = e.segment([[["Ein Absatz, der auf dieser Seite", "nicht endet und"], ["8"]], [["weitergeht auf der nächsten."]]])
        self.assertEqual(len(ps), 1)
        self.assertEqual(ps[0].text, "Ein Absatz, der auf dieser Seite nicht endet und weitergeht auf der nächsten.")
        self.assertEqual(ps[0].seite, 1)

    def test_new_paragraph_on_next_page_stays_separate(self):
        ps = e.segment([[["Ein Absatz endet hier."]], [["Neuer Absatz beginnt."]]])
        self.assertEqual(len(ps), 2)

    def test_hyphenation(self):
        self.assertEqual(e.join_lines(["Daten-", "schutz ist wichtig."]), "Datenschutz ist wichtig.")
        self.assertEqual(e.join_lines(["Nord-", "und Südseite."]), "Nord- und Südseite.")
        self.assertEqual(e.join_lines(["KI-", "Meetup"]), "KI- Meetup")  # capital follows: not a soft hyphen


class Match(unittest.TestCase):
    def status(self, abgleich):
        return [(p.text, p.status) for p in abgleich.passagen]

    def test_first_version_all_new_with_ids(self):
        ab = e.match(passages(A, B, C), [])
        self.assertTrue(all(p.status == "neu" and p.id.startswith("p") for p in ab.passagen))
        self.assertEqual(len({p.id for p in ab.passagen}), 3)

    def test_ids_deterministic(self):
        self.assertEqual(baseline(A, B), baseline(A, B))

    def test_unchanged_keeps_ids(self):
        alt = baseline(A, B, C)
        ab = e.match(passages(A, B, C), alt)
        self.assertEqual([p.id for p in ab.passagen], [p["id"] for p in alt])
        self.assertTrue(all(p.status == "unveraendert" for p in ab.passagen))

    def test_typography_changes_count_as_unchanged(self):
        alt = baseline("„Hallo“, sagte sie – leise...")
        ab = e.match(passages('"Hallo", sagte sie - leise…'), alt)
        self.assertEqual(ab.passagen[0].status, "unveraendert")

    def test_moved(self):
        alt = baseline(A, B, C, D, E)
        ab = e.match(passages(A, C, D, E, B), alt)
        ids = {p["text"]: p["id"] for p in alt}
        self.assertEqual({p.text: p.id for p in ab.passagen}, ids)
        moved = [p.text for p in ab.passagen if p.status == "verschoben"]
        self.assertEqual(moved, [B])

    def test_edited_keeps_id(self):
        alt = baseline(A, B, C)
        edited = B.replace("keine Tech-Metropole", "wahrlich keine Tech-Metropole")
        ab = e.match(passages(A, edited, C), alt)
        p = ab.passagen[1]
        self.assertEqual((p.status, p.id, p.vorher), ("bearbeitet", alt[1]["id"], B))
        self.assertLess(p.aehnlichkeit, 1)

    def test_new_and_removed(self):
        alt = baseline(A, B, C)
        ab = e.match(passages(A, C, D), alt)
        self.assertEqual(self.status(ab), [(A, "unveraendert"), (C, "unveraendert"), (D, "neu")])
        self.assertEqual([p["text"] for p in ab.entfallen], [B])
        self.assertNotIn(ab.passagen[2].id, {p["id"] for p in alt})

    def test_unrelated_rewrite_is_new_not_edited(self):
        alt = baseline(A)
        ab = e.match(passages(E), alt)
        self.assertEqual(ab.passagen[0].status, "neu")
        self.assertEqual(len(ab.entfallen), 1)

    def test_split_paragraph_keeps_id_on_one_half(self):
        long = A + " " + B
        alt = baseline(long)
        ab = e.match(passages(A, B), alt)
        statuses = sorted(p.status for p in ab.passagen)
        self.assertEqual(statuses, ["bearbeitet", "neu"])
        self.assertEqual(ab.entfallen, [])

    def test_duplicate_text_gets_distinct_ids(self):
        ab = e.match(passages(A, A), [])
        self.assertNotEqual(ab.passagen[0].id, ab.passagen[1].id)
        again = e.match(passages(A, A), [p.as_json() for p in ab.passagen])
        self.assertEqual([p.id for p in again.passagen], [p.id for p in ab.passagen])

    def test_removed_id_never_reused(self):
        alt = baseline(A, B)
        ab = e.match(passages(A), alt)  # B removed
        ab2 = e.match(passages(A, B), [p.as_json() for p in ab.passagen])  # B returns, unknown to ab
        self.assertNotIn(ab2.passagen[1].id, {p.id for p in ab.passagen})


class Impact(unittest.TestCase):
    def test_cards_and_scenes(self):
        with tempfile.TemporaryDirectory() as tmp:
            zk, roman = Path(tmp, "zettelkasten"), Path(tmp, "roman")
            zk.mkdir(), roman.mkdir()
            (zk / "anna-erster-kontakt.md").write_text("---\nquellen: [pabc123, pdef456]\n---\nAnna tritt ein.")
            (zk / "nuernberg.md").write_text("---\nquellen: [p999999]\n---\n")
            (roman / "01-schwelle.md").write_text("---\nkarten: [anna-erster-kontakt]\n---\n")
            karten, szenen = e.impact({"pabc123"}, zk, roman)
            self.assertEqual(karten, {"anna-erster-kontakt": {"pabc123"}})
            self.assertEqual(szenen, {"01-schwelle.md": {"anna-erster-kontakt"}})

    def test_no_cards_yet(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(e.impact({"pabc123"}, Path(tmp, "x"), Path(tmp, "y")), ({}, {}))


class Report(unittest.TestCase):
    def manifest(self, vorgaenger):
        return {"eingegangen": "2026-11-10", "vorgaenger": vorgaenger, "seiten": 1, "woerter": 10, "passagen": 3}

    def test_first_version(self):
        text = e.report("2026-10-28", self.manifest(None), e.match(passages(A), []), {}, {})
        self.assertIn("Erste Fassung", text)

    def test_change_report_lists_decisions(self):
        alt = baseline(A, B, C)
        ab = e.match(passages(A, B.replace("keine", "wahrlich keine"), D), alt)
        text = e.report("2026-11-10", self.manifest("2026-10-28"), ab, {}, {})
        self.assertIn("| 1 | 0 | 1 | 1 | 1 |", text)
        self.assertIn("vorher (", text)
        self.assertEqual(text.count("| offen |"), 3)  # edited, new, removed

    def test_warning_on_massive_change(self):
        ab = e.match(passages(D, E), baseline(A, B))
        text = e.report("2026-11-10", self.manifest("2026-10-28"), ab, {}, {})
        self.assertIn("Achtung", text)


if __name__ == "__main__":
    unittest.main()
