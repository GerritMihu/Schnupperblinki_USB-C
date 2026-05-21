#!/bin/bash
# Universal DXF export for a KiCad PCB project
# Usage: KICAD_CLI="kicad-cli" ./export_dxf.sh [path/to/file.kicad_pcb] [outdir]

set -euo pipefail

BOARD=${1:-}
OUTDIR=${2:-dxf}
KICAD_CLI=${KICAD_CLI:-}

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

echo "DXF export"
echo "  board: $BOARD"
echo "  outdir: $OUTDIR"
echo "  kicad-cli: $KICAD_CLI"

$KICAD_CLI pcb export dxf \
  --layers F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --common-layers Edge.Cuts \
  --output-units mm \
  --drill-shape-opt 1 \
  --mode-multi \
  -o "$OUTDIR" \
  "$BOARD"

echo "\n✓ DXF export completed"
ls -1 "$OUTDIR" || true
