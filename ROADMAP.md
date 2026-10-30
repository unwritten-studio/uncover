# Roadmap

Was erledigt ist, was als Nächstes kommt. Wird mit jeder Stufe aktualisiert.

## Erledigt

- **30.10.2026 – Neuanfang.** Bisheriger Sachbuch-Entwurf und Bearbeitungs-Dashboard entfernt (in der Git-Historie erhalten bis `2663c97`). Ziel, Prozess und Einpflegen in `docs/` beschrieben.
- **30.10.2026 – Einpflegen** (Buchleim 01–02). `werkzeuge/einpflegen.py`: extrahieren, teilen, abgleichen, Auswirkung, Bericht. 26 Tests; Simulation einer nächsten Fassung auf echtem Material fehlerfrei erkannt (siehe [`docs/EINPFLEGEN.md`](docs/EINPFLEGEN.md)). Bernds Fassung vom 28.10.2026 als Grundlage eingepflegt: 824 Passagen, 51.026 Wörter.

## Wiedereinstieg

Stand 30.10.2026: Einpflegen fertig, Grundlage (Fassung 28.10.2026) liegt in `quellen/`. Noch keine Karte, kein Code für das lokale Modell.

**Nächster konkreter Schritt:** Mixer vorbereiten
1. Kartenformat festlegen (Frontmatter mit `quellen:` gemäß `docs/EINPFLEGEN.md`, Kartentypen Szene/Person/Fakt/Zitat/Anekdote/Motiv)
2. Kleines Skript, das einen Auftrag plus Passagen an das lokale Modell schickt und die Antwort als Karten ablegt (Aufträge in `auftraege/`)
3. Probelauf an etwa 10 Passagen, Ergebnis zur Durchsicht vorlegen – erst danach das ganze Manuskript

## Als Nächstes

1. **Der Mixer** (Buchleim 03)
   - Kartenformat und Aufträge für das lokale Modell
   - Probelauf an wenigen Passagen, prüfen, dann das ganze Manuskript
   - Karten zusammenführen: Menschen, Fäden, Motive
2. **Stilmodell** (Buchleim 04)
3. **Erzählarchitektur und Szenenplan** (Buchleim 06)
4. **Musterkapitel – Go / No-Go** (Buchleim 08)
5. Kalibrieren, dann produzieren (Buchleim 09–10)
6. **Lesesaal auf GitHub Pages** – sobald es etwas zu lesen gibt (ab Musterkapitel)

## Quellfassungen

| Fassung | Eingegangen | Status |
|---|---|---|
| 28.10.2026 | 30.10.2026 | Grundlage, eingepflegt ([Bericht](quellen/berichte/2026-10-28.md)) |
