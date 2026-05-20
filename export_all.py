#!/usr/bin/env python3
"""
Combined DXF and 3D PNG export for KiCad PCB
Runs the DXF export (per-layer) and then 3D renders into pic/.
"""

import os
import subprocess
import sys

# Configuration (matches existing scripts)
KICAD_CLIPATH = "flatpak run --command=kicad-cli org.kicad.KiCad"
PCB_FILE = "Blinki mit USB-C.kicad_pcb"
OUTPUT_DIR_DXF = "dxf"
OUTPUT_DIR_PIC = "pic"

# DXF layers and settings
LAYERS = [
    "F.Cu",
    "B.Cu",
    "F.SilkS",
    "B.SilkS",
    "F.Mask",
    "B.Mask",
    "Edge.Cuts",
]
DXF_SETTINGS = [
    "--output-units", "mm",
    "--drill-shape-opt", "1",
    "--common-layers", "Edge.Cuts",
    "--mode-multi",
]

# 3D render settings
RENDER_SETTINGS = {
    "top": {"side": "top", "rotate": "", "filename": "3d_top.png"},
    "bottom": {"side": "bottom", "rotate": "", "filename": "3d_bottom.png"},
    "isometric": {"side": "top", "rotate": "-45,0,45", "filename": "3d_isometric.png"},
}


def run_command(cmd_list):
    print(f"Running: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    if result.stdout:
        print(result.stdout)
    return True


def export_dxf():
    if not os.path.exists(OUTPUT_DIR_DXF):
        os.makedirs(OUTPUT_DIR_DXF)
        print(f"Created directory: {OUTPUT_DIR_DXF}")

    layers_str = ",".join(LAYERS)
    cmd_list = KICAD_CLIPATH.split() + [
        "pcb", "export", "dxf",
    ] + DXF_SETTINGS + [
        "--layers", layers_str,
        "-o", OUTPUT_DIR_DXF,
        PCB_FILE,
    ]

    print("=" * 60)
    print("DXF Export for KiCad PCB")
    print("=" * 60)
    print(f"PCB file: {PCB_FILE}")
    print(f"Output dir: {OUTPUT_DIR_DXF}")
    print(f"Layers: {layers_str}")
    print("=" * 60)

    return run_command(cmd_list)


def run_render(view_name, view_config):
    output_file = os.path.join(OUTPUT_DIR_PIC, view_config["filename"])
    cmd = KICAD_CLIPATH.split() + [
        "pcb", "render",
        "-o", output_file,
        "--width", "1600",
        "--height", "900",
        "--quality", "high",
    ]
    if view_config["side"]:
        cmd += ["--side", view_config["side"]]
    if view_config["rotate"]:
        cmd += ["--rotate", view_config["rotate"]]
    cmd.append(PCB_FILE)

    print(f"  Rendering {view_name} -> {output_file}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        return False
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        if lines:
            print(f"  {lines[-1]}")
    return True


def export_3d():
    if not os.path.exists(OUTPUT_DIR_PIC):
        os.makedirs(OUTPUT_DIR_PIC)
        print(f"Created directory: {OUTPUT_DIR_PIC}")

    print("=" * 60)
    print("3D PNG Export for KiCad PCB")
    print("=" * 60)
    print(f"PCB file: {PCB_FILE}")
    print(f"Output dir: {OUTPUT_DIR_PIC}")
    print("=" * 60)

    all_success = True
    for view_name, config in RENDER_SETTINGS.items():
        if not run_render(view_name, config):
            all_success = False
        print()
    return all_success


def main():
    ok_dxf = export_dxf()
    ok_3d = export_3d()

    if ok_dxf and ok_3d:
        print('\n✓ All exports completed successfully!')
        # list results
        print('\nExported DXF files:')
        if os.path.exists(OUTPUT_DIR_DXF):
            for f in sorted(os.listdir(OUTPUT_DIR_DXF)):
                print(f"  - {OUTPUT_DIR_DXF}/{f}")
        print('\nExported PNG files:')
        if os.path.exists(OUTPUT_DIR_PIC):
            for view_name, cfg in RENDER_SETTINGS.items():
                p = os.path.join(OUTPUT_DIR_PIC, cfg['filename'])
                size = os.path.getsize(p) if os.path.exists(p) else 0
                print(f"  - {p} ({size:,} bytes)")
        return 0
    else:
        print('\n✗ Some exports failed!')
        return 1


if __name__ == '__main__':
    sys.exit(main())
