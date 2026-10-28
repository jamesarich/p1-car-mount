# SenseCAP Solar Node P1 magnetic roof mount

![N-type frame](images/overall.png)

A one-piece magnetic car-roof mount for the Seeed SenseCAP Solar Node P1 / P1-Pro. The node bolts to a center hub through its two 1/4-20 back inserts, tilted 4° nose down. Six stud magnets hold the frame to the roof. A swept pylon behind the node carries the antenna on its bulkhead connector: an N-type bulkhead for an external antenna, or the node's stock RP-SMA rod. Version 1.0.

![Stock-antenna frame](images/overall-stock.png)

## Files

| File | Print? | Purpose | `antenna` | `part` |
|---|---|---|---|---|
| `p1-roof-mount-n-type.stl` | yes | Frame for an N-type bulkhead antenna | `alfa` | `mount` |
| `p1-roof-mount-stock.stl` | or this | Frame for the stock RP-SMA antenna | `stock` | `mount` |
| `p1-coupon-pylon.stl` | test | N-type pylon: washer, nut, bore fit and support cleanup | `alfa` | `coupon` |
| `p1-coupon-seat.stl` | test | Node screw pockets and tool access | either | `seat_coupon` |
| `p1-coupon-front-foot.stl` | test | Front magnet foot | either | `foot_coupon` |
| `p1-coupon-rear-right-foot.stl` | test | Right rear foot and grip | either | `rear_foot_coupon` |
| `p1-coupon-rear-left-foot.stl` | test | Left rear foot and grip | either | `rear_left_foot_coupon` |
| `p1-roof-mount.scad` | source | OpenSCAD model | | |
| `p1-node-model.scad` | source | Fit-check model of the P1, used by the main source | | |

`antenna = "alfa"` is the N-type variant, named for the ALFA antenna it was sized around. Coupons are optional test pieces, not assembly parts. Print the pylon and seat coupons first.

## Print settings

- Printer: Bambu P1S (256 mm bed). Frames are 200 × 241.5 × 68 mm (N-type) and 200 × 231.5 × 68 mm (stock).
- Material: ASA, light color.
- 0.2 mm layers, 6 walls, 40% infill, 4 mm brim.
- Orientation: feet down, as exported. Center on the bed.
- Supports: under the pylon crown and nut chamber, and the two node-screw ceilings. The flat feet need none.

No slicer project or physical print has validated this design yet. Treat these as starting settings and tune with the coupons.

## Hardware

- Seeed SenseCAP Solar Node P1 or P1-Pro
- 6× DIYMAG 1.69" (43 mm) magnets with 1/4" studs, plus 6× 1/4-20 nylon-insert lock nuts
- 2× 1/4-20 screws into the node's back inserts, length checked against `docs/print-notes.md`
- N-type frame: an RP-SMA to N-female bulkhead cable (RG316) and an N-male antenna
- Stock frame: the node's RP-SMA bulkhead cable and stock rod antenna
- Blue threadlocker

Hardware dimensions are modeled from datasheets and photos and are still provisional. Confirm the nut corners, washer, thread length, socket and magnet studs with the coupons.

## Assembly

1. Press the lock nuts into the feet, nylon up, and thread on the magnets.
2. Fit the bulkhead connector down through the pylon bore and start its nut from the rear chamber. Full steps for both frames are in `docs/print-notes.md`.
3. Bolt the node to the hub with threadlocker.
4. Remove the mount by lifting one rear corner at the grip under the boss, never by the node.

## Rebuild

Needs OpenSCAD on PATH and Python 3.

```sh
python3 tools/check_parameters.py
python3 tools/build_models.py
```

The build writes the seven STLs and `BUILD-MANIFEST.json` only after its geometry checks pass. OpenSCAD tessellation varies between runs, so a rebuild passes the same checks but does not reproduce the released mesh hashes. Renders come from the `.scad` scripts in `images/`, each of which stores its camera:

```sh
openscad --render --colorscheme Tomorrow --imgsize 1300,1000 -o images/overall.png images/overall.scad
```

## Layout

| Path | Contents |
|---|---|
| `docs/` | Print notes and validation results |
| `images/` | Renders and the `.scad` scripts that produce them |
| `audits/` | Horizontal-section audit data for both frames |
| `tools/` | Build and validation scripts |

## Limits

No aerodynamic, road-load, torque or temperature testing has been done. Check the magnets before every drive.

## License

Copyright 2026 James Rich. Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); see `LICENSE`.
