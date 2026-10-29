Before-and-after comparison renders

Before: released original STLs at jamesarich/p1-car-mount 9981cb6.
After: regenerated STLs in the separate p1-car-mount-v1.1 checkout.
Both sides use identical orthographic camera, image size and material color.
Geometry is imported directly; no mesh smoothing, geometry substitution or
generative imagery is used. The N-type section is a Boolean cut of each mesh.

Original design Copyright 2026 James Rich, CC BY-SA 4.0.
Revision work is a digital prototype, not a physical fit or retention test.

Requires Python 3 with Pillow and an OpenSCAD PNG renderer. The recorded
images used OpenSCAD 2021.01; pass --openscad or OPENSCAD_RENDER to select it. This older OpenSCAD is used only to display/export PNGs
of finished meshes; see main build notes for the native modeling toolchain.
When the local 2026 snapshot is present, finished-mesh section/crop Booleans
are evaluated with its Manifold engine into display-only OFF meshes, then
displayed with the same 2021 renderer/cameras as both full-model views.
The OFF crops are reference display artifacts, not printable deliverables.

Reproduce:
python3 comparison/render_comparison.py before --openscad /path/to/png-renderer
python3 comparison/render_comparison.py after --openscad /path/to/png-renderer --fast-openscad /path/to/current/openscad
python3 comparison/compose_comparison.py

The AFTER rendering script refuses geometry whose hash matches BEFORE.
Source mesh hashes and exact commands are recorded in render manifests.
OpenSCAD's informational warning that camera $vp settings override viewall/
autocenter is accepted; other warnings or errors stop the renderer.

Main sheets:
before-after-overview.png — matching N-type and stock overview pairs.
before-after-details.png — window/root close-up and underside pairs.
before-after-pylon.png — stock bore and true N-type center-section pairs.
before-after-cable-saddles.png — left-rear foot / shoulder tie cradle pairs.
before-after-assembly.png — approximate node and nominal full coax-route context.
calibration-shims.png — four separate exported calibration shims at matched scale.
new-stock-pylon-coupon.png — actual new stock fit coupon; no before equivalent.

Assembly views show approximate original node, magnet and antenna reference bodies.
The AFTER cable route uses assembly-refinements.scad reference geometry and is not
part of the printable frame. Catalog cable-length datum and surplus slack are
unverified; the rendered route does not establish real cable or connector fit.
Screw shims are calibration specimens, not a selected service screw stack.
The cable tube is evaluated into a display-only OFF mesh with the 2026 snapshot
for performance and shown black; the nominal node plug remains a gold reference.
Both BEFORE and AFTER mesh hashes were checked against the final exports after
rendering. The AFTER manifest requires published BUILD-MANIFEST version1.1-draft.

Before and after individual PNGs and editable camera definitions in the render drivers are supplied. Generated temporary SCAD wrappers are not committed. The driver extracts the immutable baseline from Git; no sibling checkout is required.
Do not reuse an AFTER PNG after changing the model without regenerating it.
