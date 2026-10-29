> **Historical v1.0 notes.** Measurements and physical-print statements below refer to the original geometry at `9981cb6`, not the proposed v1.1 refinements. The v1.1 revision is unprinted and includes an additional stock-pylon coupon. Use [v1.1 revision notes](REVISION-1.1.md), the [current review](../COMPARISON.html) and [reproduction guide](REVIEW-REPRODUCTION.md) for current exports, checks and limitations.

# Validation

Version `1.0`, built with `OpenSCAD version 2026.10.11`. Values refer to the published meshes recorded in `BUILD-MANIFEST.json`.

## Measurements

| Measurement | N-type frame | Stock frame |
|---|---:|---:|
| Pylon root width at Y=−98, Z=8/12/16 | 39.910 / 34.285 / 28.358 mm | 30.119 / 26.376 / 22.357 mm |
| Root width minimums enforced | 34 / 30 / 24 mm | 26 / 22 / 18 mm |
| Minimum sampled radial front/side wall | 4.489 mm | 5.290 mm |
| Minimum recess cheek, transverse sections | 4.49 mm (4.2 mm enforced to Z=30, 3.8 mm above) | 5.27 mm (3.8 mm enforced, Z=35 to 55) |
| Chamber cheeks at Y=hole−3, mid-height | n/a | 6.040 mm each |
| Lower cable channel at Y=−132, Z=12 | 9.993 mm | n/a |
| Pylon horizontal downward area | 147.519 mm² | 69.682 mm² |
| Other pylon downward slopes over 45° from vertical | 172.996 mm² | 51.718 mm² |
| Envelope | 200 × 241.5 × 68 mm | 200 × 231.6 × 68 mm |
| Solid mesh volume | 399.472 cm³ | 382.192 cm³ |

Radial wall samples cover angles −90° through +90° in 15° steps around the connector axis, toward the front half of each pylon, at Z=18 to 60 mm in 6 mm steps (N-type) or Z=36 to 60 mm (stock, whose bowl floor is higher). They are not a global minimum-thickness or strength calculation. Root widths exclude the distant magnet feet.

Both pylons need selective support under their crowns and chambers; the small horizontal ledge areas do not make them support-free. Solid mesh volume is not slicer filament usage.

## Completed checks

- 25 scalar assertions for each antenna configuration, plus OpenSCAD's source-rendered assertions.
- 16 source interference checks, grouped into two empty unions of eight per antenna. Each covers cable bend, connector stack, node travel at −3/0/+3 mm and antenna/node clearance. Union cannot cancel interference.
- 3 exported bore probes; 5 rear entry-and-lift sweeps: N-type nut and washer on the frame and coupon, and the stock jack body with both washers and its ferrule.
- 18 Ø15 mm screw/tool access sweeps at both slots' −3/0/+3 mm positions.
- 2 nominal nut rotation stops and 12 rounded-corner sensitivity checks.
- 273 radial front/side wall checks (208 N-type, 65 stock), each requiring at least 4 mm; nine root-section checks across both pylons; 25 transverse pylon sections (20 N-type, 5 stock), two lower-channel gauges and one stock chamber-cheek section.
- Both rear grips checked for excessive downward overhang, with separate strict horizontal-underside checks on all foot coupons.
- 7 meshes pass finite vertices, no zero-area triangles, two incident faces per edge, positive oriented volume, one connected component, bed bounds and no geometry below the build plane.
- 680 horizontal sections across the two frames at 0.2 mm spacing: no entirely floating material islands. Section-integrated volume agrees with mesh volume within 0.0011% (N-type) and 0.0003% (stock), which rules out missing or open section contours.

## Exports

| File | Dimensions, mm |
|---|---|
| `p1-roof-mount-n-type.stl` | 200.000 × 241.500 × 68.000 |
| `p1-roof-mount-stock.stl` | 200.000 × 231.600 × 68.000 |
| `p1-coupon-pylon.stl` | 53.434 × 61.953 × 68.000 |
| `p1-coupon-seat.stl` | 44.000 × 80.000 × 16.650 |
| `p1-coupon-front-foot.stl` | 49.000 × 49.000 × 24.000 |
| `p1-coupon-rear-right-foot.stl` | 49.000 × 49.000 × 18.000 |
| `p1-coupon-rear-left-foot.stl` | 49.000 × 49.000 × 18.000 |

## Physical and printing limits

An N-type pylon of this geometry has been printed and assembled and works; the stock pylon has not been printed. No sliced toolpath, torque, fatigue, temperature or road-load test is claimed. N-type hardware dimensions are provisional and the stock pigtail is photo-measured. Confirm the actual nut corners, washers, thread length, cable ends, socket and magnet studs with the coupons. The main assembly is one printed frame; coupons are optional test pieces.

Support the rounded pylon crown and flat washer/nut shoulders as indicated by the slicer, and support or bridge the node-screw ceilings. Remove pylon supports through the wide upper opening. The cable's final route to the node is not fully modeled. No aerodynamic performance is inferred from the swept shape.

## Reproducing the section audit

```sh
uv run --no-project --with-requirements audits/requirements.txt python tools/audit_layers.py p1-roof-mount-n-type.stl --out audits/layers-n-type.json
uv run --no-project --with-requirements audits/requirements.txt python tools/audit_layers.py p1-roof-mount-stock.stl --out audits/layers-stock.json
```

The section audit is not a slicer. Each output records the SHA-256 of the mesh it measured.
