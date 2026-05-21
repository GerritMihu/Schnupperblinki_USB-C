#!/usr/bin/env python3
"""
Export documentation artifacts from a KiCad project:
- PCB PDF into Dok/ (default Dok/Doc_PCB.pdf)
- Schematic PDF and SVG into Dok/

Usage: python3 export_docs.py [--board <board.kicad_pcb>] [--schematic <file.kicad_sch>] [--outdir Dok] [--kicad-cli "kicad-cli"]
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys


def find_file(ext, provided):
    if provided:
        return provided
    candidates = [f for f in os.listdir('.') if f.endswith(ext)]
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # multiple -> prefer exact project-like names
    # fall back to first but notify
    print(f'Warning: multiple *{ext} files found, using {candidates[0]}')
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


def build_and_run(kicad_cli, parts):
    cmd = shlex.split(kicad_cli) + parts
    return run(cmd)


def main():
    p = argparse.ArgumentParser(description='Export PCB PDF and schematic PDF/SVG into Dok folder')
    p.add_argument('--board', '-b')
    p.add_argument('--schematic', '-s')
    p.add_argument('--outdir', '-o', default='Dok')
    p.add_argument('--kicad-cli')
    args = p.parse_args()

    board = find_file('.kicad_pcb', args.board)
    sch = find_file('.kicad_sch', args.schematic)
    kicad_cli = find_kicad_cli(args.kicad_cli)
    outdir = args.outdir

    if not board and not sch:
        print('No board or schematic found. Provide --board and/or --schematic.')
        sys.exit(2)

    os.makedirs(outdir, exist_ok=True)

    ok = True

    if board:
        pcb_pdf = os.path.join(outdir, 'Dok_PCB.pdf')
        # KiCad pcb pdf export requires layers; use common visible fabrication layers
        pcb_layers = ['F.Cu', 'B.Cu', 'Edge.Cuts']
        parts = ['pcb', 'export', 'pdf', '--layers', ','.join(pcb_layers), '-o', pcb_pdf, board]
        print('\nExporting PCB to PDF ->', pcb_pdf)
        if not build_and_run(kicad_cli, parts):
            ok = False

    if sch:
        sch_pdf = os.path.join(outdir, 'Dok_SCH.pdf')
        sch_svg = os.path.join(outdir, 'Dok_SCH.svg')
        # schematic PDF
        parts_pdf = ['sch', 'export', 'pdf', '-o', sch_pdf, sch]
        print('\nExporting Schematic to PDF ->', sch_pdf)
        if not build_and_run(kicad_cli, parts_pdf):
            ok = False
        # schematic SVG
        parts_svg = ['sch', 'export', 'svg', '-o', sch_svg, sch]
        print('\nExporting Schematic to SVG ->', sch_svg)
        if not build_and_run(kicad_cli, parts_svg):
            ok = False
        else:
            # KiCad may create a directory when exporting SVGs (one file per sheet).
            # If the target is a directory, pick the first SVG file and move/rename it to the expected path.
            if os.path.isdir(sch_svg):
                svgs = [os.path.join(sch_svg, f) for f in os.listdir(sch_svg) if f.lower().endswith('.svg')]
                if len(svgs) == 0:
                    print('Warning: schematic SVG export created directory but no SVG files found')
                else:
                    chosen = svgs[0]
                    final_path = sch_svg  # desired single-file path
                    tmp_target = final_path + '.tmp'
                    print('Found schematic SVG:', chosen, '-> moving to', final_path)
                    try:
                        # move the chosen file out to a temporary file path
                        os.replace(chosen, tmp_target)
                        # remove any leftover files in the created directory
                        for f in svgs[1:]:
                            try:
                                os.remove(f)
                            except Exception:
                                pass
                        # remove the now-empty directory
                        try:
                            os.rmdir(sch_svg)
                        except Exception as e:
                            print('Warning: could not remove svg export directory:', e)
                        # rename the temporary file to the final desired path
                        os.replace(tmp_target, final_path)
                    except Exception as e:
                        print('Failed to relocate schematic SVG:', e)

    if ok:
        print('\nAll documentation exports completed successfully!')
        return 0
    print('\nSome documentation exports failed')
    return 1


if __name__ == '__main__':
    sys.exit(main())
