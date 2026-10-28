# Print notes

One printed frame with direct bulkhead antenna mounting and no added fasteners. The source is `p1-roof-mount.scad`; the N-type frame is `p1-roof-mount-n-type.stl` (`antenna = "alfa"` in the source, after the ALFA antenna it was sized for) and the stock-antenna frame is `p1-roof-mount-stock.stl` (`antenna = "stock"`).

## Design

- Both pylons are the same continuous loft: a round top with a 4 mm roundover over a broad root that spreads forward and sideways into the rear rail and center spine. The N-type top is Ø35 mm; the stock top is Ø24.6 mm. The spine ends inside the root.
- Both pylons share one rear recess: a short 10 mm cable exit, a long gentle taper above a curved bowl, and a rounded crown, rounded in plan at its forward end to follow the outside wall. The N-type chamber is 26 mm wide with its bowl near the bed; the stock chamber is 14 mm wide with its bowl floor at Z=22 mm. The build rejects any sampled radial wall under 4 mm (104 front/side samples per N-type frame and coupon, 65 on the stock frame). These are sampled thicknesses, not a strength rating.
- The stock RP-SMA jack mounts from below: its hex body, flat washer and toothed lock washer sit in a Ø11.4 mm round pocket under the 2.5 mm D-flat roof, which keys it against turning, and the nut tightens on top.
- The lower rear face retreats to clear the modeled cable bend.
- The underside node-screw pockets follow the full ±3 mm shank-slot travel. Their 18 × 24 mm capsule entrances bevel down to 16 × 22 mm at the flat bearing shoulder; the bearing web is 2 mm.
- The rear grips are curved finger scoops under level rear bosses, each boss a single rounded solid with no underside shelf.
- N-type nut capture is slotless: a Ø21.1 mm washer passage with six hex corner stops. Rotation checks include hypothetical nut corner diameters of 21.5 and 21.3 mm at lateral offsets −0.3/0/+0.3 mm. Those are sensitivity tests, not measured hardware specifications.
- OpenSCAD's fast preview can show a stray line on the front air dam; the evaluated and exported solid has none. Preview evaluates the mount before display.

## Which files to print

| File | Purpose |
|---|---|
| `p1-roof-mount-n-type.stl` | Frame for an N-type bulkhead antenna |
| `p1-roof-mount-stock.stl` | Frame for the stock antenna |
| `p1-coupon-pylon.stl` | Full-height N-type pylon; washer/nut/bore fit and support cleanup |
| `p1-coupon-seat.stl` | Both node screw pockets and their head/tool access |
| `p1-coupon-front-foot.stl` | Front magnet foot |
| `p1-coupon-rear-right-foot.stl` | Right rear foot and grip |
| `p1-coupon-rear-left-foot.stl` | Left rear foot and grip |

Coupons are test pieces, not assembly parts; the pylon coupon is N-type only. The N-type frame is 200 × 241.5 × 68 mm and the stock frame is 200 × 231.6 × 68 mm. Center it on the bed and reserve space for the brim and supports; the 256 mm bed allowance includes a 4 mm brim and at least 1 mm edge margin on each side.

## Printing and supports

Print feet down in the exported orientation. Start with ASA at 0.2 mm layers, six walls, 40% infill and a 4 mm brim, then tune using the coupons and the actual filament and printer.

The complete frame needs selective support or bridging:

- Beneath the flat washer-bearing ledge and small nut-pocket shoulders (N-type) or the body-pocket ceiling (stock). Keep supports removable through the rear opening and avoid damaging the corner stops during cleanup.
- The two node-screw bearing ceilings. Their enlarged access pockets accommodate tool travel but still have flat bearing shoulders.
- The rounded pylon crown, where the slicer shows shallow overhangs. Remove these supports through the upper opening; the 10 mm lower cable exit is not the removal route.
- The magnet foot bearing faces are flat and their vertical stud holes have first-layer lead-ins, so the feet need no support.

The horizontal-section audit is a geometry check, not a sliced toolpath. An N-type pylon of this geometry has been printed and assembled and works; the stock pylon has not been printed. Print the pylon coupon first for N-type fit and support cleanup, and the seat coupon to confirm the actual screw heads and socket reach both ends of the slots.

## Assembly

Stock frame: remove the bulkhead nut, leaving the flat washer and the toothed lock washer on the body. The cable's node-end plug is wider than the Ø6.8 bore, so work from inside: bring the bulkhead end up through the rear recess and push its thread up through the D-flat bore until both washers and the hex body seat in the pocket under the roof. Fit the nut on top and tighten with an 8 mm wrench, then screw on the antenna. Lead the cable down through the recess and out of the rear opening to the node's jack.

N-type frame: remove the connector nut and washer. Feed the cable through the antenna bore from above and slip the washer, then nut, onto the free cable end. Bring each into the rear chamber below the threaded shank, roughly 44 mm above the frame bed, and raise it on the connector axis. The washer passes upward through the round relief and rests beneath the roof.

Start the nut on the thread with its corners aligned to the pocket, turning the connector from above as needed while its cable is free to rotate. Tighten before connecting the cable to the node. Confirm capture with the actual nut in the coupon; do not force or over-tighten the small printed stops. Fit the antenna onto the metal coupling afterward.

The underside access slots accept the modeled Ø15 mm tool envelope at all three tested positions. Confirm the actual socket diameter and supplied screw head. A nominal 6 mm screw through a 2 mm bearing web leaves 4 mm before any washer or insert recess; check actual engagement and bottoming before tightening.

## Dimensions and limits

The bulkhead envelope is provisional: shank Ø15.875 mm, 15 mm panel-thread length, flange Ø24 mm, nut 19.1 mm across flats × 2.82 mm thick, and washer Ø20.5 × 1.1 mm. The straight antenna bore is Ø16.475 mm with a 0.4 mm entrance chamfer. The washer passage has 0.3 mm radial allowance. Confirm nut corners as well as flats: small or heavily rounded corners can defeat capture even if the nut fits.

The stock RP-SMA envelope is photo-derived: the supplied Seeed pigtail was photographed flat beside a US quarter, the quarter fixed the scale at the table and the 1/4-36 thread pitch fixed it at the connector, about 3% plus 0.1 mm per edge. Seeed publishes no drawing. The part is a front-mount jack with, from the cable side, a hex body 8.1 mm across flats (9.4 across corners) × 1.9 mm, a flat washer Ø10.0 × 1.0 mm, a toothed lock washer Ø8.7 mm (2.1 mm as photographed, cocked on the thread; 0.6 mm flattened), and a 5/16" nut 7.8 mm across flats × 1.5 mm. The thread measures 6.06 mm, consistent with 1/4-36, and keeps the 5.8 mm D-flat bore. It runs 10.25 mm above the body plus a 0.9 mm plain nose, ±0.5 mm. With both washers under the 2.5 mm roof and the nut on top, 4.65 mm of thread remains for the antenna coupling; the build requires 4 mm and allows a 3.15 mm panel. Under the body the heat shrink is Ø5.4 × 9 mm over the crimp ferrule, then Ø4.6 × 9.5 mm over the cable, which measures Ø2.9 mm. The pocket is Ø11.4 mm, 0.7 mm radial clearance around the flat washer, and 5.6 mm tall for the body plus the photographed washer stack plus 0.6 mm. The photo cannot resolve the washer thicknesses to better than about 0.3 mm or tell whether the flat washer is loose or an integral flange; neither changes the pocket.

The modeled N-type cable uses a 25 mm bend radius around Ø2.5 mm cable and the stock cable a 15 mm bend radius around Ø2.9 mm cable, starting below the heat shrink tail, each with a 1 mm radial keep-out. The magnet foot web is nominally 3.03 mm, with 1.27 mm stud protrusion beyond the modeled nut. Back-box and insert coordinates, connector hardware and magnet stud/nut dimensions still require confirmation against the actual parts. No aerodynamic, road-load or tightening-torque performance has been measured.

## Rebuild

```sh
python3 tools/check_parameters.py
python3 tools/build_models.py
```

The build uses `openscad` from PATH and publishes exports only after geometry checks pass. `BUILD-MANIFEST.json` records source and mesh hashes, topology/bounds, source-level interference checks, exported bore and hardware insertion probes, screw/tool travel, rounded-nut rotation stops, lower-pylon and root sections, front/side radial wall thickness, and downward-face measurements. Source interference checks run as two unions (N-type and stock); each union must be empty, so every constituent check must be empty. `docs/validation.md` summarizes the measured results.
