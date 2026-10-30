# Uncover

**Worte werden Welten.** Ein Roman, gebaut aus dem Rohmaterial von [unwritten](https://unwritten.studio/).

---

## Worum es geht

Seit 2022 macht unwritten Geschichten begehbar – Bücher, die zurücksprechen, Gefährten aus Wissen, Gespräche mit Literatur. Bernd hält diesen Weg als Sachbuch-Manuskript fest: *Das begehbare Buch 2.0*.

Dieses Repository macht daraus etwas ganz anderes: **einen Roman.**

Keine bereinigte Ausgabe. Keine Überarbeitung Kapitel für Kapitel. Das Manuskript geht einmal durch den Mixer – zerlegt in seine kleinsten Teile: Szenen, Menschen, Fakten, Zitate, Anekdoten, Motive. Aus diesem Zettelkasten entsteht ein neues Buch, das seine Geschichte über mehrere Erzählebenen verwebt und wirklich spannend zu lesen ist.

Die Inspiration ist Wolf Haas' *Wackelkontakt* – nicht als Vorlage zum Kopieren, sondern als Beweis dafür, was möglich wird, wenn man sein Handwerk beherrscht und eine Geschichte über Ebenen hinweg verflechten kann. Siehe [`docs/ZIEL.md`](docs/ZIEL.md).

## Wie es funktioniert

Die Methode ist [Buchleim](https://buchleim.unwritten.studio): Erst verstehen, was da ist. Dann entscheiden, was daraus wird. Zehn Schritte, vom Sichern der Quellen bis zum gebundenen Buch.

Die Arbeit ist nach Art geteilt:

- **Denken, Struktur, Entscheidungen, Code, Repository** – Claude.
- **Textarbeit** (zerlegen, entwerfen, überarbeiten nach präzisen Aufträgen) – ein lokales Modell.
- **Urteil darüber, was trägt** – Menschen. Nichts wird skaliert, bevor ein Musterkapitel gelesen und freigegeben ist.

Details: [`docs/PROZESS.md`](docs/PROZESS.md).

## Eine bewegliche Quelle

Bernd schreibt weiter. Alle ein bis zwei Wochen kommt eine neue Fassung des Manuskripts als PDF. Das ist kein Problem, das gelöst werden muss, sondern die Arbeitsbedingung. Jede neue Fassung wird auf dieselbe Weise eingepflegt: extrahiert, mit der vorigen verglichen – und nur was sich tatsächlich geändert hat, fließt in den Zettelkasten und, wo es zählt, in den Roman.

Details: [`docs/EINPFLEGEN.md`](docs/EINPFLEGEN.md).

## Stand

Neuanfang am 30.10.2026. Alles Frühere – der offene Sachbuch-Entwurf und das Bearbeitungs-Dashboard – wurde entfernt und bleibt in der Git-Historie bis Commit `2663c97` erhalten.

Was erledigt ist und was als Nächstes kommt: [`ROADMAP.md`](ROADMAP.md).

## Aufbau (geplant)

```
quellen/        Bernds Fassungen als extrahierter Text, nie bearbeitet
zettelkasten/   die Karten: das Manuskript in seinen Teilen
architektur/    Stilmodell, Erzählebenen, Szenenplan
auftraege/      die genauen Aufträge an das lokale Modell
roman/          der Roman selbst
werkzeuge/      Skripte für Einpflegen und Bauen
docs/           Ziel, Prozess, Einpflegen
```

## Team

[unwritten](https://unwritten.studio/) – Worte werden Welten. Kontakt: post@unwritten.studio
