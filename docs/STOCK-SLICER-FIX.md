# Stock v1.1 slicer diagnostic — resolved for this project

The stock project now slices without the `ZFiller: encounter idx from clip`
diagnostic. CAD, all STL files, before/after renders and N-type toolpaths are
unchanged. The later GUI import correction changes metadata in both projects. This is a stock-specific Bambu Studio process workaround, not a patch
to the installed slicer or a claim that the upstream algorithm is repaired.

## Cause and selected process

Bambu Studio 02.08.02.61 emits the diagnostic in the floating-shell segment
clipping/classification routine. The reported number is a clipping metadata tag,
not an STL triangle or layer index. Primary implementation:
[FillFloatingConcentric.cpp](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/Fill/FillFloatingConcentric.cpp#L389-L492).

The stock-only `slicer/process-stock.json` differs from the common process in
exactly two fields:

| Setting | Previous | Selected |
|---|---|---|
| `detect_floating_vertical_shell` | 1 | 0 |
| `vertical_shell_speed` | 80% of solid-fill speed | Absolute 50 mm/s |

Disabling the problematic per-segment classifier preserves the complete fill
loops. Applying the existing bridge-speed value to the **entire floating-shell
role** preserves conservative deposition speed instead of letting formerly
classified segments run at the ordinary solid-fill percentage. Actual G-code
checks confirm these paths remain at or below 3,000 mm/min (50 mm/s).

The 0.42 mm internal-solid width, six walls, 40% infill, 1.2 mm skins, material,
supports, orientation, brim and all geometry stay unchanged. Narrow-region
handling remains enabled. The tradeoff is roughly 11 additional estimated
minutes: about **8 h 16 min and 312 g**, versus 8 h 5 min before the fix.

## Alternatives and material coverage

A 0.45 mm solid-fill-width trial also cleared the diagnostic, but it removed
some narrow baseline fill bands, up to 5.26 mm² locally. It was rejected.
Simply disabling classification at the original speed was also not selected:
the complete role now receives the explicit 50 mm/s limit.

The selected result has the same 518,135 model deposition paths, widths and
heights as the fill-preserving classification-off trial; only feed rates change.
Across all 249 layers containing solid/floating fill, the largest baseline
footprint absent beyond the 0.03 mm arc/path-analysis tolerance is 0.01894 mm².
Inspected worst-case images show tiny endpoint/arc slivers, not the larger bands
lost by the rejected width change. The analysis polygon grid is 0.0001 mm.

All 340 model layers and 534 material-section components were checked against
the final selected G-code. There are no newly omitted components above 0.05 mm².
Both baseline and fixed results omit the same three sub-nozzle remnants,
approximately 0.095–0.126 mm wide. This is explicit approximation evidence, not
a claim of perfect reproduction of every cross-section or printed strength.

## Regeneration and verification

From the project root:

```sh
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio --debug 3 --load-settings 'slicer/machine.json;slicer/process-stock.json' --load-filaments slicer/filament.json --orient 0 --arrange 1 --slice 0 --export-3mf p1-v11-stock-A1-fit-prototype.3mf --outputdir "$PWD/slicer/stock" p1-roof-mount-stock.stl
python3 tools/preserve_gui_project_settings.py
python3 slicer/verify_projects.py
```

Three independent selected-profile slices plus a re-slice of the saved project
without external settings finish with zero clipping diagnostics and zero error
log entries. The independent selected-profile G-code files are byte-identical.
The stock project reopens as one manifold part with all 103,392 triangles and
the expected 200 × 231.6 × 68 mm bounds. The saved settings, material assignment
and embedded toolpaths are verified. Existing CLI/input-color and timelapse
compatibility notices are recorded separately, not suppressed.

Evidence is under `validation/slicer-fix/`: `diagnostic-fix.json`, the final
component summary, preserved-fill comparison and path-equivalence report.
Source geometry, assembly and opening-contour evidence remains applicable by
unchanged mesh hashes. Physical print/support-cleanup, fit, operating force,
thermal behavior and road retention remain **not checked**.

The PR retains the final corrected 3MFs with embedded toolpaths, source, profiles and concise analysis reports. Raw repeated G-code, parser caches and unselected trial projects are omitted. The current saved-project checker runs directly on the committed corrected projects without regeneration. Historical comparisons require baseline/alternative slices from the retained profiles and unchanged STL; see [review reproduction](REVIEW-REPRODUCTION.md).
