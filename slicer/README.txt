CURRENT GUI DELIVERIES
Use stock/p1-v11-stock-A1-supported.3mf or
n-type/p1-v11-n-type-A1-supported.3mf. Open as a project, retaining settings.
These correct missing retained-override metadata in the earlier fit-prototype
exports. The older files contain the same geometry/settings/toolpaths but could
reset custom settings to Standard defaults in the GUI. See docs/GUI-PROJECT-FIX.md.
Reproduce this packaging fix with tools/preserve_gui_project_settings.py AFTER
creating the original sliced exports below. The script changes only import metadata.

v1.1 A1 fit-prototype slicing study

Bambu Studio02.08.02.61, A1 0.4 mm, Textured PEI, provisional Bambu PETG HF,
0.2 mm model layers, six walls,40% infill,1.2 mm top/bottom skins,4 mm brim,
automatic normal supports with cavity support allowed. No printer was operated.
Actual spool grade/color and AMS lite slot are not confirmed. Single filament.

From repository root, N-type command:
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio --load-settings 'slicer/machine.json;slicer/process.json' --load-filaments slicer/filament.json --orient 0 --arrange 1 --slice 0 --export-3mf p1-v11-n-type-A1-fit-prototype.3mf --outputdir "$PWD/slicer/n-type" p1-roof-mount-n-type.stl

For stock, use slicer/process-stock.json instead of slicer/process.json, and substitute the stock STL/output folder/project name. Use an absolute
output directory and basename for export-3mf with this installed version.
Machine/process/filament files include inherited settings and G-code templates;
they are the exact saved inputs, not merely preset names. Projects persist these
settings, material assignments and embedded toolpaths. verify_projects.py checks
geometry against final STLs and embedded G-code hashes against retained evidence.

N-type:111612 triangles retained,~8h34m,330g; unchanged project.
Stock:103392 triangles retained,~8h16m,312g. The stock-only workaround sets
detect_floating_vertical_shell=0 and absolute vertical_shell_speed=50 mm/s;
internal-solid width stays0.42. All other process values match the common profile.
This bypasses the buggy segment classifier while printing the ENTIRE floating
role at bridge speed. Three independent slices and a re-slice of the saved
project without external profiles finish with no ZFiller diagnostic/error logs.
The independent selected-profile G-code files are byte-identical.

Both projects reopen manifold with persisted geometry/settings/toolpaths. Ordinary
CLI/input-color and timelapse compatibility notices remain separate. All340stock
model layers and249solid/floating-bearing levels were audited; no new omitted
components, and the same three0.095-0.126mm sub-nozzle remnants remain.
See docs/STOCK-SLICER-FIX.md and validation/slicer-fix/diagnostic-fix.json.
Slicer acceptance is digital/targeted; physical support/bridge acceptance and
roof-service qualification remain NOT CHECKED.

Native source frames passed topology, hardware and grip checks. The left-rear
coupon includes the complete new N-type saddle; inspect tie threading, bridge
roof, cleanup and cable clamp physically. The stock saddle is represented in its
full-frame slice. Geometry-only shim3MF has four named calibration specimens and
NO machine/material profile or saved slicing.

Actual path plots, including new tie-eye roof/cradle, are toolpaths-n-type.png /
toolpaths-stock.png in the repository root; tools/inspect_toolpaths_v11.py includes
G2/G3 arcs and full previous model/support paths. These targeted views do not
establish exhaustive bridge anchoring or successful physical printing.
