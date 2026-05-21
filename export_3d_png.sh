#!/bin/bash
# Universal 3D PNG export for a KiCad PCB project
# Usage: KICAD_CLI="kicad-cli" ./export_3d_png.sh [path/to/file.kicad_pcb] [outdir]

set -euo pipefail

BOARD=${1:-}
OUTDIR=${2:-pic}
KICAD_CLI=${KICAD_CLI:-}
WIDTH=${WIDTH:-1600}
HEIGHT=${HEIGHT:-900}
QUALITY=${QUALITY:-high}

# Discover kicad-cli if not provided
if [ -z "$KICAD_CLI" ]; then
  if command -v kicad-cli >/dev/null 2>&1; then
    KICAD_CLI=kicad-cli
  else
    KICAD_CLI="flatpak run --command=kicad-cli org.kicad.KiCad"
  fi
fi

if [ -z "$BOARD" ]; then
  pcs=( *.kicad_pcb )
  if [ ${#pcs[@]} -eq 1 ]; then
    BOARD=${pcs[0]}
  else
    echo "Please specify the board file (found ${#pcs[@]} .kicad_pcb files)."
    echo "Usage: KICAD_CLI=... $0 path/to/file.kicad_pcb [outdir]"
    exit 2
  fi
fi

mkdir -p "$OUTDIR"

echo "3D PNG renders"
echo "  board: $BOARD"
echo "  outdir: $OUTDIR"
echo "  kicad-cli: $KICAD_CLI"

echo "Rendering top view..."
$KICAD_CLI pcb render -o "$OUTDIR/3d_top.png" --width $WIDTH --height $HEIGHT --side top --quality $QUALITY "$BOARD"
echo "  -> $OUTDIR/3d_top.png"
echo ""

echo "Rendering bottom view..."
$KICAD_CLI pcb render -o "$OUTDIR/3d_bottom.png" --width $WIDTH --height $HEIGHT --side bottom --quality $QUALITY "$BOARD"
echo "  -> $OUTDIR/3d_bottom.png"
echo ""

echo "Rendering isometric view..."
$KICAD_CLI pcb render -o "$OUTDIR/3d_isometric.png" --width $WIDTH --height $HEIGHT --rotate "-45,0,45" --quality $QUALITY "$BOARD"
echo "  -> $OUTDIR/3d_isometric.png"
echo ""

echo "✓ All 3D renders completed"
ls -lh "$OUTDIR"/3d_*.png || true
