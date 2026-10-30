# Prozess

Die Methode folgt [Buchleim](https://buchleim.unwritten.studio) – zehn Schritte vom Schuhkarton voller Rohmaterial bis zum gebundenen Buch. Ihre Grundregel gilt durchgehend: **Nichts wird skaliert, bevor es geprüft ist.**

## Wer macht was

| Rolle | Macht | Macht nicht |
|---|---|---|
| **Claude** | Analyse über das ganze Buch, alle Struktur- und Stilentscheidungen, Aufträge schreiben, Ergebnisse prüfen, sämtlicher Code, sämtliche Arbeit am Repository | Textproduktion in der Masse |
| **Lokales Modell** | Textarbeit nach präzisem Auftrag: Passagen in Karten zerlegen, Szenen entwerfen, Überarbeitungsdurchgänge | Entscheidungen, Struktur, Werkzeuge, Zugriff aufs Repository |
| **Menschen** | Lesen und urteilen: Trägt es? Freigabe des Musterkapitels und jeder Stufe | – |

Das lokale Modell sieht immer nur einen Ausschnitt plus einen Auftrag. Es sieht nie das ganze Buch und muss das auch nicht: Den Überblick hält Claude, festgehalten in den Dateien unter `architektur/`. Jeder Auftrag an das lokale Modell wird in `auftraege/` abgelegt. So lässt sich jedes Stück Text auf die Anweisung zurückführen, die es erzeugt hat – und neu erzeugen, wenn sich der Auftrag ändert.

## Die zehn Schritte, angewendet auf Uncover

| # | Buchleim | In diesem Projekt | Wer |
|---|---|---|---|
| 01 | Quellen sichern | Jede Fassung von Bernds PDF als Text nach `quellen/`, nie bearbeitet | Claude (Skript) |
| 02 | Materiallage | Was steckt im Manuskript, was hat sich seit der letzten Fassung geändert | Claude (Skript) |
| 03 | Innere Ordnung freilegen | **Der Mixer:** jede Passage in Karten zerlegt (Szene, Person, Fakt, Zitat, Anekdote, Motiv), jede Karte verweist auf ihre Quellstelle | Lokales Modell, Claude prüft |
| 03 | | Karten zusammenführen: Wer taucht wo auf, welche Fäden und Motive ziehen sich durch | Claude |
| 04 | Stimme und Stil | Ein kompaktes Stilmodell für den Roman, mit ausdrücklichen Ausschlüssen (keine übernommenen Formulierungen, keine Stilkopie) | Claude |
| 05 | Zielmedium | Roman, gedrucktes Buch | entschieden |
| 06 | Strukturarchitektur | Die Erzählebenen, wie sie einander spiegeln, ein Szenenplan mit einem Auftrag pro Szene | Claude |
| 07 | Gestaltung | Typografie und Satz für das gedruckte Buch | später |
| 08 | Prototyp | **Ein Musterkapitel**, vom lokalen Modell nach seinen Aufträgen geschrieben, von Menschen gelesen. Go / No-Go für alles Weitere. | Lokales Modell, Menschen entscheiden |
| 09 | Kalibrieren | Stilmodell und Aufträge nachschärfen – nicht den Text von Hand flicken | Claude |
| 10 | Produzieren | Szene für Szene, danach Überarbeitungsdurchgänge nach Checklisten; Bau als PDF | Lokales Modell, Claude prüft |

## Arbeitsregeln

- **Quellen sind schreibgeschützt.** In `quellen/` wird nie etwas von Hand oder von einem Modell verändert.
- **Den Auftrag reparieren, nicht den Text.** Ist ein Ergebnis schwach, stimmt der Auftrag oder das Stilmodell nicht. Korrigiert wird dort, dann wird der Text neu erzeugt.
- **Nachvollziehbarkeit.** Szene → Karten → Quellstellen. Was sich nicht zurückverfolgen lässt, kommt nicht hinein.
- **Kleine, geprüfte Schritte.** Jede Stufe wird einzeln committet und in der `ROADMAP.md` festgehalten.
