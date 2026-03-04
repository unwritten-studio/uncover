#!/bin/bash

# Uncover Buch Build Script
# Generiert PDF im beautiful Unwritten Design

set -e  # Exit bei Fehler

BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   Uncover Buch Builder${NC}"
echo -e "${BLUE}   Worte werden Welten${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Prüfe ob Pandoc installiert ist
if ! command -v pandoc &> /dev/null; then
    echo "❌ Pandoc ist nicht installiert!"
    echo "   Installiere mit: brew install pandoc"
    exit 1
fi

# Erstelle build Verzeichnis
mkdir -p build

# Wenn ein spezifisches Kapitel angegeben wurde
if [ $# -eq 1 ]; then
    CHAPTER=$1
    OUTPUT="build/$(basename $CHAPTER .md).pdf"

    echo -e "📖 Baue einzelnes Kapitel: ${GREEN}$(basename $CHAPTER)${NC}"
    echo ""

    pandoc "$CHAPTER" \
        -o "$OUTPUT" \
        --pdf-engine=xelatex \
        --metadata-file=metadata.yaml \
        -V geometry:margin=25mm

    echo ""
    echo -e "✅ Kapitel erstellt: ${GREEN}$OUTPUT${NC}"

else
    # Baue vollständiges Buch
    echo -e "📚 Baue vollständiges Buch..."
    echo ""

    # Prüfe ob Kapitel vorhanden sind
    if [ ! "$(ls -A chapters/*.md 2>/dev/null)" ]; then
        echo "❌ Keine Kapitel gefunden in chapters/"
        exit 1
    fi

    # Kombiniere alle Kapitel in richtiger Reihenfolge
    pandoc chapters/*.md \
        -o build/uncover-buch.pdf \
        --pdf-engine=xelatex \
        --metadata-file=metadata.yaml \
        --toc \
        --toc-depth=2 \
        -V toc-title:"Inhaltsverzeichnis" \
        --number-sections

    echo ""
    echo -e "✅ Buch erfolgreich erstellt!"
    echo -e "   📄 ${GREEN}build/uncover-buch.pdf${NC}"

    # Zeige Dateigröße
    SIZE=$(du -h build/uncover-buch.pdf | cut -f1)
    echo -e "   📊 Größe: ${SIZE}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
