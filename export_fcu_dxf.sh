#!/bin/bash
# Export only F.Cu layer DXF suitable for xTool Laser F2 Ultra (mm, Edge.Cuts included)
# Usage: KICAD_CLI="kicad-cli" ./export_fcu_dxf.sh [path/to/file.kicad_pcb] [outdir]

set -euo pipefail

PCB_FILE=${1:-}
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

if [ -z "$PCB_FILE" ]; then
  pcs=( *.kicad_pcb )
  if [ ${#pcs[@]} -eq 1 ]; then
    PCB_FILE=${pcs[0]}
  else
    echo "Please specify the board file (found ${#pcs[@]} .kicad_pcb files)."
    echo "Usage: KICAD_CLI=... $0 path/to/file.kicad_pcb [outdir]"
    exit 2
  fi
fi

mkdir -p "$OUTDIR"

echo "Exporting F.Cu DXF (units: mm) -> $OUTDIR"
$KICAD_CLI pcb export dxf \
  --layers F.Cu \
  --common-layers Edge.Cuts \
  --output-units mm \
  --drill-shape-opt 1 \
  --mode-single \
  -o "$OUTDIR" \
  "$PCB_FILE"

echo "Export completed. Files in $OUTDIR:"
ls -1 "$OUTDIR" || true
