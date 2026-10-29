# A1 project loading fix — v1.1

The `A1-supported.3mf` projects supersede the earlier `A1-fit-prototype.3mf` files for opening and editing in Bambu Studio:

- [Stock antenna A1 project](../slicer/stock/p1-v11-stock-A1-supported.3mf)
- [N-type antenna A1 project](../slicer/n-type/p1-v11-n-type-A1-supported.3mf)

“Supported” identifies the saved support configuration. It does not establish a successful physical print or qualification for vehicle use.

## What the screenshot exposed

The user's stock-mount screenshot showed a floating-cantilever warning. Inspection in the live Bambu Studio GUI found support generation disabled and the process using Standard defaults. Enabling support and slicing again cleared that warning in the GUI. That diagnostic was separate from the earlier stock `ZFiller` issue.

The earlier CLI checks read the saved settings and re-sliced through the command-line loading path. Those files contained `enable_support=1` and real support toolpaths. That evidence did not test how the GUI reconstructs the editable presets. The previous GUI-persistence claim was therefore incomplete.

## Root cause

The CLI-exported projects named the built-in `0.20mm Standard @BBL A1` process, but their `different_settings_to_system` metadata contained three empty strings. The GUI uses that metadata to decide which saved values are deliberate overrides and which should follow the installed system presets.

For the process, Bambu Studio reads the first difference string, adds the preset-identity exclusions, and passes the resulting set into its external-preset loader. When it finds the named system preset, it replaces values not listed as differences with that preset's defaults. Thus the saved support-on setting, six walls, 40% infill, and other process overrides could revert when the GUI opened the project.

This behavior is visible in the source for the installed Bambu Studio 02.08.02.61:

- [Parse and apply process difference metadata](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PresetBundle.cpp#L3863-L3879).
- [Load an external preset and update unlisted values from the installed base](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/Preset.cpp#L2245-L2269).
- [Replace an option only when it is absent from the retained-difference set](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp#L9267-L9288).
- [Emit the floating-cantilever warning when support is disabled](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintObject.cpp#L865-L898).

The three difference strings correspond to process, the single filament, and printer. A blanket list of every setting was considered but rejected because it also marked unchanged custom-G-code fields as overrides and produced an unnecessary custom-G-code notice.

## Repair and preservation

`tools/preserve_gui_project_settings.py` builds the retained-difference lists against a system-default snapshot normalized through the GUI. This records the actual differences while keeping the frozen geometry, effective settings, and embedded toolpaths unchanged. Comparing only the raw installed profile JSON is insufficient because the effective presets also include inherited and compiled defaults.

The intended preserved configuration is Bambu Lab A1, 0.4 mm nozzle, Textured PEI, provisional Bambu PETG HF, 0.2 mm model layers, six walls, 40% grid infill, 1.2 mm top and bottom skins, 4 mm brim, and normal automatic supports with support on model surfaces allowed. The stock-specific `ZFiller` workaround remains classifier off with the floating-shell role limited to 50 mm/s; internal-solid line width remains 0.42 mm. No geometry or support-policy redesign is part of this repair.

The earlier files remain as provenance for the validated toolpaths. Use the supported projects above for the corrected GUI import metadata.

## Verification status

Both corrected delivery projects were opened as projects in Bambu Studio 02.08.02.61. The interface retained support enabled with normal automatic supports, six walls, 40% infill, 1.2 mm top/bottom skins and the variant-specific floating-shell settings. Fresh GUI slices completed without the floating-cantilever warning. Both were saved to separate validation projects, reopened, and again showed support enabled.

Independent comparison of both GUI saves checked 185 process, 104 machine and 127 filament options against each corrected delivery. All non-UI effective settings matched. Exact mesh XML was byte-identical; world placement agreed within 0.000001 mm. GUI normalization of preset metadata, AMS/nozzle status, and one-filament purge arrays is recorded separately. No printer was operated.

[Metadata-only archive checks](../validation/cantilever-reopen/metadata-fix.json) prove that only the retained-override metadata changed in the delivered archives. Every geometry entry, actual setting value and embedded G-code byte is unchanged. [GUI roundtrip comparison](../validation/cantilever-reopen/gui-settings-verification.json) records the saved settings and geometry comparisons. The current delivered-project checker is `slicer/verify_projects.py`; repeat the manual GUI save/reopen sequence in [review reproduction](REVIEW-REPRODUCTION.md) to independently confirm GUI behavior. Historical GUI-save copies are omitted from the PR.

Bambu's GUI Save Project operation omitted embedded G-code in the validation copies; those copies are not the delivered sliced files. The corrected A1-supported deliveries retain the previously checked embedded toolpaths. Existing timelapse compatibility notices and physical support/bridge limitations remain recorded; clearing this warning does not establish a successful physical print.

CAD, usability, opening-contour, and assembly evidence are unchanged by this metadata-only repair and retain their existing scope and limitations. Physical printing, support removal, fit, strength, and vehicle use remain **not checked**. The user's insert-depth and washer-thickness measurements remain unknown, so the optional screw shims remain adjustable rather than a specified final stack.
