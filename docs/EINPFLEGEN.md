# Neue Fassungen einpflegen

## Die Lage

Bernd liefert alle ein bis zwei Wochen eine neue Fassung seines Manuskripts als PDF. Er schreibt in seinem eigenen Programm und wird das weiter tun; die Arbeit in diesem Repository gehört nicht zu seinem Prozess und soll es auch nicht werden.

Also passt sich das Repository an ihn an, nicht umgekehrt. Eine neue Fassung aufzunehmen muss Routine sein: ein Befehl, ein lesbarer Bericht, eine überschaubare Zahl von Entscheidungen.

## Was sich automatisieren lässt – und was nicht

**Rein mechanisch (ohne Modell):** Text aus dem PDF holen, aufräumen, in Passagen teilen, erkennen, welche Passagen unverändert, verschoben, bearbeitet, neu oder entfallen sind, und auflisten, welche Karten und Szenen davon betroffen sind.

**Braucht Urteil:** ob eine Änderung für den Roman zählt. Ein korrigierter Tippfehler nicht. Eine neue Anekdote vielleicht schon. Diese Entscheidung fällt pro Änderung – aber nur für die Änderungen, nie wieder für das ganze Buch.

Der Aufwand einer neuen Fassung richtet sich deshalb danach, *wie viel Bernd geändert hat*, nicht nach dem Umfang des Buchs.

## Aufruf

```bash
python3 werkzeuge/einpflegen.py PFAD/ZU/BERNDS.pdf
```

Das Fassungsdatum wird aus dem Erstellungsdatum des PDFs gelesen; abweichend mit `--datum JJJJ-MM-TT`. Ein PDF, das schon eingepflegt ist (gleiche Prüfsumme), wird abgewiesen. Danach den Bericht unter `quellen/berichte/` lesen, Entscheidungen eintragen, alles als Pull Request einreichen.

Voraussetzung: Python 3.10+ und Poppler (`pdftotext`, `pdfinfo`; auf dem Mac `brew install poppler`). Sonst keine Abhängigkeiten.

Tests: `python3 -m unittest discover werkzeuge`

## Ablauf

```
neues PDF
  │
  ▼
1. extrahieren   Text aus dem PDF, Seitenballast entfernt
                 (Seitenzahlen, Kolumnentitel, Silbentrennung)
  │
  ▼
2. teilen        in Passagen zerlegen, jede mit stabiler Kennung
  │
  ▼
3. abgleichen    mit der vorigen Fassung vergleichen:
                 identisch          → gleiche Kennung
                 leicht bearbeitet  → gleiche Kennung, markiert „bearbeitet“
                 verschoben         → gleiche Kennung, neue Position
                 ohne Entsprechung  → neue Kennung, markiert „neu“
                 verschwunden       → markiert „entfallen“
  │
  ▼
4. auswirkung    bearbeitete/entfallene Passagen → Karten, die sie zitieren
                 → Szenen, die diese Karten verwenden
  │
  ▼
5. bericht       ein Markdown-Bericht pro Fassung:
                 was sich geändert hat, was es berührt, was entschieden werden muss
```

Die Kennungen überstehen Umstellungen und leichte Bearbeitung, weil Passagen über inhaltliche Ähnlichkeit zugeordnet werden, nicht über ihre Position. Das ist wichtig: Bernd stellt regelmäßig um und benennt Kapitel neu.

### Einzelheiten

- **Passagen** sind die Textblöcke des PDF-Layouts – in Bernds Export entsprechen sie weitgehend den Absätzen. Einzeilige Blöcke ohne Satzzeichen gelten als Überschrift.
- **Entfernt** werden Seitenzahlen und das Inhaltsverzeichnis (erkannt an Füllpunkten vor Seitenzahlen). Sonst würde jede neue Seitenaufteilung als Änderung erscheinen.
- **Seitenumbrüche:** Endet eine Seite mitten im Satz und beginnt die nächste klein, werden beide Teile zu einer Passage verbunden.
- **Vergleich:** Typografie (Anführungszeichen, Gedankenstriche, Auslassungspunkte, Leerraum) zählt nicht als Änderung. Ähnlichkeit wird auf Wortebene gemessen; ab 60 % gilt eine Passage als „bearbeitet“, darunter als neu.
- **Kennungen** werden aus dem Text der ersten Fassung abgeleitet (`p` + Prüfsummenanfang) und danach nur noch vererbt. Eine entfallene Kennung wird nie wieder vergeben.

### Gemessen

Simulation einer nächsten Fassung auf Basis des echten Manuskripts (824 Passagen):

| Änderung | erkannt |
|---|---|
| ein Kapitel (40 Passagen) ans Ende verschoben | 40 von 40 als verschoben, Kennungen erhalten |
| 30 Passagen bearbeitet | 30 von 30 |
| 15 gelöscht, 15 neu eingefügt | alle |
| 3 Passagen in zwei geteilt | 3 von 3 (eine Hälfte „bearbeitet“, die andere „neu“) |
| unberührte Passagen fälschlich markiert | 0 |

Belastungsprobe: Die Hälfte aller Passagen wird umgeschrieben. Bis etwa 40 % ausgetauschter Wörter pro Passage bleibt die Zuordnung erhalten; darüber wird sie als „neu“ plus „entfallen“ geführt – was inhaltlich dann auch stimmt. Laufzeit auch in diesem Fall unter drei Sekunden.

### Wie Karten und Szenen auf Quellen verweisen

Damit Schritt 4 (Auswirkung) greift, nennt jede Karte in `zettelkasten/` die Kennungen der Passagen, aus denen sie stammt, und jede Szene in `roman/` die Karten (Dateiname ohne `.md`), die sie verwendet:

```markdown
---
quellen: [p3f9a1c, p08bd42]
---
```

```markdown
---
karten: [anna-erster-kontakt, nuernberg-2022]
---
```

## Wo was liegt

```
quellen/bernd/2026-10-28/
  manuskript.md      extrahierter, bereinigter Text
  passagen.jsonl     eine Passage pro Zeile, mit stabiler Kennung
  manifest.json      Datum, Prüfsumme des PDFs, Seiten- und Wortzahl
quellen/berichte/
  2026-10-28.md      Änderungsbericht zu dieser Fassung
```

**Die PDFs selbst kommen nicht ins Repository.** Sie bleiben als Vorlage lokal bei uns. Im Repository steht nur der daraus extrahierte Text; die Prüfsumme im Manifest belegt, aus welchem PDF er stammt. Weil der Text in Git liegt, ist auch ein einfaches `git diff` zwischen zwei Fassungen lesbar.

## Nach dem Bericht

Für jede markierte Änderung eines von drei Ergebnissen, festgehalten im Bericht:

- **ignorieren** – keine Auswirkung auf den Roman
- **Karte anpassen** – die Karte wird korrigiert, Szenen, die sie verwenden, werden nachgeprüft
- **Szene überarbeiten** – ein neuer Auftrag geht an das lokale Modell

## Grenzen

- Sehr große Umbauten (das halbe Buch neu geschrieben) erzeugen einen langen Bericht. Der Ablauf funktioniert trotzdem, es sind nur mehr Entscheidungen.
- Die Textextraktion hängt vom PDF-Export ab. Ändert sich das Exportformat, muss der Extraktionsschritt eventuell angepasst werden. Das zeigt sich sofort im Bericht – an einer unplausibel hohen Zahl von Änderungen; ab mehr als der Hälfte geänderter Passagen warnt der Bericht ausdrücklich.
- Werden zwei Absätze zu einem zusammengelegt, behält der neue Absatz die Kennung des ähnlicheren; der andere erscheint als „entfallen“. Bei der Entscheidung im Bericht ist das leicht zu erkennen.
- Bilder werden nicht übernommen, nur Text.
