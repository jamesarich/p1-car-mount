Independent width-aware deposition comparison

Inputs: baseline repro/plate_1.gcode, solid-width045 trial, and floating-off trial.
No source, profile, STL, or delivered project was modified by this analysis.

Parser: tools/inspect_toolpaths_v11.py, including G2/G3 IJ arcs with <=0.02 mm
chord sagitta and all positive-E model paths. Buffer radius is stated LINE_WIDTH/2.
Analysis polygon coordinates are regularized on a0.0001 mm grid after an initial
GEOS precision topology exception; this regularization affects only comparison
polygons, not G-code or model geometry. We report one-sided baseline Internal
solid infill/Floating vertical shell footprints absent from all candidate model
path coverage. A0.03 mm comparison allowance covers chord approximation and the
0.015 mm nominal half-width shift in the0.45 trial. It is not a physical-fit or
bridge-anchoring allowance. Quad-segment buffer cap approximation is2.

All249 model levels with either target solid-fill feature are checked. Other
model levels are outside this band-focused comparison; parent's independent
mesh/component audit addresses all340 model levels.

0.45 mm width candidate:
- Exact outer-wall and inner-wall path sets remain identical to baseline.
- Largest baseline-filled patch absent beyond0.03 mm:5.259685 mm2 at Z12.6.
- Total one-sided loss beyond tolerance, summed across249 layers:553.304277 mm2.
- Worst patches include thin rings/fill-boundary strips; some maximum inscribed
  diameters are0.34–0.71 mm. This is not proof of an invalid print (fill routing
  legitimately changes with width), but it does not support a no-material-loss
  claim and is less conservative than the alternative below.

0.42 mm width, detect_floating_vertical_shell=0 candidate:
- Exact outer/inner wall, sparse-infill, bottom-surface, brim and overhang wall
  command geometry remains identical. Floating-role commands differ by six
  clipping/splitting commands. See floating-off-unmatched-layers.json.
- Largest baseline-filled patch absent beyond0.03 mm:0.01893922 mm2 at Z13.6.
- Total one-sided loss beyond tolerance, summed across249 layers:0.21417971 mm2.
- All four worst plots visually inspected: only tiny endpoint/arc/seam patches,
  no missing broad solid band like the0.45 candidate.
- This geometric evidence transfers to a conservative vertical-shell-speed50
  candidate ONLY if its spatial/width/E paths are independently shown equal to
  the floating-off candidate. Exact equivalence confirmed for all518,135 model deposition commands, including
  pathwidth and Z (ignorefeed/order/reversal), and allmodel-roleE totals agree
  within1e-8mm. Seechosen-candidate-path-equivalence.json. Parent separately
  checksfloatingfeedrates<=50mm/s and repeat-slice diagnostics.

These are digital path comparisons, not proof of deposited bead shape, layer
bonding, support removability, or physical strength. Output JSONs preserve all
per-layer metrics and worst-view PNGs. Parsed pickle files are scratch caches;
regenerate them with the established parser rather than packaging them.
