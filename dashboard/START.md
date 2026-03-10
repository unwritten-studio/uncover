# Uncoverboard — Einrichtung

## Was du brauchst

- Einen GitHub-Account (einmalig anlegen auf [github.com](https://github.com))
- Die drei Dateien `uncoverboard.html`, `app.js` und `style.css` — alle in denselben Ordner legen
- Einen Access Token (einmalig erstellen, siehe unten)

---

## Schritt 1 — Access Token erstellen

Der Token erlaubt dem Dashboard, Änderungen direkt ins Buch zu speichern.

1. Auf [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new) einloggen
2. Folgende Einstellungen wählen:

| Feld | Wert |
|---|---|
| Token name | `Uncover Dashboard` |
| Expiration | 1 year |
| Resource owner | `unwritten-studio` |
| Repository access | Only select repositories → **uncover** |
| Permissions → Contents | **Read and write** |

3. Unten auf **Generate token** klicken
4. Den Token kopieren — er wird nur einmal angezeigt!

---

## Schritt 2 — Dashboard öffnen

Doppelklick auf `uncoverboard.html` — es öffnet sich im Browser.

---

## Schritt 3 — Token eingeben

Oben rechts auf **⚙ Token** klicken, den kopierten Token einfügen, speichern.

Das war's. Der Token wird im Browser gespeichert und muss nicht erneut eingegeben werden.

---

## Tipp — Als App ins Dock legen (Mac)

`uncoverboard.html` bei gedrückter **⌘-Taste** ins Dock ziehen. Danach öffnet ein Klick das Dashboard direkt.

---

## Kapitel bearbeiten

1. Kapitel in der linken Liste anklicken
2. Text bearbeiten
3. **Speichern** (oben rechts) oder **⌘S** — die Änderung landet sofort im Buch

---

Fragen? → [post@unwritten.studio](mailto:post@unwritten.studio)
