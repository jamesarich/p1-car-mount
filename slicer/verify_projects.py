"""Verify current A1 deliveries without scratch profiles or standalone G-code.

Embedded toolpath hashes are compared with retained metadata-fix evidence.
Positive support extrusion is a sanity check, not bridge/support qualification.
"""
import json, zipfile, hashlib, re
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import cKDTree

root = Path(__file__).resolve().parent
repo = root.parent
results = {}
evidence = json.loads((repo / 'validation/cantilever-reopen/metadata-fix.json').read_text())


def support_moves(gcode):
    """Count positive-E support XY moves, respecting extrusion coordinate mode."""
    counts = Counter()
    feature = ''
    relative_e = True
    last_e = 0.0
    words = re.compile(r'([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))')
    for line in gcode.decode('utf-8').splitlines():
        if line.startswith('; FEATURE:'):
            feature = line.split(':', 1)[1].strip()
        code = line.split(';', 1)[0].strip()
        if not code:
            continue
        cmd = code.split()[0]
        values = {k: float(v) for k, v in words.findall(code)}
        if cmd == 'M82':
            relative_e = False
        elif cmd == 'M83':
            relative_e = True
        elif cmd == 'G92' and 'E' in values:
            last_e = values['E']
        elif cmd in ('G0', 'G1', 'G2', 'G3') and 'E' in values:
            delta_e = values['E'] if relative_e else values['E'] - last_e
            last_e = last_e + values['E'] if relative_e else values['E']
            if (delta_e > 0 and ('X' in values or 'Y' in values)
                    and feature.startswith('Support')):
                counts[feature] += 1
    return dict(counts)


for variant, original in [('n-type','p1-roof-mount-n-type.stl'), ('stock','p1-roof-mount-stock.stl')]:
    file = root / variant / ('p1-v11-' + variant + '-A1-supported.3mf')
    with zipfile.ZipFile(file) as z:
        assert z.testzip() is None
        settings = json.loads(z.read('Metadata/project_settings.config'))
        name = next(n for n in z.namelist() if n.startswith('3D/Objects/') and n.endswith('.model'))
        xml = ET.fromstring(z.read(name))
        vertices = np.array([[float(v.attrib[c]) for c in ('x','y','z')] for v in xml.iter() if v.tag.endswith('}vertex')])
        faces = np.array([[int(t.attrib[c]) for c in ('v1','v2','v3')] for t in xml.iter() if t.tag.endswith('}triangle')])
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        source = trimesh.load(repo / original, process=False)
        assert mesh.is_volume
        # Stock's stricter area check is retained. N-type's geometry is unchanged
        # from its earlier export; this check does not imply a fresh area audit.
        if variant=='stock':
            assert np.all(mesh.area_faces>0)
        assert len(mesh.faces)==len(source.faces)
        a = vertices - mesh.bounds.mean(axis=0)
        b = source.vertices - source.bounds.mean(axis=0)
        max_gap = max(cKDTree(a).query(b)[0].max(), cKDTree(b).query(a)[0].max())
        gcode = z.read('Metadata/plate_1.gcode')
        gcode_sha256 = hashlib.sha256(gcode).hexdigest()
        toolpaths_match = gcode_sha256 == evidence[variant]['gcode_sha256']
        support_extrusions = support_moves(gcode)
        assert support_extrusions.get('Support', 0) > 0
        assert support_extrusions.get('Support interface', 0) > 0
        source_volume = float(source.volume)
        assert source_volume > 0
        relative_volume_delta = abs(float(mesh.volume) - source_volume) / source_volume
        assert relative_volume_delta < 1e-6
        result = dict(project=str(file.relative_to(repo)),
                      size_mm=mesh.extents.tolist(), triangles=len(faces),
                      source_volume_mm3=source_volume,
                      imported_volume_mm3=float(mesh.volume),
                      relative_volume_delta=relative_volume_delta,
                      vertex_set_max_gap_mm=float(max_gap),
                      embedded_gcode_sha256=gcode_sha256,
                      toolpath_hash_matches_retained_evidence=toolpaths_match,
                      positive_support_extrusion_moves=support_extrusions,
                      support_check_scope='Positive extrusion only; not exhaustive bridge anchoring or physical print acceptance',
                      settings={k:settings.get(k) for k in ['printer_model','printer_settings_id','nozzle_diameter','curr_bed_type','filament_settings_id','filament_type','wall_loops','layer_height','sparse_infill_density','brim_width','enable_support','support_type','support_on_build_plate_only','internal_solid_infill_line_width','detect_floating_vertical_shell','vertical_shell_speed','bottom_shell_layers','top_shell_layers','bottom_shell_thickness','top_shell_thickness']},
                      slice_metadata_present='Metadata/slice_info.config' in z.namelist(),
                      sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        assert np.allclose(mesh.extents, source.extents, atol=.0001)
        assert max_gap < .0001 and toolpaths_match
        assert settings['printer_model'] == 'Bambu Lab A1'
        assert settings['nozzle_diameter'] == ['0.4']
        assert settings['curr_bed_type'] == 'Textured PEI Plate'
        assert settings['filament_type'] == ['PETG']
        assert settings['enable_support'] == '1'
        assert settings['support_type'] == 'normal(auto)'
        assert settings['support_on_build_plate_only'] == '0'
        assert settings['wall_loops'] == '6'
        assert settings['sparse_infill_density'] == '40%'
        assert settings['bottom_shell_layers'] == '6' and settings['top_shell_layers'] == '6'
        retained = settings['different_settings_to_system'][0].split(';')
        assert {'enable_support', 'wall_loops', 'sparse_infill_density'} <= set(retained)
        expected_width=.42
        assert abs(float(settings['internal_solid_infill_line_width'])-expected_width)<1e-9
        assert settings['detect_floating_vertical_shell']==('0' if variant=='stock' else '1')
        if variant=='stock':
            assert settings['vertical_shell_speed']==['50']
            assert {'detect_floating_vertical_shell', 'vertical_shell_speed'} <= set(retained)
        assert float(settings['bottom_shell_thickness'])==1.2 and float(settings['top_shell_thickness'])==1.2
        results[variant] = result
(root / 'project-verification.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
