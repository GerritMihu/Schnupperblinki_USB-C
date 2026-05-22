#!/usr/bin/env python3
"""
Universal 3D PNG export for a KiCad PCB project.
- Auto-detects a single .kicad_pcb file in CWD or accepts --board
- Uses KICAD_CLI env var or system kicad-cli, falls back to Flatpak
- Allows overriding output dir, size and which views to render
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys

DEFAULT_VIEWS = {
    'top': {'side': 'top', 'rotate': '', 'filename': '3d_top.png'},
    'bottom': {'side': 'bottom', 'rotate': '', 'filename': '3d_bottom.png'},
    'isometric': {'side': 'top', 'rotate': '45,0,45', 'filename': '3d_isometric.png'},
}


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


def build_render_cmd(kicad_cli, board, out_file, width, height, quality, side, rotate):
    parts = shlex.split(kicad_cli)
    cmd = parts + ['pcb', 'render', '-o', out_file, '--width', str(width), '--height', str(height), '--quality', quality]
    if side:
        cmd += ['--side', side]
    if rotate:
        cmd += ['--rotate', rotate]
    cmd.append(board)
    return cmd


def main():
    p = argparse.ArgumentParser(description='Render 3D PNGs from a KiCad PCB (universal).')
    p.add_argument('--board', '-b', help='Path to .kicad_pcb file (default: autodetect single file in CWD)')
    p.add_argument('--kicad-cli', help='kicad-cli command or prefix (env KICAD_CLI overrides)')
    p.add_argument('--outdir', '-o', default='pic', help='Output directory (default: pic)')
    p.add_argument('--views', help='Comma-separated list of views to render (default: top,bottom,isometric)')
    p.add_argument('--width', type=int, default=1600, help='Render width')
    p.add_argument('--height', type=int, default=900, help='Render height')
    p.add_argument('--quality', default='high', help='Render quality')
    args = p.parse_args()

    board = find_board(args.board)
    kicad_cli = find_kicad_cli(args.kicad_cli)
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    if args.views:
        wanted = [v.strip() for v in args.views.split(',') if v.strip()]
    else:
        wanted = list(DEFAULT_VIEWS.keys())

    print('\n3D render')
    print('  board:', board)
    print('  outdir:', outdir)
    print('  kicad-cli:', kicad_cli)
    print('  views:', ','.join(wanted))

    all_ok = True
    for v in wanted:
        cfg = DEFAULT_VIEWS.get(v)
        if not cfg:
            print('Skipping unknown view:', v)
            all_ok = False
            continue
        out_file = os.path.join(outdir, cfg['filename'])
        cmd = build_render_cmd(kicad_cli, board, out_file, args.width, args.height, args.quality, cfg['side'], cfg['rotate'])
        ok = run(cmd)
        if not ok:
            all_ok = False
        print()

    if all_ok:
        print('✓ All 3D renders completed successfully!')
        print('\nExported files:')
        for v in wanted:
            cfg = DEFAULT_VIEWS.get(v)
            if not cfg:
                continue
            pth = os.path.join(outdir, cfg['filename'])
            size = os.path.getsize(pth) if os.path.exists(pth) else 0
            print(' -', pth, f'({size:,} bytes)')
        return 0
    print('✗ Some renders failed')
    return 1


if __name__ == '__main__':
    sys.exit(main())
