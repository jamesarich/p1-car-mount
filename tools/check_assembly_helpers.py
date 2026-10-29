#!/usr/bin/env python3
"""Export and independently inspect shim and cable-saddle helper geometry.

Run with numpy, scipy, trimesh, rtree installed; e.g.
uv run --with numpy --with scipy --with trimesh --with rtree python tools/check_assembly_helpers.py
Does not operate a printer or regenerate the full frame.
"""
import ast
import json
from pathlib import Path
import subprocess
import tempfile
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
SCAD=ROOT/'.tools/OpenSCAD.app/Contents/MacOS/OpenSCAD'
HELPER=ROOT/'assembly-refinements.scad'

def evaluate(temp,name,source,empty=False):
    src=temp/(name+'.scad'); mesh=temp/(name+'.stl')
    src.write_text(source)
    done=subprocess.run([str(SCAD),'--backend','Manifold','--export-format','asciistl',
                         '-o',str(mesh),str(src)],capture_output=True,text=True)
    log=done.stdout+done.stderr
    if empty:
        assert 'top level object is empty' in log.lower(),(name,log)
    else:
        assert done.returncode==0 and 'ERROR:' not in log,(name,log)
    return mesh,log

def main():
    results={'scope':'Nominal helper exports; full frame, actual hardware and physical fit remain separate.',
             'source':str(HELPER),'screw_stack':'not checked: actual lengths/depths/washer thickness/minimum engagement unknown'}
    with tempfile.TemporaryDirectory(prefix='p1-helper-') as tmp:
        tmp=Path(tmp)
        header=f'use <{HELPER}>\n'
        shim,_=evaluate(tmp,'shims',header+'ar_screw_shim_set();\n')
        m=trimesh.load(shim,force='mesh')
        parts=sorted(m.split(),key=lambda p:p.bounds[0,0])
        assert len(parts)==4
        rows=[]
        for part,height in zip(parts,[.5,1,1.5,2]):
            assert part.is_volume and np.allclose(part.extents,[14,20,height],atol=1e-5)
            rows.append({'size_mm':part.extents.tolist(),'watertight':bool(part.is_watertight),
                         'volume_mm3':float(part.volume)})
        results['shim_set']={'components':4,'parts':rows,'bearing_recess_radial_gap_mm':1,
                             'shank_travel_mm':6,'metal_flat_washer_required':True}
        for variant,alfa in [('n-type',True),('stock',False)]:
            flag='true' if alfa else 'false'
            file,log=evaluate(tmp,variant,header+f'echo(ar_coax_route({flag}));\necho(ar_path_min_radius(ar_coax_route({flag})));\nar_cable_saddle(alfa={flag});\n')
            points=np.array(ast.literal_eval(next(line[6:] for line in log.splitlines() if line.startswith('ECHO: [['))))
            ix=np.argmin(np.abs(points[:,1]-(-86 if alfa else -65)))
            p=points[ix]; tangent=points[ix+1]-points[ix-1]
            angle=np.arctan2(tangent[1],tangent[0])-np.pi/2
            n=np.array([np.cos(angle),np.sin(angle),0])
            t=np.array([-np.sin(angle),np.cos(angle),0])
            m=trimesh.load(file,force='mesh')
            assert m.is_volume and len(m.split())==1
            assert m.bounds[0,0]>=-100
            # Exported-geometry insertion sweep for nominal 2.5 x 1.5 tie.
            # The cube traverses the whole normal direction, including both mouths.
            probe=(f'intersection() {{ import("{file}"); translate({p.tolist()}) '
                   f'rotate([0,0,{np.degrees(angle)}]) translate([0,0,-6.5]) '
                   'cube([40,2.5,1.5],center=true); }')
            evaluate(tmp,variant+'-tie-sweep',probe,empty=True)
            # Actual vertical ligaments between eye ceiling and open cradle floor.
            # 169 columns in central 3 x 3 mm region; this is NOT a global thickness check.
            origin=[]
            for x in np.linspace(-1.5,1.5,13):
                for y in np.linspace(-1.5,1.5,13):
                    origin.append(p+x*n+y*t+[0,0,-10])
            origin=np.array(origin); directions=np.tile([0,0,1],(len(origin),1))
            locations,rays,_=m.ray.intersects_location(origin,directions,multiple_hits=True)
            webs=[]
            for ri in range(len(origin)):
                heights=np.sort(np.unique(np.round(locations[rays==ri,2]-p[2],5)))
                eye_top=heights[(heights>-6.5)&(heights<-4)]
                floor=heights[(heights>-4)&(heights<0)]
                if len(eye_top) and len(floor):webs.append(float(floor.min()-eye_top.max()))
            assert webs and min(webs)>2.3
            # The centerline sampling is exactly that used for native helper construction.
            length=float(np.linalg.norm(np.diff(points,axis=0),axis=1).sum())
            # OpenSCAD echo rounds coordinate vectors to six significant figures.
            # Radius from those rounded points is unstable across tiny joint chords;
            # evaluate radius in native full-precision source, before echo rounding.
            min_r=float(next(line[6:] for line in log.splitlines()
                             if line.startswith('ECHO: ') and not line.startswith('ECHO: [[')))
            results[variant]={'saddle_bounds_mm':m.bounds.tolist(),'saddle_one_volume':True,
                'saddle_center_mm':p.tolist(),'centerline_length_mm':length,
                'source_sampled_minimum_3point_radius_mm':min_r,
                'radius_scope':'Native full-precision route samples; not physical bend measurement',
                'catalog_300mm_datum_and_surplus_slack':'not checked',
                'tie_2.5_by_1.5mm_complete_transverse_sweep':'pass, final helper STL intersection empty',
                'sampled_vertical_web_mm':min(webs),'web_columns_with_eye_and_cradle':len(webs),
                'web_scope':'169 central vertical columns; no global thickness or strength claim',
                'physical_test':'not checked'}
    target=ROOT/'audits/assembly-helpers.json'
    target.write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
