#!/usr/bin/env python3
"""Measure 0.2 mm mesh sections; this is not a slicer or support generator.

Run with Python, numpy and shapely. build_area assembles closed linework with
holes: https://shapely.readthedocs.io/en/stable/reference/shapely.build_area.html
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import MultiLineString, box

from build_models import mesh_vertices, mesh_stats


def sections(path, step=.2):
    vertices = np.asarray(mesh_vertices(path), dtype=float).reshape(-1, 3, 3)
    lo, hi = vertices[:, :, 2].min(axis=1), vertices[:, :, 2].max(axis=1)
    for z in np.arange(step/2, float(hi.max()), step):
        triangles = vertices[(lo <= z) & (hi > z)]
        segments = []
        for triangle in triangles:
            points = []
            for a, b in zip(triangle, np.roll(triangle, -1, axis=0)):
                if a[2] <= z < b[2] or b[2] <= z < a[2]:
                    t = (z-a[2])/(b[2]-a[2])
                    points.append(np.round(a[:2] + t*(b[:2]-a[:2]), 5))
            if len(points) == 2 and np.linalg.norm(points[0]-points[1]) > 1e-7:
                segments.append(points)
        lines = MultiLineString(segments)
        # Adjacent triangles can land on opposite sides of a rounding tie.
        # Weld at 0.1 micron, then node the linework before building its area.
        # The independent volume comparison catches missing/open contours.
        lines = shapely.unary_union(shapely.snap(lines, lines, .0001))
        shape = shapely.build_area(lines)
        if not shape.is_valid or shape.is_empty:
            raise ValueError(f'{path}: invalid or empty section at Z={z}')
        yield float(z), shape


def polygons(shape):
    if shape.geom_type == 'Polygon':
        return [shape]
    return [p for p in shape.geoms if p.geom_type == 'Polygon']


def audit(path):
    previous = None
    islands, rows = [], []
    regions = {'front_dam': box(-61, 64, 61, 104),
               'pylon_and_root': box(-50, -150, 50, -78)}
    volume = 0
    for z, shape in sections(path):
        row = {'z': round(z, 3), 'area_mm2': shape.area,
               'components': len(polygons(shape))}
        volume += shape.area*.2
        if previous is not None:
            # Only entirely new polygons are islands; overhanging material
            # attached to an existing wall is a separate bridging concern.
            for p in polygons(shape):
                if p.area > .01 and p.intersection(previous.buffer(.01)).area < .001:
                    islands.append({'z': round(z, 3), 'area_mm2': p.area,
                                    'bounds': list(p.bounds)})
            overhang = shape.difference(previous.buffer(.2))
            row['beyond_45_degree_layer_growth_mm2'] = overhang.area
            for name, region in regions.items():
                row[name + '_growth_mm2'] = overhang.intersection(region).area
        rows.append(row)
        previous = shape
    stats = mesh_stats(path)
    error = abs(volume-stats['volume_mm3'])/stats['volume_mm3']
    if error > .005:
        raise ValueError(f'{path}: section volume disagrees with mesh by {error:.2%}')
    return {
        'file': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'step_mm': .2, 'section_count': len(rows), 'floating_islands': islands,
        'integrated_section_volume_mm3': volume, 'mesh_volume_mm3': stats['volume_mm3'],
        'volume_relative_error': error,
        'peak_layer_growth_by_region': {
            name: max((r for r in rows if name+'_growth_mm2' in r),
                      key=lambda r: r[name+'_growth_mm2'])
            for name in regions},
        'sections': rows,
        'limitations': 'Geometry sections only. No extrusion widths, support toolpaths, '
                        'bridge direction, thermal deformation or material strength modeled.'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mesh', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.mesh)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'sections'}, indent=2))
    if result['floating_islands']:
        raise SystemExit('Floating sections found: review the recorded geometry.')
