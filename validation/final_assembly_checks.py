#!/usr/bin/env python3
"""Guarded checks against published v1.1 frame exports, never stale v1.0 meshes.

--prepare exports small reference assets without evaluating the main frame CSG.
Run again without --prepare after the final build publishes its manifest.
Requires numpy, trimesh, manifold3d. Select OpenSCAD with --openscad or OPENSCAD;
otherwise search PATH, the local snapshot, and the standard macOS application.
"""
import argparse, ast, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as md

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from check_parameters import load
ASSETS=ROOT/'validation/assembly-assets'
SCAD=None
HELPER=ROOT/'assembly-refinements.scad'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def find_openscad(requested=None):
    requested=requested or os.environ.get('OPENSCAD')
    if requested:
        executable=shutil.which(requested) or requested
        if not Path(executable).is_file():
            raise FileNotFoundError(f'OpenSCAD executable not found: {requested}')
        return str(Path(executable).resolve())
    candidates=[shutil.which('openscad'),
                ROOT/'.tools/OpenSCAD.app/Contents/MacOS/OpenSCAD',
                '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD']
    executable=next((p for p in candidates if p and Path(p).is_file()),None)
    if executable is None:
        raise FileNotFoundError('OpenSCAD unavailable; pass --openscad PATH or set OPENSCAD.')
    return str(Path(executable).resolve())

def export(name,source):
    executable=find_openscad(SCAD)
    file=ASSETS/(name+'.scad'); target=file.with_suffix('.stl')
    file.write_text(source)
    job=subprocess.run([executable,'--backend','Manifold','--export-format','asciistl',
                        '-o',str(target),str(file)],capture_output=True,text=True)
    log=job.stdout+job.stderr
    file.with_suffix('.log').write_text(log)
    assert job.returncode==0 and 'ERROR:' not in log,(name,log)
    return target,log

def prepare():
    ASSETS.mkdir(exist_ok=True)
    meta={'helper_sha256':sha(HELPER),'main_sha256':sha(ROOT/'p1-roof-mount.scad'),'variants':{}}
    head=f'use <{HELPER}>\n'
    for label,antenna,alfa in [('n-type','alfa',True),('stock','stock',False)]:
        p,_=load(antenna,ROOT/'p1-roof-mount.scad')
        args=f'{str(alfa).lower()},{p["hole_y"]},{p["fin_h"]},{p["drop_z"]},{p["drop_straight"]},{p["bend_r"]},{p["seat_z"]},{p["tilt"]},{p["insert_offset"]}'
        pts=f'ar_coax_route({args})'
        _,log=export(label+'-cable-keepout',head+f'points={pts}; echo(points); ar_path_tube(points,{p["free_cable_d"]+2*p["cable_clear"]},32);')
        # Independent tolerance probe for the normalized float32 boundary.
        # Raw exact-1mm intersections remain recorded separately, never hidden.
        export(label+'-cable-keepout-tolerance',head+f'ar_path_tube({pts},{p["free_cable_d"]+2*(p["cable_clear"]-.0001)},32);')
        points=np.array(ast.literal_eval(next(line[6:] for line in log.splitlines() if line.startswith('ECHO: [['))))
        ix=int(np.argmin(np.abs(points[:,1]-(-86 if alfa else -65))))
        center=points[ix]; tangent=points[ix+1]-points[ix-1]
        angle=float(np.degrees(np.arctan2(tangent[1],tangent[0]))-90)
        meta['variants'][label]={'center_mm':center.tolist(),'saddle_angle_deg':angle,
                                 'antenna':antenna,'keepout_diameter_mm':p['free_cable_d']+2*p['cable_clear']}
        export(label+'-cable-physical',head+f'ar_path_tube({pts},{p["free_cable_d"]},32);')
        export(label+'-tie-sweep',f'translate({center.tolist()}) rotate([0,0,{angle}]) translate([0,0,-6.5]) cube([40,2.5,1.5],center=true);')
        export(label+'-node-plug',head+f'ar_node_plug_envelope({p["seat_z"]},{p["tilt"]},{p["insert_offset"]},false);')
        export(label+'-node-tool',head+f'ar_node_plug_envelope({p["seat_z"]},{p["tilt"]},{p["insert_offset"]},true);')
        # Candidate thin spanner at outboard portion of the nominal 10 mm hex.
        # An assumed envelope, not a measured supplied tool or a tool recommendation.
        export(label+'-thin-wrench',head+
               f'q=ar_node_port({p["seat_z"]},{p["tilt"]},{p["insert_offset"]}); '
               'translate([-71.5,q[1],q[2]]) union() {'
               'rotate([0,90,0]) cylinder(d=15,h=2.5,$fn=96); '
               'translate([0,-35,-3]) cube([2.5,35,6]); }')
        for dy in [-3,0,3]:
            # Same conservative body envelope as the source audit, without frame CSG.
            source=(f'translate([0,{p["insert_offset"]},{p["seat_z"]}]) rotate([-{p["tilt"]},0,0]) translate([0,{-p["insert_offset"]+dy},0]) union() {{ '
                    f'translate([{-p["box_w"]/2},{-p["box_l"]/2},0]) cube([{p["box_w"]},{p["box_l"]},60]); '
                    f'translate([{-p["case_w"]/2},{-p["case_l"]/2},{p["box_h"]}]) cube([{p["case_w"]},{p["case_l"]},60]); }}')
            export(label+f'-node-envelope-{dy}',source)
        export(label+'-node-reference',f'use <{ROOT/"p1-node-model.scad"}>\ntranslate([0,{p["insert_offset"]},{p["seat_z"]}]) rotate([-{p["tilt"]},0,0]) translate([0,{-p["insert_offset"]},0]) p1_node();')
    (ASSETS/'meta.json').write_text(json.dumps(meta,indent=2))
    return meta

def solid(file):
    mesh=trimesh.load(file,force='mesh',process=False)
    v,inv=np.unique(mesh.vertices,axis=0,return_inverse=True)
    faces=inv[mesh.faces]
    body=md.Manifold(md.Mesh64(v.astype(np.float64),faces.astype(np.uint64)))
    assert body.status()==md.Error.NoError,(str(file),str(body.status()))
    return body,trimesh.Trimesh(v,faces,process=False)

def boolean(a,b):
    intersection=a^b
    assert intersection.status()==md.Error.NoError,str(intersection.status())
    vol=float(intersection.volume())
    return {'intersection_volume_mm3':vol,'triangles':int(intersection.num_tri()),
            'status':'pass' if vol<1e-6 else 'fail','scope':'Nominal modeled envelopes; no tolerance or physical qualification'}

def vertical_hits(mesh,xy):
    tri=mesh.triangles
    candidates=tri[np.all(tri[:,:,:2].min(axis=1)-1e-8<=xy,axis=1)&np.all(tri[:,:,:2].max(axis=1)+1e-8>=xy,axis=1)]
    a,b,c=candidates[:,0],candidates[:,1],candidates[:,2]
    ab=b[:,:2]-a[:,:2];ac=c[:,:2]-a[:,:2];q=xy-a[:,:2]
    den=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0]
    good=np.abs(den)>1e-12
    den=den[good];a=a[good];b=b[good];c=c[good];ab=ab[good];ac=ac[good];q=q[good]
    u=(q[:,0]*ac[:,1]-q[:,1]*ac[:,0])/den
    v=(ab[:,0]*q[:,1]-ab[:,1]*q[:,0])/den
    inside=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)
    z=a[:,2]+u*(b[:,2]-a[:,2])+v*(c[:,2]-a[:,2])
    return np.unique(np.round(z[inside],6))

def main():
    global SCAD
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--openscad',help='OpenSCAD executable; defaults to OPENSCAD, PATH, or a local application')
    args=parser.parse_args()
    SCAD=args.openscad
    if args.prepare:
        prepare();print('Prepared cable, tie, plug, tool and node references without main CSG.');return
    manifest=json.loads((ROOT/'BUILD-MANIFEST.json').read_text())
    assert manifest['version'].startswith('1.1'), 'Final v1.1 exports have not been published; refusing stale geometry'
    for name in ['p1-roof-mount.scad','assembly-refinements.scad']:
        assert manifest['source_sha256'][name]==sha(ROOT/name), 'Manifest source mismatch: '+name
    meta=json.loads((ASSETS/'meta.json').read_text()) if (ASSETS/'meta.json').exists() else prepare()
    if meta['helper_sha256']!=sha(HELPER) or meta['main_sha256']!=sha(ROOT/'p1-roof-mount.scad'):meta=prepare()
    results={'version':manifest['version'],'scope':'Published final exported frame geometry at recorded hashes; nominal reference hardware.',
             'physical_testing':'not checked','catalog_300mm_cable_datum':'not checked','variants':{}}
    for label,info in meta['variants'].items():
        file=ROOT/f'p1-roof-mount-{label}.stl'
        assert manifest['models'][file.name]['sha256']==sha(file), 'Final mesh hash mismatch'
        frame,mesh=solid(file)
        bodies={name:solid(ASSETS/(label+'-'+name+'.stl'))[0]
                for name in ['cable-physical','cable-keepout','cable-keepout-tolerance','tie-sweep','node-plug','node-tool','thin-wrench','node-reference','node-envelope--3','node-envelope-0','node-envelope-3']}
        row={'sha256':sha(file),'size_mm':mesh.extents.tolist(),
             'physical_cable_vs_frame':boolean(frame,bodies['cable-physical']),
             'cable_1mm_radial_keepout_vs_frame':boolean(frame,bodies['cable-keepout']),
             'cable_0p9999mm_radial_keepout_vs_frame':boolean(frame,bodies['cable-keepout-tolerance']),
             'clearance_tolerance_scope':'Exact 1mm raw result retained; 0.9999mm probe separately bounds float32 export boundary sensitivity within 0.0001mm, not physical clearance calibration',
             'tie_complete_transverse_insertion_vs_final_frame':boolean(frame,bodies['tie-sweep']),
             'nominal_node_plug_vs_frame':boolean(frame,bodies['node-plug']),
             'nominal_node_plug_vs_node_reference':boolean(bodies['node-plug'],bodies['node-reference']),
             'conservative_15mm_tool_vs_frame':boolean(frame,bodies['node-tool']),
             'conservative_15mm_tool_vs_node_reference':boolean(bodies['node-reference'],bodies['node-tool']),
             'candidate_2p5mm_thick_15mm_head_wrench_vs_frame':boolean(frame,bodies['thin-wrench']),
             'candidate_2p5mm_thick_15mm_head_wrench_vs_node_reference':boolean(bodies['node-reference'],bodies['thin-wrench']),
             'actual_tool_dimensions_and_motion':'not checked; thin wrench is a hypothetical static envelope',
             'cable_keepout_vs_node_at_slot_positions':{str(dy):boolean(bodies['cable-keepout'],bodies[f'node-envelope-{dy}']) for dy in [-3,0,3]}}
        p=np.array(info['center_mm']);a=np.radians(info['saddle_angle_deg'])
        normal=np.array([np.cos(a),np.sin(a),0]);tangent=np.array([-np.sin(a),np.cos(a),0])
        webs=[]
        for x in np.linspace(-1.5,1.5,13):
            for y in np.linspace(-1.5,1.5,13):
                q=p+x*normal+y*tangent
                z=vertical_hits(mesh,q[:2])-p[2]
                upper_eye=z[(z>-6.5)&(z<-4)];cradle=z[(z>-4)&(z<0)]
                if len(upper_eye) and len(cradle):webs.append(float(cradle.min()-upper_eye.max()))
        row['final_saddle_sampled_vertical_web']={'minimum_mm':min(webs) if webs else None,
            'sample_columns':169,'material_columns':len(webs),
            'status':'pass' if webs and min(webs)>2.3 else 'fail',
            'scope':'Local central 3x3mm region; not global minimum thickness or strength'}
        results['variants'][label]=row
    (ROOT/'validation/final-assembly.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
