"""Additional exported-mesh checks for the roof mount.

Sections and facet normals are geometric checks, not strength or slicer tests.
Hardware/tool envelopes remain provisional until measured on the actual parts.
"""
import json
import math
import subprocess


def cross_section(triangles, z, y):
    """X crossings of a horizontal slice at a fixed Y, with duplicate hits merged."""
    hits = []
    for tri in triangles:
        points = []
        for a, b in zip(tri, tri[1:] + tri[:1]):
            if a[2] <= z < b[2] or b[2] <= z < a[2]:
                t = (z - a[2]) / (b[2] - a[2])
                points.append([a[j] + t * (b[j] - a[j]) for j in range(2)])
        if len(points) != 2:
            continue
        a, b = points
        if a[1] <= y < b[1] or b[1] <= y < a[1]:
            t = (y - a[1]) / (b[1] - a[1])
            hits.append(a[0] + t * (b[0] - a[0]))
    unique = []
    for value in sorted(hits):
        if not unique or abs(value - unique[-1]) > 1e-6:
            unique.append(value)
    return unique


def radial_walls(triangles, y, minimum=4, levels=(18, 24, 30, 36, 42, 48, 54, 60)):
    """Sample the front half of the shell along rays from the connector axis."""
    results = []
    for z in levels:
        segments = []
        for tri in triangles:
            points = []
            for a, b in zip(tri, tri[1:] + tri[:1]):
                if a[2] <= z < b[2] or b[2] <= z < a[2]:
                    t = (z-a[2])/(b[2]-a[2])
                    points.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])-y))
            if len(points) == 2:
                segments.append(points)
        for angle in range(-90, 91, 15):
            s, c = math.sin(math.radians(angle)), math.cos(math.radians(angle))
            hits = []
            for points in segments:
                (u0, v0), (u1, v1) = [(x*s+q*c, x*c-q*s) for x, q in points]
                if v0 <= 0 < v1 or v1 <= 0 < v0:
                    u = u0 - v0*(u1-u0)/(v1-v0)
                    # Ignore distant frame members crossed by the same ray.
                    if 0 < u < 60:
                        hits.append(u)
            unique = []
            for u in sorted(hits):
                if not unique or u-unique[-1] > 1e-6:
                    unique.append(u)
            if len(unique) != 2:
                raise ValueError(f'Unexpected shell section at Z={z}, angle={angle}: {unique}')
            width = unique[1]-unique[0]
            if width < minimum:
                raise ValueError(f'Thin front/side pylon wall at Z={z}, angle={angle}: {width:.3f} mm')
            results.append(dict(z=z, angle=angle, radial_width_mm=width))
    return results


def surface_metrics(triangles, part, p):
    """Measure downward faces over 45 degrees from vertical, above first layers."""
    areas = {}
    for a, b, c in triangles:
        u = [b[j] - a[j] for j in range(3)]
        v = [c[j] - a[j] for j in range(3)]
        n = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        magnitude = math.sqrt(sum(q*q for q in n))
        if not magnitude or n[2]/magnitude > -math.sqrt(.5) or min(a[2], b[2], c[2]) < 1.5:
            continue
        center = [sum(q[j] for q in (a, b, c))/3 for j in range(3)]
        if part == 'coupon' or center[1] < p['fin_front']:
            region = 'pylon'
        elif part in ('rear_foot_coupon', 'rear_left_foot_coupon'):
            region = 'grip'
        elif abs(center[0]) > 50 and center[1] < -50:
            region = 'left_grip' if center[0] < 0 else 'right_grip'
        else:
            region = 'other'
        key = region + ('_horizontal' if n[2]/magnitude < -.999999 else '_sloping')
        areas[key] = areas.get(key, 0) + magnitude/2
    return areas


def validate(path, part, antenna, p, executable, temp, vertices, mesh_stats):
    triangles = [vertices[i:i+3] for i in range(0, len(vertices), 3)]
    result = {'surface_areas_mm2': surface_metrics(triangles, part, p)}

    def probe(label, solid, blocked=False):
        source = temp / 'mesh-probe.scad'
        output = temp / 'mesh-probe.stl'
        output.unlink(missing_ok=True)
        source.write_text(f'intersection() {{ import({json.dumps(path.name)}); {solid} }}\n')
        command = subprocess.run([executable, '-o', str(output), str(source)], capture_output=True, text=True)
        if 'WARNING:' in command.stderr or 'ERROR:' in command.stderr:
            raise ValueError(f'{path.name}: {label}: {command.stderr}')
        empty = 'top level object is empty' in command.stderr.lower()
        if blocked:
            if empty or command.returncode:
                raise ValueError(f'{path.name}: missing rotation stop for {label}')
            stats = mesh_stats(output)
            if stats['volume_mm3'] < .5:
                raise ValueError(f'{path.name}: negligible nominal rotation interference for {label}')
            return {'test': label, 'result': 'blocked', 'interference_mm3': stats['volume_mm3']}
        if not empty:
            raise ValueError(f'{path.name}: obstruction in {label}: {command.stderr}')
        return {'test': label, 'result': 'clear'}

    if part in ('mount', 'seat_coupon'):
        result['screw_tool_access'] = []
        # A full-height 15 mm tool envelope also encloses the representative
        # 7/16-inch-AF screw head at every rotation. Sweep along the screw axis
        # from below the bed to the bearing shoulder at each slot position.
        for screw in (-1, 1):
            for shift in (-p['screw_slot']/2, 0, p['screw_slot']/2):
                solid = (f'translate([0,{p["seat_c"][1]},{p["seat_z"]}]) rotate([{-p["tilt"]},0,0]) '
                         f'translate([0,{screw*p["insert_spacing"]/2+shift},-60]) '
                         f'cylinder(d=15,h={60-p["screw_web"]-.01},$fn=96);')
                result['screw_tool_access'].append(probe(f'screw_{screw}_shift_{shift}_tool_d15', solid))

    def root_sections(y_root, minimums):
        # These planes lie between the pylon and the rear rail.
        sections = []
        for z, minimum in minimums:
            crossings = [x for x in cross_section(triangles, z, y_root) if abs(x) < 50]
            if len(crossings) != 2 or crossings[1]-crossings[0] < minimum:
                raise ValueError(f'{path.name}: narrow/disconnected pylon root at Z={z}: {crossings}')
            sections.append(dict(z=z, y=y_root, width_mm=crossings[1]-crossings[0], minimum=minimum))
        return sections

    if antenna == 'stock' and part == 'mount':
        result['root_sections'] = root_sections(p['pylon_reach']-19, ((8, 26), (12, 22), (16, 18)))
        z = p['slot_z'] + p['slot'][1]/2
        crossings = cross_section(triangles, z, p['hole_y']-3)
        if len(crossings) != 4:
            raise ValueError(f'{path.name}: unexpected nut chamber section {crossings}')
        widths = [crossings[1]-crossings[0], crossings[3]-crossings[2]]
        if min(widths) < 4:
            raise ValueError(f'{path.name}: thin chamber cheeks: {widths}')
        result['chamber_cheek_section'] = dict(z=z, y=p['hole_y']-3, x_widths_mm=widths, minimum=4)

    if part in ('mount', 'coupon'):
        y = 0 if part == 'coupon' else p['hole_y']
        result['lower_cheek_sections'] = []
        # The stock bowl floor sits higher, so its open sections start at Z=35.
        for z in ((16, 18, 20, 25, 30, 35, 40, 45, 50, 55) if antenna == 'alfa' else (35, 40, 45, 50, 55)):
            crossings = cross_section(triangles, z, y)
            if len(crossings) != 4:
                raise ValueError(f'{path.name}: unexpected lower pylon section at Z={z}: {crossings}')
            widths = [crossings[1]-crossings[0], crossings[3]-crossings[2]]
            minimum = 4.2 if z <= 30 else 3.8
            if min(widths) < minimum:
                raise ValueError(f'{path.name}: thin pylon cheeks at Z={z}: {widths}')
            result['lower_cheek_sections'].append(dict(z=z, x_widths_mm=widths, minimum=minimum))
        result['front_and_side_wall_sections'] = radial_walls(
            triangles, y, levels=(18, 24, 30, 36, 42, 48, 54, 60) if antenna == 'alfa' else (36, 42, 48, 54, 60))

    if antenna == 'alfa' and part in ('mount', 'coupon'):
        channel_z = p['recess_channel_z']
        channel_y = y-8
        crossings = cross_section(triangles, channel_z, channel_y)
        if len(crossings) != 4:
            raise ValueError(f'{path.name}: unexpected cable-exit section {crossings}')
        opening = crossings[2] - crossings[1]
        if not p['recess_channel_w'] - .2 <= opening <= p['recess_channel_w'] + .2:
            raise ValueError(f'{path.name}: unexpected lower cable channel width {opening}')
        result['lower_channel_width_mm'] = opening
        result['lower_channel_section'] = dict(z=channel_z, y=channel_y)
        result['root_sections'] = root_sections(y+26, ((8, 34), (12, 30), (16, 24)))
        if result['surface_areas_mm2'].get('pylon_horizontal', 0) > 220:
            raise ValueError(f'{path.name}: broad flat chamber ceiling returned')
        # The clipped corner envelope is a test scenario, not a hardware spec.
        # Extra 0.2 mm diameter loss checks sensitivity to rounding/clearance.
        nut_z = p['fin_h']-p['fin_wall']-p['n_washer'][1]-p['n_nut_h']+.01
        result['rounded_nut_capture'] = []
        for corner_d in (p['n_nut_corner_d'], p['n_nut_corner_d']-.2):
            for x in (-p['bulkhead_clear'], 0, p['bulkhead_clear']):
                solid = (f'translate([{x},{y},{nut_z}]) rotate([0,0,30]) intersection() {{ '
                         f'cylinder(r={p["n_nut_af"]}/(2*cos(30)),h={p["n_nut_h"]-.02},$fn=6); '
                         f'cylinder(d={corner_d},h={p["n_nut_h"]-.02},$fn=96); }}')
                result['rounded_nut_capture'].append(probe(f'corner_d{corner_d}_offset{x}', solid, blocked=True))

    for region in ('grip', 'left_grip', 'right_grip'):
        area = sum(result['surface_areas_mm2'].get(region+suffix, 0) for suffix in ('_horizontal', '_sloping'))
        # Ignore sub-millimeter triangulation slivers.
        if area > 1:
            raise ValueError(f'{path.name}: {region} has {area:.3f} mm² of steep downward faces')
    return result
