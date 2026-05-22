# Copilot instructions for Schnupperblinki_USB-C

## Quick commands (project-specific)
- Run combined export (DXF + 3D PNG):
  - bash ./export_all.sh
  - or: python3 export_all.py

- Run DXF export only:
  - bash ./export_dxf.sh
  - or: python3 export_dxf.py

- Run 3D PNG renders only:
  - bash ./export_3d_png.sh
  - or: python3 export_3d_png.py

Notes: scripts call KiCad's CLI via `flatpak run --command=kicad-cli org.kicad.KiCad` by default. If using a native kicad-cli, edit the KICAD_CLIPATH variable in the Python scripts or run with that binary in PATH.

## Build / test / lint
- No automated build, test, or lint toolchain found in this repository.
- "Single-test" guidance: there are no unit tests. Use the individual export scripts above to validate outputs (DXF files in `dxf/`, PNGs in `pic/`).

## High-level architecture
- This is a KiCad PCB project. Key artifact types:
  - Schematic: `Blinki mit USB-C.kicad_sch`
  - PCB: `Blinki mit USB-C.kicad_pcb` (primary source for exports)
  - Footprint library: `Lib.pretty/` and `lib.kicad_sym` (symbols)
  - BOM and documentation: `bom/`, `pic/`, `dxf/`
- Export automation:
  - `export_dxf.*` (shell & python) exports each layer as DXF (per-layer, Edge.Cuts included).
  - `export_3d_png.*` (shell & python) renders top, bottom and isometric PNGs (1600×900, high quality).
  - `export_all.*` runs DXF export then 3D renders and prints exported filenames.
- Outputs are intended for documentation and fabrication (DXF for CNC/laser/plotting, PNG for README and previews).

## Key conventions and patterns
- Scripts assume the PCB filename is `Blinki mit USB-C.kicad_pcb`. Updates to the PCB filename must be mirrored in the scripts (variables PCB_FILE or script arguments).
- Exports use these fixed output directories:
  - DXF -> `dxf/` (one file per layer, Edge.Cuts included via `--common-layers`)
  - 3D PNG -> `pic/` (3d_top.png, 3d_bottom.png, 3d_isometric.png)
- The scripts default to calling KiCad via Flatpak. To run against a system install, edit `KICAD_CLIPATH` in the Python scripts or replace the flatpak prefix in shell scripts.
- DXF export settings used consistently: units = mm, `--drill-shape-opt 1`, and `--mode-multi` to emit separate files per layer. When updating export logic, preserve these flags unless intentionally changing output semantics.
- 3D render settings: width 1600, height 900, quality = high, isometric rotate `45,0,45`. 
- Filenames contain spaces and an umlaut ("Blinki mit USB-C"). Scripts quote variables/arguments correctly; be cautious when editing to preserve quoting.

## Files to consult when changing exports
- `export_dxf.py` / `export_dxf.sh`
- `export_3d_png.py` / `export_3d_png.sh`
- `export_all.py` / `export_all.sh`

## Other AI assistant configs
- No CLAUDE.md, .cursorrules, AGENTS.md, .windsurfrules, CONVENTIONS.md, or .clinerules files were found. No additional assistant config incorporated.

---

Summary:
- This file lists repository-specific commands, architecture notes, and conventions for editing export scripts and outputs. Keep the KICAD_CLIPATH and PCB_FILE variables in sync if renaming or changing how KiCad is invoked.
