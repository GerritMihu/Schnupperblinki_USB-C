#!/usr/bin/env python3
"""
Universal DXF export for a KiCad PCB project.
- Auto-detects a single .kicad_pcb file in CWD or accepts --board
- Uses KICAD_CLI env var or system kicad-cli, falls back to Flatpak
- Preserves original DXF flags by default; allows overrides
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys

DEFAULT_LAYERS = [
    "F.Cu",
    "B.Cu",
    "F.SilkS",
    "B.SilkS",
    "F.Mask",
    "B.Mask",
    "Edge.Cuts",
]

DEFAULT_DXF_FLAGS = [
    "--output-units", "mm",
    "--drill-shape-opt", "1",
    "--common-layers", "Edge.Cuts",
    "--mode-multi",
]


def find_board(provided):
    if provided:
        return provided
    candidates = [f for f in os.listdir('.') if f.endswith('.kicad_pcb')]
    if not candidates:
        print('No .kicad_pcb file found in current directory. Provide --board <file>.')
        sys.exit(2)
    if len(candidates) > 1:
        print('Multiple .kicad_pcb files found. Pass the desired one with --board:')
        for c in candidates:
            print('  -', c)
        sys.exit(2)
    return candidates[0]


def find_kicad_cli(provided):
    # Order: provided arg -> env KICAD_CLI -> system kicad-cli -> flatpak fallback
    if provided:
        return provided
    env = os.environ.get('KICAD_CLI') or os.environ.get('KICAD_CLIPATH')
    if env:
        return env
    if shutil.which('kicad-cli'):
        return 'kicad-cli'
    return 'flatpak run --command=kicad-cli org.kicad.KiCad'


def run(cmd):
    print('Running:', ' '.join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print('Error:', r.stderr.strip())
        return False
    if r.stdout:
        print(r.stdout.strip())
    return True


def build_dxf_cmd(kicad_cli, layers, flags, outdir, board):
    parts = shlex.split(kicad_cli)
    cmd = parts + ['pcb', 'export', 'dxf'] + flags + ['--layers', ','.join(layers), '-o', outdir, board]
    return cmd


def main():
    p = argparse.ArgumentParser(description='Export DXF files from a KiCad PCB (universal).')
    p.add_argument('--board', '-b', help='Path to .kicad_pcb file (default: autodetect single file in CWD)')
    p.add_argument('--kicad-cli', help='kicad-cli command or prefix (env KICAD_CLI overrides)')
    p.add_argument('--outdir', '-o', default='dxf', help='Output directory (default: dxf)')
    p.add_argument('--layers', help='Comma-separated list of layers to export')
    p.add_argument('--no-default-flags', action='store_true', help='Do not include default DXF flags')
    args = p.parse_args()

    board = find_board(args.board)
    kicad_cli = find_kicad_cli(args.kicad_cli)
    outdir = args.outdir
    if args.layers:
        layers = [s.strip() for s in args.layers.split(',') if s.strip()]
    else:
        layers = DEFAULT_LAYERS
    flags = [] if args.no_default_flags else DEFAULT_DXF_FLAGS

    os.makedirs(outdir, exist_ok=True)

    cmd = build_dxf_cmd(kicad_cli, layers, flags, outdir, board)

    print('\nDXF export')
    print('  board:', board)
    print('  outdir:', outdir)
    print('  kicad-cli:', kicad_cli)
    print('  layers:', ','.join(layers))

    ok = run(cmd)
    if ok:
        print('\nExported files:')
        for f in sorted(os.listdir(outdir)):
            print(' -', os.path.join(outdir, f))
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
