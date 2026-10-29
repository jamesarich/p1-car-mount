"""Matched actual-mesh views. Render BEFORE now; AFTER only once revised exports exist."""
import argparse, hashlib, json, subprocess, concurrent.futures, os, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ORIGINAL=ROOT/'.build-before-source'
REVISED=ROOT.parent
EXE=None
FAST_EXE=REVISED/'.tools/OpenSCAD.app/Contents/MacOS/OpenSCAD'

VIEWS={
 'n-overview':('p1-roof-mount-n-type.stl',[0,-18,15],[55,0,32],535,'full'),
 'stock-overview':('p1-roof-mount-stock.stl',[0,-18,15],[55,0,32],535,'full'),
 'top':('p1-roof-mount-n-type.stl',[0,-18,15],[0,0,0],535,'full'),
 'window':('p1-roof-mount-n-type.stl',[15,-46,15],[0,0,0],180,'full'),
 'underside':('p1-roof-mount-n-type.stl',[0,-18,15],[128,0,32],535,'full'),
 'stock-bore':('p1-roof-mount-stock.stl',[0,-118.2,65],[30,0,0],70,'pylon'),
 'n-section':('p1-roof-mount-n-type.stl',[0,-105,34],[90,0,270],220,'section'),
 'saddle-n':('p1-roof-mount-n-type.stl',[-68,-76,27],[60,0,-32],155,'full'),
 'saddle-stock':('p1-roof-mount-stock.stl',[-68,-76,27],[60,0,-32],155,'full'),
 'assembly-n':('p1-roof-mount-n-type.stl',[-12,-40,105],[65,0,-42],950,'assembly'),
 'assembly-stock':('p1-roof-mount-stock.stl',[-12,-40,105],[65,0,-42],950,'assembly'),
}

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def render(job):
    revision,name=job
    filename,pt,rot,distance,mode=VIEWS[name]
    directory=ORIGINAL if revision=='before' else REVISED
    source=directory/filename
    if revision=='after':
        manifest=json.loads((REVISED/'BUILD-MANIFEST.json').read_text())
        if manifest.get('version')!='1.1-draft':
            raise RuntimeError('AFTER rendering requires published final 1.1-draft build manifest')
        listed=manifest.get('models',{}).get(filename,{})
        if listed.get('sha256') and listed['sha256']!=digest(source):
            raise RuntimeError(f'Final manifest hash mismatch for {filename}')
    if revision=='after' and digest(source)==digest(ORIGINAL/filename):
        raise RuntimeError(f'Refusing to label original {filename} as AFTER')
    mesh=f'import({json.dumps(str(source))});'
    if mode=='section': mesh='render() intersection(){'+mesh+'translate([0,-151,-1]) cube([38,84,71]);}'
    if mode=='pylon': mesh='render() intersection(){'+mesh+'translate([-25,-145,45]) cube([50,58,28]);}'
    extra=''
    if mode=='assembly':
        stock='stock' in name
        extra=(f'use <{ORIGINAL}/p1-node-model.scad>\n'
               f'use <{REVISED}/assembly-refinements.scad>\n'
               'translate([0,11.5,10.5+59*tan(4)]) rotate([-4,0,0]) translate([0,-11.5,0]) p1_node();\n'
               'for(x=[-76,76],y=[-76,0,76]) translate([x,y,0]) magnet_foot();\n'
               + ('translate([0,-118.2,69.5]) seeed_rod();\n' if stock else 'translate([0,-124,68]) alfa_915();\n'))
        if revision=='after':
            variant='stock' if stock else 'n'
            reference=ROOT/f'coax-{variant}-display.off'
            if FAST_EXE.exists():
                crop_scad=ROOT/f'coax-{variant}-crop.scad'
                crop_scad.write_text('use <../assembly-refinements.scad>\n'
                    'ar_path_tube(ar_coax_route('+('false' if stock else 'true')+'),'+('2.9' if stock else '2.5')+');\n')
                if not reference.exists() or reference.stat().st_mtime < (REVISED/'assembly-refinements.scad').stat().st_mtime:
                    rr=subprocess.run([str(FAST_EXE),'--backend','Manifold','-o',str(reference),str(crop_scad)],capture_output=True,text=True)
                    (ROOT/f'coax-{variant}-crop.log').write_text(rr.stdout+rr.stderr)
                    if rr.returncode or 'ERROR:' in rr.stderr:raise RuntimeError(rr.stderr)
                extra+='color([0.08,0.08,0.08]) import('+json.dumps(str(reference))+');\n'
                extra+='color("gold") ar_node_plug_envelope();\n'
            else:
                extra+='ar_coax_reference(alfa='+('false' if stock else 'true')+');\n'
    scad=ROOT/f'{revision}-{name}.scad'
    scad.write_text('// Matched view; actual mesh geometry. No geometry smoothing.\n'
                    f'$vpt={pt}; $vpr={rot}; $vpd={distance};\n'
                    'color("#bbc5cd") '+mesh+'\n'+extra)
    display=scad
    crop_command=None
    if mode in ('section','pylon') and FAST_EXE.exists():
        crop=ROOT/f'{revision}-{name}-display.off'
        crop_command=[str(FAST_EXE),'--backend','Manifold','-o',str(crop),str(scad)]
        cr=subprocess.run(crop_command,capture_output=True,text=True)
        (ROOT/f'{revision}-{name}-crop.log').write_text(cr.stdout+cr.stderr)
        if cr.returncode or 'ERROR:' in cr.stderr:raise RuntimeError(cr.stderr)
        display=ROOT/f'{revision}-{name}-display.scad'
        display.write_text(f'$vpt={pt};$vpr={rot};$vpd={distance};\ncolor("#bbc5cd") import({json.dumps(str(crop))});\n')
    command=[EXE,'--preview','--projection','o','--colorscheme','Tomorrow','--imgsize','1600,1200','-o',str(scad.with_suffix('.png')),str(display)]
    result=subprocess.run(command,capture_output=True,text=True)
    (ROOT/f'{revision}-{name}.log').write_text(result.stdout+result.stderr)
    meaningful='\n'.join(line for line in result.stderr.splitlines() if line!='WARNING: Viewall and autocenter disabled in favor of $vp*')
    if result.returncode or 'ERROR:' in meaningful or 'WARNING:' in meaningful:
        raise RuntimeError(f'{revision}-{name}: {result.stderr}')
    return {'view':name,'revision':revision,'mesh':str(source),'sha256':digest(source),'command':command,'crop_command':crop_command}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('revision',choices=['before','after']);p.add_argument('--views',nargs='+',choices=list(VIEWS),default=list(VIEWS));p.add_argument('--workers',type=int,default=2)
    p.add_argument('--original',type=Path,help='Optional directory containing unmodified v1.0 meshes and node reference')
    p.add_argument('--openscad',help='PNG renderer; also accepts OPENSCAD_RENDER')
    p.add_argument('--fast-openscad',type=Path,help='Optional current Manifold build for display-only cuts; also accepts OPENSCAD')
    args=p.parse_args()
    EXE=args.openscad or os.environ.get('OPENSCAD_RENDER')
    if not EXE:
        old=Path('/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
        EXE=str(old) if old.exists() else shutil.which('openscad')
    if not EXE: p.error('Set --openscad or OPENSCAD_RENDER to an OpenSCAD executable')
    if args.original:
        ORIGINAL=args.original.resolve()
    else:
        # Use the immutable baseline, never a sibling checkout that may itself
        # contain this revision. Only display inputs are extracted from Git.
        ORIGINAL.mkdir(exist_ok=True)
        for filename in ('p1-roof-mount-n-type.stl','p1-roof-mount-stock.stl','p1-node-model.scad'):
            blob=subprocess.run(['git','show',f'9981cb696d0fd03d09503277934305a4a317377c:{filename}'],cwd=REVISED,capture_output=True,check=True)
            (ORIGINAL/filename).write_bytes(blob.stdout)
    candidate=args.fast_openscad or os.environ.get('OPENSCAD')
    if candidate: FAST_EXE=Path(shutil.which(str(candidate)) or candidate)
    jobs=[(args.revision,n) for n in args.views]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool: results=list(pool.map(render,jobs))
    record=ROOT/f'{args.revision}-render-manifest.json'
    old=json.loads(record.read_text()) if record.exists() else []
    merged={r['view']:r for r in old}
    merged.update({r['view']:r for r in results})
    record.write_text(json.dumps(list(merged.values()),indent=2))
    print(f'Rendered {len(results)} {args.revision} views')
