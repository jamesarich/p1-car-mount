"""Extract the delivered embedded toolpaths for optional local path analysis."""
from pathlib import Path
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    for variant in ('stock', 'n-type'):
        folder = root / 'slicer' / variant
        project = folder / f'p1-v11-{variant}-A1-supported.3mf'
        with zipfile.ZipFile(project) as archive:
            data = archive.read('Metadata/plate_1.gcode')
        target = folder / 'plate_1.gcode'
        target.write_bytes(data)
        print(f'Extracted {variant} toolpaths to {target.relative_to(root)}')


if __name__ == '__main__':
    main()
