"""Export optional calibration shims separately; no screw stack is selected."""
from pathlib import Path
import argparse, os, shutil, subprocess, json
from normalize_export import normalize_export
from build_models import mesh_stats

root=Path(__file__).resolve().parents[1]


def find_openscad(requested=None):
    requested=requested or os.environ.get('OPENSCAD')
    if requested:
        executable=shutil.which(requested) or requested
        if not Path(executable).is_file():
            raise FileNotFoundError(f'OpenSCAD executable not found: {requested}')
        return str(Path(executable).resolve())
    candidates=[shutil.which('openscad'),
                root/'.tools/OpenSCAD.app/Contents/MacOS/OpenSCAD',
                '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD']
    executable=next((p for p in candidates if p and Path(p).is_file()),None)
    if executable is None:
        raise FileNotFoundError('OpenSCAD unavailable; pass --openscad PATH or set OPENSCAD.')
    return str(Path(executable).resolve())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--openscad',help='OpenSCAD executable; defaults to OPENSCAD, PATH, or a local application')
    args=parser.parse_args()
    try:
        scad=find_openscad(args.openscad)
    except FileNotFoundError as error:
        parser.error(str(error))
    (root/'validation').mkdir(exist_ok=True)
    results={}
    for t in [.5,1,1.5,2]:
        wrapper=root/'validation/shim-wrapper.scad'
        wrapper.write_text('use <../assembly-refinements.scad>\n'+f'ar_screw_shim({t});\n')
        target=root/f'p1-screw-shim-{str(t).replace(".","p")}mm.stl'
        r=subprocess.run([scad,'-o',str(target),str(wrapper)],capture_output=True,text=True)
        if r.returncode or 'WARNING:' in r.stderr or 'ERROR:' in r.stderr: raise RuntimeError(r.stderr)
        normalization=normalize_export(target)
        stats=mesh_stats(target)
        assert stats['components']==1 and abs(stats['size'][2]-t)<.0001
        stats['normalization']=normalization
        results[target.name]=stats
    (root/'validation/shim-exports.json').write_text(json.dumps(results,indent=2))
    print('Four optional individually valid calibration shims exported; stack remains unselected.')


if __name__=='__main__':
    main()
