# Revision 1.1 — digital prototype

Separate version of James Rich’s CC BY-SA 4.0 mount at commit `9981cb6`.
The original checkout is unchanged. All dimensions below are millimeters.

## Geometry and interaction changes

- Native additive R4 concave blends smooth the two connected frame windows
  (each has front/rear corner sectors). R2 upper-edge relief is independent.
  A rounded hub-local blend reaches the original seat plane without changing
  that plane, the inserts, slot travel, magnet locations or bearing interfaces.
- A broad lofted cable-tie saddle grows from the left rear foot/rail shoulder.
  Its rounded cradle follows the variant-specific nominal cable centerline.
  The tie-eye outline is a 3.4 × 2.2 capsule with R1.1 ends and a 0.35 entry flare.
  The saddle crest stays below the cable axis so the tie can contact the cable.
  Use the actual tie only after testing its width/thickness and threading path.
- Complete reference-only coax paths reach the modeled node-side plug axially.
  The free-cable centerlines measure approximately 288.37 N-type / 211.08 stock,
  with source-sampled minimum radii 25 / 15. Actual connector dimensions,
  purchased cable-length datums and excess stock-cable slack remain unmeasured.
- The stock D-flat bore gains a 0.25 exterior entry relief; the lower 2.25 of
  keyed roof and the original seating face remain. The stock pylon now has its
  own full-height coupon (`p1-coupon-pylon-stock.stl`).
- Optional 0.5 / 1 / 1.5 / 2 capsule screw shims preserve the full ±3 slot travel.
  They fit inside the original tool recess and retain planar bearing faces.
  Metal washers remain under the screw heads. No shim thickness is selected as
  a service stack: both usable insert depths, real screw length, washer thickness
  and required engagement must be measured/specified first.

## Source and export construction

The OpenSCAD model and `assembly-refinements.scad` remain the editable source.
The frame blend is evaluated natively once per variant and cached within a build.
Only this new additive blend receives bounded facet reduction at 0.001 tolerance,
before all original mating cuts. This removes redundant tessellation while
preserving the modeled shape within that tolerance; it is not cosmetic smoothing
of the final mount. Cached source/version fingerprints and mesh hashes are checked.

Final exports are explicitly normalized at float32 precision with Manifold.
Zero-area facets may trigger contraction only of an edge shorter than 0.000001,
with total vertex motion capped at that value. Bounds, volume, positive triangle
areas, exact edge topology and binary STL reopening remain strict requirements.
The build manifest records normalization counts and errors. Supported source
parameters have not been validated over arbitrary ranges.

## Opening audit and evidence

The original hex nut traps and stock D-flat retain functional angular outlines
as local antirotation exceptions. Flat bearing faces also remain intentional.
The stock saddle's inboard face is clipped by the original magnet-nut pocket;
that specific flat face/corners preserve the nut installation/antirotation
envelope. Final tie-sweep and web checks include the clipped geometry. This
exception does not waive the rounded tie-eye or open-cradle treatments.
Frame-window roots have no such exception: actual native sections at Z3/8/12
replace the original 88–91° corner turns with ordinary approximately 5.63° facets.
The sampled rear arc fits R4.010, with maximum fit residual 0.0053. The Z16 roof
section transition is distinguished from a sharp through-window wall corner.
See `validation/frame-outline-stations.json`, `frame-radius-fit.json` and final
comparison renders. These samples do not establish a global radius or thickness.

The complete inventory includes both frame windows; six stud bores and nut
pockets; both shank slots and underside access mouths; both rear grips; each
variant’s bore, hardware pocket, rear recess and cable exit; the new tie eye and
open cradle; and the separate shim outlines/bores. Clearance and retention remain
nominal wherever hardware is assumed or photo-derived.

The legacy grip-overhang test is preserved over the original foot/grip height.
The newly added tie passage/head above Z18 is measured separately as a saddle
feature with bridging/support requirements. This avoids misclassifying its roof
as the original finger scoop; it does not waive the original grip check or claim
the new saddle is support-free. Print and inspect the left-rear coupon first.

## Material, assembly and remaining physical work

Use the provisional A1 0.4 / Bambu PETG HF / Textured PEI study only for fit and
support evaluation: feet down, 0.2 model layers, six walls, 40% infill, 1.2 top and
bottom skins, 4 brim and automatic normal supports. The author’s service-material
choice is ASA on a P1S. Neither PETG service suitability nor ASA printing on an
A1 is established by this revision.

Print the seat, corresponding pylon, left-rear cradle/foot and shims as needed.
Check hardware insertion, nut capture, clamp-before-bottoming, engagement,
support removal, tie threading, cable clamping and corner removal without damage.
The conservative optional Ø15 connector-tool cylinder overlaps the approximate
node skirt; the nominal plug clears. Verify access with the actual thin open-ended
wrench/tool instead of claiming generic socket clearance.

Roof conformity cannot be corrected without a roof/contact measurement. Confirm
all six contact patches without rocking before choosing any height correction.
An independent tether requires an actual path, anchor and load specification;
no untested anchor or road-load rating is invented here. Actual cable lengths,
thermal/UV/creep behavior, magnet retention, wind/impact/fatigue loads, comfort
and removal force remain physical tests. No printer was operated in this task.

Final validation areas and estimates are recorded in the comparison report and
`BUILD-MANIFEST.json`; physical testing remains **not checked**.

## Stock slicing follow-up

The stock diagnostic is now resolved for this project using a preserved-fill
process workaround; CAD and every STL are unchanged. The stock profile bypasses
per-segment floating classification and applies an absolute50mm/s speed to the
entire floating role while retaining0.42mm solid fill. See
[STOCK-SLICER-FIX.md](STOCK-SLICER-FIX.md) for source analysis, rejected alternatives,
all-layer coverage and saved-project checks. Physical tests remain unperformed.

GUI delivery correction: use the A1-supported.3mf projects linked in the README. Their retained-override metadata preserves six walls, 40% infill, supports and the intended process on GUI import. See [GUI project fix](GUI-PROJECT-FIX.md).
