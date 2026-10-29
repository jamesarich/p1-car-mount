#!/usr/bin/env python3
"""Render the roof-mount exports, check topology/bounds and retain build provenance.

Requires a current OpenSCAD on PATH or passed with --openscad. Writes ASCII
STLs, which keep full precision for the zero-area facet check, and only after
all renders and checks succeed.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import numpy as np
import trimesh
import manifold3d as md

from check_parameters import ROOT, SOURCE, load, main as check_parameters
from validate import validate
from normalize_export import normalize_export


def mesh_vertices(path):
    data = path.read_bytes()
    binary = len(data) >= 84 and len(data) == 84 + 50 * struct.unpack_from('<I', data, 80)[0]
    vertices = []
    if binary:
        for offset in range(84, len(data), 50):
            record = struct.unpack_from('<12fH', data, offset)
            vertices.extend(tuple(record[i:i+3]) for i in (3, 6, 9))
    else:
        vertices = [tuple(map(float, line.split()[1:])) for line in data.decode().splitlines()
                    if line.strip().startswith('vertex ')]
    return vertices


def mesh_stats(path):
    vertices = mesh_vertices(path)
    if not vertices or len(vertices) % 3:
        raise ValueError(f'{path.name}: empty or invalid STL')
    if any(not math.isfinite(x) for v in vertices for x in v):
        raise ValueError(f'{path.name}: nonfinite vertex')
    edges = Counter()
    volume = 0
    elevated_downward_flat_area = 0
    elevated_downward_flat_below_rear_foot_top = 0
    near_zero_area_triangles = 0
    for i in range(0, len(vertices), 3):
        a, b, c = vertices[i:i+3]
        cross = (b[1]*c[2]-b[2]*c[1], b[2]*c[0]-b[0]*c[2], b[0]*c[1]-b[1]*c[0])
        volume += sum(a[j]*cross[j] for j in range(3)) / 6
        u, v = [b[j]-a[j] for j in range(3)], [c[j]-a[j] for j in range(3)]
        normal = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        magnitude = math.sqrt(sum(x*x for x in normal))
        if magnitude == 0:
            raise ValueError(f'{path.name}: degenerate triangle')
        if magnitude < 1e-12:
            near_zero_area_triangles += 1
        if magnitude and -normal[2] > .999999*magnitude and min(a[2], b[2], c[2]) > 1.5:
            elevated_downward_flat_area += magnitude/2
            if max(a[2],b[2],c[2]) <= 18.001:
                elevated_downward_flat_below_rear_foot_top += magnitude/2
        for u, v in ((a, b), (b, c), (c, a)):
            if u == v:
                raise ValueError(f'{path.name}: collapsed triangle edge')
            edges[tuple(sorted((u, v)))] += 1
    bad = Counter(value for value in edges.values() if value != 2)
    if bad:
        raise ValueError(f'{path.name}: nonmanifold edge incidence {dict(bad)}')
    if volume <= 0:
        raise ValueError(f'{path.name}: nonpositive oriented volume')
    adjacency = defaultdict(set)
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    unseen, components = set(adjacency), 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            for vertex in adjacency[stack.pop()]:
                if vertex in unseen:
                    unseen.remove(vertex)
                    stack.append(vertex)
    bounds = [[min(v[j] for v in vertices) for j in range(3)],
              [max(v[j] for v in vertices) for j in range(3)]]
    return {'triangles': len(vertices)//3, 'bounds': bounds,
            'size': [bounds[1][j]-bounds[0][j] for j in range(3)],
            'volume_mm3': volume, 'components': components,
            'near_zero_area_triangles': near_zero_area_triangles,
            'elevated_downward_flat_area_mm2': elevated_downward_flat_area,
            'elevated_downward_flat_below_rear_foot_top_mm2': elevated_downward_flat_below_rear_foot_top,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--openscad', help='path to OpenSCAD executable')
    parser.add_argument('--source', type=Path, default=SOURCE, help='SCAD source; defaults to p1-roof-mount.scad')
    parser.add_argument('--blend-cache-dir', type=Path, help='Reuse fingerprint-verified native blend cache')
    parser.add_argument('--reuse-frames', type=Path, help='Reuse native frames with matching source/version fingerprint')
    args = parser.parse_args()
    source = args.source.resolve()
    check_parameters(source)
    candidates = [args.openscad, shutil.which('openscad'),
                  '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD']
    executable = next((c for c in candidates if c and Path(c).is_file()), None)
    if executable is None:
        parser.error('OpenSCAD unavailable; no STLs were generated. Install a current official build or pass --openscad PATH.')
    version_result = subprocess.run([executable, '--version'], capture_output=True, text=True, check=True)
    version = (version_result.stdout + version_result.stderr).strip()
    jobs = [('p1-roof-mount-n-type.stl', 'alfa', 'mount'),
            ('p1-coupon-pylon.stl', 'alfa', 'coupon'),
            ('p1-coupon-pylon-stock.stl', 'stock', 'coupon'),
            ('p1-coupon-front-foot.stl', 'alfa', 'foot_coupon'),
            ('p1-coupon-rear-right-foot.stl', 'alfa', 'rear_foot_coupon'),
            ('p1-roof-mount-stock.stl', 'stock', 'mount'),
            ('p1-coupon-rear-left-foot.stl', 'alfa', 'rear_left_foot_coupon'),
            ('p1-coupon-seat.stl', 'alfa', 'seat_coupon')]
    manifest = {'openscad': version, 'version': load('alfa', source)[0]['version'],
                'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (source, source.parent / 'p1-node-model.scad',
                          source.parent / 'assembly-refinements.scad',
                          source.parent / 'tools/normalize_export.py',
                          source.parent / 'tools/precision_edges.py',
                          source.parent / 'tools/validate.py',
                          Path(__file__))},
                'intersection_checks': [], 'exported_bore_checks': [],
                'exported_hardware_access_checks': [], 'exported_nut_rotation_checks': [], 'mesh_checks': {}, 'models': {}}
    with tempfile.TemporaryDirectory(prefix='.build-', dir=ROOT) as temp:
        temp = Path(temp)
        blend_caches = {}
        reusable_frames = {}
        def render(path, antenna, part, extra=()):
            if part == 'mount' and antenna in reusable_frames:
                shutil.copy2(reusable_frames[antenna],path)
                return subprocess.CompletedProcess([],0,'','')
            # Coupons crop the freshly checked frame, retaining the exact same
            # geometry without rebuilding the expensive rounded envelope.
            frame = temp/'p1-roof-mount-n-type.stl'
            if frame.exists() and part in ('foot_coupon','rear_foot_coupon','rear_left_foot_coupon','seat_coupon'):
                pp,_ = load(antenna,source)
                if part == 'seat_coupon':
                    body=f'intersection() {{ import({json.dumps(str(frame))}); translate([{ -pp["pad"][0]/2-1},{pp["seat_c"][1]-pp["pad"][1]/2-5},-1]) cube([{pp["pad"][0]+2},{pp["pad"][1]+10},{pp["fin_h"]+2}]); }}'
                else:
                    fx=-pp['foot_x'] if part=='rear_left_foot_coupon' else pp['foot_x']
                    fy=pp['foot_y'] if part=='foot_coupon' else -pp['foot_y']
                    r=pp['boss_r']
                    body=f'translate([{ -fx},{-fy},0]) intersection() {{ import({json.dumps(str(frame))}); translate([{fx-r-1},{fy-r-1},-1]) cube([{2*r+2},{2*r+2},{pp["dam_h"]+pp["max_t"]}]); }}'
                wrapper=temp/'coupon-from-frame.scad';wrapper.write_text(body)
                return subprocess.run([executable,'-o',str(path),str(wrapper)],capture_output=True,text=True)
            if part == 'audit_checks' and antenna in reusable_frames:
                # Same source-native frame, final exported boundary. Repeat all
                # collision checks with native source reference/tool geometry.
                wrapper=temp/f'assembly-audit-{antenna}.scad'
                wrapper.write_text(f'use <{source}>\n$fn=96;\n'
                    f'module tested_frame() import({json.dumps(str(reusable_frames[antenna]))});\n'
                    'intersection(){tested_frame();n_tail_clearance();}\n'
                    'intersection(){tested_frame();bulkhead_hardware();}\n'
                    'for(dy=[-3,0,3]) { intersection(){tested_frame();node_body(dy,0);} intersection(){antenna_preview();node_body(dy,0);} }\n')
                return subprocess.run([executable,'-o',str(path),'-D',f'antenna="{antenna}"',str(wrapper)],capture_output=True,text=True)
            command = [executable, '-o', str(path), '-D', f'antenna="{antenna}"',
                       '-D', f'part="{part}"', '-D', 'show_node=false',
                       *(['-D', f'blend_cache={json.dumps(str(blend_caches[antenna]))}']
                         if antenna in blend_caches else []), *extra, str(source)]
            result = subprocess.run(command, capture_output=True, text=True)
            if 'WARNING:' in result.stderr or 'ERROR:' in result.stderr:
                raise RuntimeError(result.stderr)
            return result
        # Evaluate the same expensive native blend once per antenna variant.
        # Cache is local to this build and is not substituted for editable CAD.
        manifest['native_blend_caches'] = {}
        fingerprint = hashlib.sha256(source.read_bytes() +
            (source.parent/'assembly-refinements.scad').read_bytes() + version.encode()).hexdigest()
        if args.reuse_frames:
            prior=json.loads((args.reuse_frames/'frames.json').read_text())
            if prior['source_fingerprint'] != fingerprint:
                raise ValueError('Native frame source/version mismatch')
            for antenna,name in [('alfa','p1-roof-mount-n-type.stl'),('stock','p1-roof-mount-stock.stl')]:
                saved=args.reuse_frames/name
                if hashlib.sha256(saved.read_bytes()).hexdigest()!=prior['files'][name]:
                    raise ValueError('Native frame content mismatch')
                reusable_frames[antenna]=saved.resolve()
            manifest['native_frame_reuse']=prior
        reusable = None
        if args.blend_cache_dir:
            reusable = json.loads((args.blend_cache_dir/'cache.json').read_text())
            if reusable['source_fingerprint'] != fingerprint:
                raise ValueError('Native blend cache source/version mismatch')
        for antenna in ('alfa','stock'):
            cache = temp / f'blend-{antenna}.stl'
            if reusable:
                saved = args.blend_cache_dir/cache.name
                if hashlib.sha256(saved.read_bytes()).hexdigest() != reusable['files'][cache.name]:
                    raise ValueError('Native blend cache content mismatch')
                shutil.copy2(saved,cache)
            else:
                result = render(cache, antenna, 'frame_blend')
                if result.returncode:
                    raise RuntimeError(result.stderr)
            # Native Minkowski construction contains many redundant tiny facets.
            # Bounded tessellation reduction is limited to the NEW additive blend
            # before all interface cuts; source dimensions remain unchanged.
            raw_cache_hash = hashlib.sha256(cache.read_bytes()).hexdigest()
            native = trimesh.load(cache,process=False,force='mesh')
            vertices,inverse = np.unique(native.vertices,axis=0,return_inverse=True)
            solid = md.Manifold(md.Mesh64(vertices,inverse[native.faces].astype(np.uint64)))
            reduced = solid.as_original().simplify(.001).to_mesh64()
            tessellated = trimesh.Trimesh(reduced.vert_properties[:,:3],reduced.tri_verts,process=False)
            cache.write_bytes(trimesh.exchange.stl.export_stl_ascii(tessellated).encode())
            cache_normalization = normalize_export(cache)
            blend_caches[antenna] = cache
            manifest['native_blend_caches'][antenna] = dict(
                native_sha256=raw_cache_hash,sha256=hashlib.sha256(cache.read_bytes()).hexdigest(),
                additive_blend_tessellation_tolerance_mm=.001,
                native_triangles=len(native.faces), reduced_triangles=len(tessellated.faces),
                normalization=cache_normalization)
            print(f'{antenna}: native rounded-frame blend evaluated', flush=True)
        # Intersections must render empty. OpenSCAD may exit nonzero on an empty mesh.
        checks = []
        for antenna in ('alfa', 'stock'):
            override = () if antenna == 'alfa' else ('-D', 'antenna="stock"')
            checks.append(('cable_check', override))
            checks.append(('bulkhead_check', override))
            for shift in (-3, 0, 3):
                checks.append(('check', (*override, '-D', f'check_dy={shift}', '-D', 'check_dz=0')))
                checks.append(('antenna_node_check', (*override, '-D', f'check_dy={shift}', '-D', 'check_dz=0')))
        # The source's audit_checks part unions the eight interference checks of
        # each antenna in one evaluation, reusing geometry within the process.
        # A union is empty only if every constituent intersection is empty.
        manifest['source_check_batches'] = []
        for antenna in ('alfa', 'stock'):
            result = render(temp / f'intersection-{antenna}.stl', antenna, 'audit_checks')
            if 'top level object is empty' not in result.stderr.lower():
                raise RuntimeError(f'Expected empty {antenna} audit union:\n{result.stderr}')
            manifest['source_check_batches'].append(dict(antenna=antenna, result='empty'))
        for part, extra in checks:
            manifest['intersection_checks'].append({'part': part, 'overrides': list(extra),
                'result': 'empty', 'batch': 'stock' if 'antenna="stock"' in extra else 'alfa'})
        for name, antenna, part in jobs:
            # Manifold can choose a different triangulation across runs. A
            # floating-point sliver can become exactly collinear on STL export.
            # Retry only this specific failure, never waive validation or edit
            # the mesh. Every published export must pass the same strict checks.
            for attempt in range(3):
                result = render(temp / name, antenna, part)
                if result.returncode:
                    raise RuntimeError(result.stderr)
                normalization = normalize_export(temp / name)
                try:
                    stats = mesh_stats(temp / name)
                except ValueError as error:
                    if 'degenerate triangle' not in str(error) or attempt == 2:
                        raise
                    print(f'{name}: rejected zero-area facet; re-exporting ({attempt + 1}/2)')
                else:
                    stats['render_attempts'] = attempt + 1
                    stats['export_normalization'] = normalization
                    break
            if stats['components'] != 1:
                raise ValueError(f'{name}: expected 1 component, found {stats["components"]}')
            flat_area = stats['elevated_downward_flat_area_mm2']
            if part == 'rear_left_foot_coupon':
                # The newly integrated upper tie eye is deliberately bridged/
                # supported. The original lower foot/grip remains support-free.
                flat_area = stats['elevated_downward_flat_below_rear_foot_top_mm2']
            if part in ('foot_coupon', 'rear_foot_coupon', 'rear_left_foot_coupon') and flat_area > .01:
                raise ValueError(f'{name}: unexpected elevated flat underside; inspect a pocket ceiling or capped cut')
            params, _ = load(antenna, source)
            if any(size + 2*params['brim'] + 2 > params['bed'] + .01 for size in stats['size'][:2]):
                raise ValueError(f'{name}: actual mesh plus brim/edge margin exceeds bed: {stats["size"]}')
            if stats['bounds'][0][2] < -.001:
                raise ValueError(f'{name}: geometry below build plate')
            if part in ('mount', 'coupon'):
                # Inspect the exported mesh independently of the source CSG.
                # A near-full-diameter gauge must traverse roof into chamber.
                y = 0 if part == 'coupon' else params['hole_y']
                top = params['fin_h']
                depth = params['n_thread'] if antenna == 'alfa' else params['fin_wall'] + params['slot'][1]
                diameter = params['sma_d'] - .05
                # Stock has an off-center D-flat; test that shape, not a circle
                # whose radius would incorrectly cross the intentional flat.
                gauge = f'cylinder(d={diameter}, h={depth+1}, $fn=96);'
                if antenna == 'stock':
                    gauge = (f'linear_extrude({depth+1}) intersection() {{ circle(d={diameter}, $fn=96); '
                             f'translate([{-params["sma_d"]}, {-params["sma_d"]/2+.025}]) '
                             f'square([{2*params["sma_d"]}, {params["sma_flat"]-.05}]); }}')
                probe = temp / 'exported-bore-probe.scad'
                probe.write_text('intersection() {\n'
                    f'  import({json.dumps(name)});\n'
                    f'  translate([0, {y}, {top-depth}]) {gauge}\n'
                    '}\n')
                result = subprocess.run([executable, '-o', str(temp / 'exported-bore-probe.stl'), str(probe)],
                                        capture_output=True, text=True)
                if ('WARNING:' in result.stderr or 'ERROR:' in result.stderr or
                        'top level object is empty' not in result.stderr.lower()):
                    raise ValueError(f'{name}: exported antenna passage obstructed:\n{result.stderr}')
                manifest['exported_bore_checks'].append(dict(file=name, gauge_diameter=diameter, gauge_shape='round' if antenna == 'alfa' else 'D-flat',
                                                            z_from=top-depth, z_to=top+1, result='empty'))
                # Sweep solid hardware envelopes through the exported mesh.
                # N-type: nut enters below the shank, then rises into its hex
                # seat; washer follows the same lower entrance and rises through
                # the round relief inside the hex pocket. Stock: the jack's hex
                # body, both washers loose on it and the ferrule below enter the
                # chamber and rise into the round pocket under the roof.
                dz = params['fin_h'] - top
                rear_y = y - params['fin_top_l'] - 5
                def sweep(shape, start, end):
                    return f'hull() {{ translate({start}) {shape} translate({end}) {shape} }}'
                if antenna == 'alfa':
                    entry_z = params['fin_h'] - params['n_thread'] - params['n_nut_h'] - 6 - dz
                    nut_z = top - params['fin_wall'] - params['n_washer'][1] - params['n_nut_h']
                    washer_z = top - params['fin_wall'] - params['n_washer'][1] - .01
                    nut = f'cylinder(r={params["n_nut_af"]}/(2*cos(30)), h={params["n_nut_h"]}, $fn=6);'
                    washer = f'cylinder(d={params["n_washer"][0]}, h={params["n_washer"][1]}, $fn=96);'
                    paths = {
                        'nut_rear_entry_and_lift': sweep(nut, [0, rear_y, entry_z], [0, y, entry_z]) +
                            sweep(nut, [0, y, entry_z], [0, y, nut_z]),
                        'washer_rear_entry_and_lift': sweep(washer, [0, rear_y, entry_z], [0, y, entry_z]) +
                            sweep(washer, [0, y, entry_z], [0, y, washer_z]),
                    }
                else:
                    # The body enters under the arched crown, below the chamber's
                    # widest station, and only then rises on the axis.
                    entry_z = params['slot_z'] - 4 - dz
                    body_z = top - params['fin_wall'] - params['s_stack_free'] - params['s_body_h'] - .01
                    body = (f'union() {{ cylinder(r={params["s_body_af"]}/(2*cos(30)), h={params["s_body_h"]}, $fn=6); '
                            f'translate([0,0,{params["s_body_h"]}]) cylinder(d={params["s_flat_washer"][0]}, h={params["s_flat_washer"][1]}, $fn=96); '
                            f'translate([0,0,{params["s_body_h"] + params["s_flat_washer"][1]}]) cylinder(d={params["s_washer"][0]}, h={params["s_washer"][1]}, $fn=96); '
                            f'translate([0,0,{-params["s_ferrule_h"]}]) cylinder(d={params["s_ferrule_d"]}, h={params["s_ferrule_h"]}, $fn=48); }}')
                    paths = {
                        'body_rear_entry_and_lift': sweep(body, [0, rear_y, entry_z], [0, y, entry_z]) +
                            sweep(body, [0, y, entry_z], [0, y, body_z]),
                    }
                for label, path in paths.items():
                    probe = temp / 'exported-hardware-access.scad'
                    probe.write_text(f'intersection() {{ import({json.dumps(name)}); union() {{ {path} }} }}\n')
                    result = subprocess.run([executable, '-o', str(temp / 'exported-hardware-access.stl'), str(probe)],
                                            capture_output=True, text=True)
                    if ('WARNING:' in result.stderr or 'ERROR:' in result.stderr or
                            'top level object is empty' not in result.stderr.lower()):
                        raise ValueError(f'{name}: {label} obstructed:\n{result.stderr}')
                    manifest['exported_hardware_access_checks'].append(dict(file=name, path=label, result='empty'))
                if antenna == 'alfa':
                    # The round washer relief must not turn the trap into a
                    # free-spinning socket. A seated hex rotated halfway to
                    # the next alignment must intersect the remaining walls.
                    # Stock has no trapped hex: its round pocket is keyed by the D-flat bore.
                    probe = temp / 'exported-nut-rotation.scad'
                    probe.write_text(f'intersection() {{ import({json.dumps(name)}); '
                                     f'translate({[0, y, nut_z]}) rotate([0,0,30]) {nut} }}\n')
                    result = subprocess.run([executable, '-o', str(temp / 'exported-nut-rotation.stl'), str(probe)],
                                            capture_output=True, text=True)
                    if result.returncode or 'WARNING:' in result.stderr or 'ERROR:' in result.stderr:
                        raise ValueError(f'{name}: nut rotation stop missing:\n{result.stderr}')
                    blocked = mesh_stats(temp / 'exported-nut-rotation.stl')
                    if blocked['volume_mm3'] < 1:
                        raise ValueError(f'{name}: insufficient nominal nut rotation interference')
                    manifest['exported_nut_rotation_checks'].append(dict(file=name, angle_degrees=30,
                        interference_mm3=blocked['volume_mm3'], result='blocked'))
            if part == 'mount':
                shutil.copy2(temp/name,ROOT/'validation'/('last-'+name))
            manifest['mesh_checks'][name] = validate(temp / name, part, antenna, params, executable, temp, mesh_vertices(temp / name), mesh_stats)
            manifest['models'][name] = dict(antenna=antenna, part=part, **stats)
            print(f'{name}: {stats["triangles"]} triangles, size {stats["size"]}')
        for name, _, _ in jobs:
            shutil.copy2(temp / name, ROOT / name)
        (ROOT / 'BUILD-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Exports passed edge topology, bounds and nominal intersection checks. Inspect supports and print the coupon before the frame.')


if __name__ == '__main__':
    main()
