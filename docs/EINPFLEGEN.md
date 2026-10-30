# Neue Fassungen einpflegen

## Die Lage

Bernd liefert alle ein bis zwei Wochen eine neue Fassung seines Manuskripts als PDF. Er schreibt in seinem eigenen Programm und wird das weiter tun; die Arbeit in diesem Repository gehört nicht zu seinem Prozess und soll es auch nicht werden.

Also passt sich das Repository an ihn an, nicht umgekehrt. Eine neue Fassung aufzunehmen muss Routine sein: ein Befehl, ein lesbarer Bericht, eine überschaubare Zahl von Entscheidungen.

## Was sich automatisieren lässt – und was nicht

**Rein mechanisch (ohne Modell):** Text aus dem PDF holen, aufräumen, in Passagen teilen, erkennen, welche Passagen unverändert, verschoben, bearbeitet, neu oder entfallen sind, und auflisten, welche Karten und Szenen davon betroffen sind.

**Braucht Urteil:** ob eine Änderung für den Roman zählt. Ein korrigierter Tippfehler nicht. Eine neue Anekdote vielleicht schon. Diese Entscheidung fällt pro Änderung – aber nur für die Änderungen, nie wieder für das ganze Buch.

Der Aufwand einer neuen Fassung richtet sich deshalb danach, *wie viel Bernd geändert hat*, nicht nach dem Umfang des Buchs.

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
- Die Textextraktion hängt vom PDF-Export ab. Ändert sich das Exportformat, muss der Extraktionsschritt eventuell angepasst werden. Das zeigt sich sofort im Bericht – an einer unplausibel hohen Zahl von Änderungen.
