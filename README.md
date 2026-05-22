# Schnupperblinki_USB-C
 Schnupperübung für die Schupperschüler

 
 ## Bilder


![Fertige Schaltung](./pic/Blinki%20mit%20USB-C.png)
![SMD Bestückte Schaltung](./pic/Blinki%20mit%20USB-C_SMD_only.png)

## Exporte

- 3D-Ansichten:
  - [3D Top](./pic/3d_top.png)
  - [3D Bottom](./pic/3d_bottom.png)
  - [3D Isometrisch](./pic/3d_isometric.png)

- DXF (Layer-Exports): [dxf/](./dxf/)

### xTool Laser F2 Ultra — empfohlenes Vorgehensweise

- Empfohlen: zwei DXF-Dateien im dxf/-Ordner erzeugen:
  - Edge.Cuts → Schneidekante (äußerste Linie) — zum Schneiden
  - F.Cu     → Gravur (restliche Vektoren, kombiniert) 

Beispielbefehle:

# F.Cu (Gravur)
KICAD_CLI="kicad-cli" ./export_fcu_dxf.sh "Blinki mit USB-C.kicad_pcb" dxf

# Edge.Cuts (Schneiden)
flatpak run --command=kicad-cli org.kicad.KiCad pcb export dxf --layers Edge.Cuts --output-units mm --mode-single -o dxf "Blinki mit USB-C.kicad_pcb"

Hinweis: Die äußerste Linie (Edge.Cuts) ist die Schneidekante; der Rest wird als kombinierter Vektor für die Gravur genutzt. Falls Pfade gemerged oder Text in Konturen umgewandelt werden müssen, kann ein Zusatzskript oder Inkscape dafür genutzt; bei Bedarf hinzufügen.




## Bestückplan
[BOM (HTML-Preview)](https://htmlpreview.github.io/?https://github.com/GerritMihu/Schnupperblinki_USB-C/blob/main/bom/Blinki%20mit%20USB-C-ibom.html)

## Documentation exports

- PCB PDF: [Dok/Dok_PCB.pdf](./Dok/Dok_PCB.pdf)
- Schematic PDF: [Dok/Dok_SCH.pdf](./Dok/Dok_SCH.pdf)
- Schematic SVG: [Dok/Dok_SCH.svg](./Dok/Dok_SCH.svg)

