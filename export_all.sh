#!/bin/bash
# Combined DXF and 3D PNG export for KiCad PCB
# Runs export_dxf and 3D renders in sequence

set -e

PCB_FILE="Blinki mit USB-C.kicad_pcb"
OUTPUT_DIR_DXF="dxf"
OUTPUT_DIR_PIC="pic"

mkdir -p "$OUTPUT_DIR_DXF"
mkdir -p "$OUTPUT_DIR_PIC"

echo "============================================================"
echo "Combined Export for KiCad PCB"
echo "============================================================"
echo "PCB file: $PCB_FILE"
echo "Output DXF dir: $OUTPUT_DIR_DXF"
echo "Output PNG dir: $OUTPUT_DIR_PIC"
echo "============================================================"

# DXF export
echo "Running DXF export..."
flatpak run --command=kicad-cli org.kicad.KiCad pcb export dxf \
    --layers F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
    --common-layers Edge.Cuts \
    --output-units mm \
    --drill-shape-opt 1 \
    --mode-multi \
    -o "$OUTPUT_DIR_DXF" \
    "$PCB_FILE"

echo ""
echo "✓ DXF export completed"
echo "Exported files:"
ls -1 "$OUTPUT_DIR_DXF" || true

echo ""
# 3D renders
echo "Rendering 3D top view..."
flatpak run --command=kicad-cli org.kicad.KiCad pcb render \
    -o "$OUTPUT_DIR_PIC/3d_top.png" \
    --width 1600 \
    --height 900 \
    --side top \
    --quality high \
    "$PCB_FILE"
echo "  -> $OUTPUT_DIR_PIC/3d_top.png"
echo ""

echo "Rendering 3D bottom view..."
flatpak run --command=kicad-cli org.kicad.KiCad pcb render \
    -o "$OUTPUT_DIR_PIC/3d_bottom.png" \
    --width 1600 \
    --height 900 \
    --side bottom \
    --quality high \
    "$PCB_FILE"
echo "  -> $OUTPUT_DIR_PIC/3d_bottom.png"
echo ""

echo "Rendering 3D isometric view..."
flatpak run --command=kicad-cli org.kicad.KiCad pcb render \
    -o "$OUTPUT_DIR_PIC/3d_isometric.png" \
    --width 1600 \
    --height 900 \
    --rotate "45,0,45" \
    --quality high \
    "$PCB_FILE"
echo "  -> $OUTPUT_DIR_PIC/3d_isometric.png"
echo ""

echo "✓ All 3D renders completed"
echo "Exported PNG files:"
ls -lh "$OUTPUT_DIR_PIC" || true

echo ""
echo "Updating README.md with preview links..."
if [ -f "./update_readme.py" ]; then
    python3 ./update_readme.py
else
    echo "Warning: update_readme.py not found"
fi

echo "============================================================"
echo "Export process finished"
echo "============================================================"
