"""Preserve the frozen sliced configuration when Bambu's GUI loads a project.

Bambu 02.08.02.61 replaces values absent from different_settings_to_system
with the named installed preset's values. CLI exports incorrectly marked these
custom projects with three empty difference strings. Retain actual differences
from a GUI-normalized system-default snapshot; each preset collection selects
its own option keys. The snapshot was saved before any custom profile changes,
apart from enable_support, which is explicitly restored to its default of zero.
This changes only import metadata, never geometry, actual settings, or G-code.
"""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'different_settings_to_system', 'inherits', 'inherits_group',
           'print_settings_id', 'filament_settings_id', 'printer_settings_id'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    results = {}
    baseline_path = ROOT / 'validation' / 'cantilever-reopen' / 'gui-system-defaults.json'
    baseline = json.loads(baseline_path.read_text())
    for variant in ('stock', 'n-type'):
        folder = ROOT / 'slicer' / variant
        source = folder / f'p1-v11-{variant}-A1-fit-prototype.3mf'
        target = folder / f'p1-v11-{variant}-A1-supported.3mf'
        with zipfile.ZipFile(source) as zin:
            settings = json.loads(zin.read('Metadata/project_settings.config'))
            retained_keys = sorted(k for k, v in settings.items()
                                   if k not in IGNORED and baseline.get(k) != v)
            assert not any('gcode' in k for k in retained_keys)
            retained = ';'.join(retained_keys)
            nfilaments = len(settings['filament_settings_id'])
            settings['different_settings_to_system'] = [retained] * (nfilaments + 2)
            with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zout:
                for entry in zin.infolist():
                    data = zin.read(entry.filename)
                    if entry.filename == 'Metadata/project_settings.config':
                        data = (json.dumps(settings, indent=2) + '\n').encode()
                    zout.writestr(entry, data)
        with zipfile.ZipFile(source) as a, zipfile.ZipFile(target) as b:
            assert a.namelist() == b.namelist()
            changed = [n for n in a.namelist() if a.read(n) != b.read(n)]
            assert changed == ['Metadata/project_settings.config']
            old = json.loads(a.read(changed[0]))
            new = json.loads(b.read(changed[0]))
            assert [k for k in new if old.get(k) != new[k]] == ['different_settings_to_system']
            assert new['enable_support'] == '1'
            assert new['wall_loops'] == '6'
            assert new['sparse_infill_density'] == '40%'
            assert new['support_type'] == 'normal(auto)'
            results[variant] = {
                'source': str(source.relative_to(ROOT)),
                'delivered': str(target.relative_to(ROOT)),
                'source_sha256': digest(source.read_bytes()),
                'delivered_sha256': digest(target.read_bytes()),
                'changed_entries': changed,
                'changed_setting': 'different_settings_to_system',
                'retained_override_keys_per_preset': len(retained.split(';')),
                'retained_override_keys': retained_keys,
                'gui_system_default_snapshot_sha256': digest(baseline_path.read_bytes()),
                'gcode_sha256': digest(b.read('Metadata/plate_1.gcode')),
                'geometry_settings_and_gcode_unchanged': True,
                'zip_crc_pass': b.testzip() is None,
            }
    report = ROOT / 'validation' / 'cantilever-reopen' / 'metadata-fix.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
