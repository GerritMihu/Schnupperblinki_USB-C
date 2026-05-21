#!/usr/bin/env python3
"""
Universal combined exporter for KiCad PCB projects.
- Uses export_dxf.py and export_3d_png.py if present, or runs inline defaults.
- Accepts --board and forwards options to sub-commands.
"""

import argparse
import os
import subprocess
import sys


def find_script(name):
    if os.path.exists(name):
        return os.path.abspath(name)
    return None


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


def run_subcommand(cmd):
    print('Running:', ' '.join(cmd))
    r = subprocess.run(cmd)
    return r.returncode == 0


def main():
    p = argparse.ArgumentParser(description='Run combined DXF and 3D exports (universal).')
    p.add_argument('--board', '-b', help='Path to .kicad_pcb file (default: autodetect single file in CWD)')
    p.add_argument('--kicad-cli', help='kicad-cli command or prefix (passed to sub-scripts)')
    p.add_argument('--outdir-dxf', default='dxf')
    p.add_argument('--outdir-pic', default='pic')
    args, extra = p.parse_known_args()

    board = find_board(args.board)

    # Prefer local Python scripts if they exist
    export_dxf_py = find_script('export_dxf.py')
    export_3d_py = find_script('export_3d_png.py')

    ok_dxf = True
    ok_3d = True

    base_cmd = [sys.executable]

    if export_dxf_py:
        cmd = base_cmd + [export_dxf_py, '--board', board, '--outdir', args.outdir_dxf]
        if args.kicad_cli:
            cmd += ['--kicad-cli', args.kicad_cli]
        ok_dxf = run_subcommand(cmd)
    else:
        print('export_dxf.py not found; skipping DXF export')

    if export_3d_py:
        cmd = base_cmd + [export_3d_py, '--board', board, '--outdir', args.outdir_pic]
        if args.kicad_cli:
            cmd += ['--kicad-cli', args.kicad_cli]
        ok_3d = run_subcommand(cmd)
    else:
        print('export_3d_png.py not found; skipping 3D renders')

    # Documentation exports (PDF/SVG) into Dok/
    export_docs_py = find_script('export_docs.py')
    ok_docs = True
    if export_docs_py:
        cmd = base_cmd + [export_docs_py, '--board', board]
        if args.kicad_cli:
            cmd += ['--kicad-cli', args.kicad_cli]
        ok_docs = run_subcommand(cmd)
    else:
        print('export_docs.py not found; skipping documentation exports')

    if ok_dxf and ok_3d and ok_docs:
        print('\n✓ All exports completed successfully!')
        return 0
    print('\n✗ Some exports failed!')
    return 1


if __name__ == '__main__':
    sys.exit(main())
