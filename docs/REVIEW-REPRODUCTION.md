# Reproducing the v1.1 review

The PR contains final editable CAD, exported meshes, the two corrected sliced A1 projects, camera/render drivers and concise evidence. Runtimes, temporary assembly assets, generated camera wrappers, raw duplicate G-code, obsolete project exports, experimental meshes and large parser caches are not committed.

## Check the delivered files

Use a Python virtual environment with `tools/requirements-v11.txt`. The native build used OpenSCAD 2026.10.27; the saved projects used Bambu Studio 02.08.02.61. Analysis dependencies are pinned alongside the core geometry dependencies.

```sh
python3 tools/check_parameters.py
python3 slicer/verify_projects.py
```

The project checker reads geometry, saved settings and actual embedded G-code from the corrected `A1-supported.3mf` files. It checks them against final STLs and retained toolpath hashes, including real support/interface extrusion and the retained GUI override metadata. It does not need any old project or standalone G-code.

`BUILD-MANIFEST.json` records eight final native frame/coupon exports and frozen source hashes. `validation/shim-exports.json` records the four separate shims. The assembly, opening and slicer reports have explicitly limited digital scope; no physical printing or road qualification is implied.

## Regenerate geometry and nominal assembly checks

```sh
python3 tools/build_models.py --openscad /path/to/current/openscad
python3 tools/export_shims.py --openscad /path/to/current/openscad
python3 validation/final_assembly_checks.py --prepare --openscad /path/to/current/openscad
python3 validation/final_assembly_checks.py --openscad /path/to/current/openscad
```

Rebuilding can change tessellation and mesh hashes. Regenerate dependent renders, slices and reports before delivering a changed export. Cache reuse is source/version/hash guarded; an ignored cache is never the editable source. The exact-1 mm cable-boundary intersection and conservative long-tool collision remain recorded in `validation/final-assembly.json`; their nominal tolerance/real-tool limitations have not been turned into unconditional passes.

## Regenerate before-and-after views

The render driver extracts baseline display inputs from the immutable Git commit `9981cb696d0fd03d09503277934305a4a317377c` into an ignored directory. A separate original checkout is optional via `--original`. A recent shallow clone must fetch that baseline commit first.

```sh
python3 comparison/render_comparison.py before --openscad /path/to/png-renderer
python3 comparison/render_comparison.py after --openscad /path/to/png-renderer --fast-openscad /path/to/current/openscad
python3 comparison/compose_comparison.py
```

The recorded PNGs used OpenSCAD 2021.01 for displaying finished meshes and the 2026.10.27 Manifold build for display-only cuts. For the closest visual match, use those versions; other versions/fonts may render differently without changing geometry. Set `OPENSCAD_RENDER` for the shim renderer. The compositors accept `RENDER_FONT` and `RENDER_FONT_BOLD`, then try Arial, DejaVu Sans and Pillow's default. Camera and model settings are in the render drivers; no AI-generated model imagery is used. Historical report/command paths have been normalized to `${REPO_ROOT}` and `${BASELINE_ROOT}`; their geometry hashes are unchanged.

## Re-slice and preserve editable GUI settings

The delivered projects already contain their machine/material/process values and saved toolpaths. For independent regeneration, use the recorded Bambu Studio version; different installed system presets must be rechecked in the GUI.

```sh
# Example executable; set this to the installed Bambu Studio CLI.
BAMBU_STUDIO=/Applications/BambuStudio.app/Contents/MacOS/BambuStudio
mkdir -p slicer/stock slicer/n-type
"$BAMBU_STUDIO" --debug 3 --load-settings 'slicer/machine.json;slicer/process-stock.json' --load-filaments slicer/filament.json --orient 0 --arrange 1 --slice 0 --export-3mf p1-v11-stock-A1-fit-prototype.3mf --outputdir "$PWD/slicer/stock" p1-roof-mount-stock.stl
"$BAMBU_STUDIO" --debug 3 --load-settings 'slicer/machine.json;slicer/process.json' --load-filaments slicer/filament.json --orient 0 --arrange 1 --slice 0 --export-3mf p1-v11-n-type-A1-fit-prototype.3mf --outputdir "$PWD/slicer/n-type" p1-roof-mount-n-type.stl
python3 tools/preserve_gui_project_settings.py
python3 slicer/verify_projects.py
```

The metadata correction uses the retained GUI-normalized system-default snapshot for this slicer version. Only retained-override metadata changes; model data, effective values and embedded G-code remain intact. Open each corrected file **as a project**, verify six walls, 40% infill, 1.2 mm skins, normal automatic supports and the intended variant-specific settings, then slice, save and reopen. The original review performed this GUI sequence for both variants. GUI Save Project omitted G-code in the separate validation copies; the delivered supported projects retain it.

For optional actual-path plots:

```sh
python3 tools/extract_project_gcode.py
python3 tools/inspect_toolpaths_v11.py
```

## Retained historical analysis

The stock clipping workaround was selected after three independent slices and a saved-project re-slice, an all-340-layer section/component audit, a 249-level width-aware fill comparison and exact geometric equivalence of 518,135 model deposition paths. Summary reports, the selected worst-case images, original profile and source analysis are retained under `validation/slicer-fix/`. The discarded 0.45 mm-width trial is retained only as comparison metrics; it is not a printable delivery.

These are frozen historical reports, not a promise that their omitted scratch caches and trial paths exist in a fresh clone. Repeat those experiments by generating baseline/alternative slices from the retained profiles and unchanged STL. Current artifact checks and plots above run directly from the committed final projects. Physical support removal, tie threading, measured connector/washer/insert fit, roof contact, heat/UV/creep behavior and vehicle retention remain untested.
