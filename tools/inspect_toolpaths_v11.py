"""Read actual Bambu paths; G2/G3 are tessellated for plots, originals unchanged.

Run with installed Python (numpy, matplotlib). Plots retain complete previous
model/support paths and let axes clip them; no endpoint-based support inference.
This is targeted path visualization, not a support/contact or strength solver.
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, json, math, re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
WORDS=re.compile(r'([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))')
COLORS={'Support':'#ee912a','Support interface':'#b46a12','Support transition':'#d9a05d','Brim':'#8495a0',
        'Bridge':'#d03971','Overhang wall':'#a243b2','Outer wall':'#174f7e',
        'Inner wall':'#3386b5','Bottom surface':'#00a99c','Top surface':'#00a99c',
        'Internal solid infill':'#00a99c','Sparse infill':'#5a8b53',
        'Floating vertical shell':'#816a94','Gap infill':'#848340'}

def parse(path):
    xyz=np.zeros(3); e=0.; absxy=True; abse=False; zmark=None; feature='Custom'; width=.42
    layers=defaultdict(list); counts=Counter(); lengths=Counter(); extrusion=Counter(); arcs=Counter()
    for line in path.open():
        if line.startswith('; Z_HEIGHT:'):
            zmark=round(float(line.split(':')[1]),6)
        elif line.startswith('; FEATURE:'):
            feature=line.split(':',1)[1].strip()
        elif line.startswith('; LINE_WIDTH:'):
            width=float(line.split(':')[1])
        raw=line.split(';',1)[0].strip()
        if not raw: continue
        cmd=raw.split()[0]; p={k:float(v) for k,v in WORDS.findall(raw)}
        if cmd=='G90': absxy=True
        elif cmd=='G91': absxy=False
        elif cmd=='M82': abse=True
        elif cmd=='M83': abse=False
        elif cmd=='G92':
            if 'E' in p:e=p['E']
            for i,k in enumerate('XYZ'):
                if k in p:xyz[i]=p[k]
        elif cmd in ('G0','G1','G2','G3'):
            end=xyz.copy()
            for i,k in enumerate('XYZ'):
                if k in p:end[i]=p[k] if absxy else end[i]+p[k]
            de=(p['E']-e if abse else p['E']) if 'E' in p else 0.
            if 'E' in p:e=p['E'] if abse else e+p['E']
            points=np.array([xyz[:2],end[:2]])
            if cmd in ('G2','G3') and ('I' in p or 'J' in p):
                center=xyz[:2]+np.array([p.get('I',0.),p.get('J',0.)])
                radius=np.linalg.norm(xyz[:2]-center)
                a=math.atan2(xyz[1]-center[1],xyz[0]-center[0]); b=math.atan2(end[1]-center[1],end[0]-center[0])
                sweep=(b-a)%(2*math.pi) if cmd=='G3' else -((a-b)%(2*math.pi))
                if abs(sweep)<1e-8:sweep=(2*math.pi if cmd=='G3' else -2*math.pi)
                # At most 0.02 mm chord sagitta and 10 degree steps.
                step=min(math.radians(10),2*math.acos(max(-1.,1-.02/max(radius,.02))))
                angles=np.linspace(a,a+sweep,max(2,math.ceil(abs(sweep)/max(step,1e-5))+1))
                points=center+radius*np.column_stack((np.cos(angles),np.sin(angles)))
                points[0]=xyz[:2];points[-1]=end[:2]
            if zmark is not None and de>0 and np.linalg.norm(points[-1]-points[0])+len(points)>2.000001 and feature!='Custom':
                length=float(np.linalg.norm(np.diff(points,axis=0),axis=1).sum())
                if length>1e-7:
                    layers[zmark].append((feature,points,width))
                    counts[feature]+=1;lengths[feature]+=length;extrusion[feature]+=de
                    if cmd in ('G2','G3'):arcs[feature]+=1
            xyz=end
    return dict(layers),dict(counts),dict(lengths),dict(extrusion),dict(arcs)

def bounds(paths):
    pts=np.concatenate([x[1] for x in paths]);return [pts.min(axis=0).tolist(),pts.max(axis=0).tolist()]

def draw(ax,paths,prior=False,support_only=None):
    groups=defaultdict(list)
    for f,p,w in paths:
        support=f.startswith('Support')
        if support_only is not None and support!=support_only:continue
        groups[f].append(p)
    for f,segments in groups.items():
        c=('#e0b67f' if f.startswith('Support') else '#c7cbd0') if prior else COLORS.get(f,'#677582')
        ax.add_collection(LineCollection(segments,colors=c,linewidths=.65 if prior else .9,alpha=.65 if prior else 1,zorder=1 if prior else 2))

def main():
    report={'scope':'Targeted actual toolpath inspection. No printer operated. Not exhaustive support/bridge proof.',
        'profile':'Bambu A1 0.4; Bambu PETG HF provisional prototype; 0.20mm model layers; 6 walls, 40% infill, 4mm brim, automatic supports',
        'parser':'Positive-E XY extrusion after Z_HEIGHT markers; G2/G3 IJ arcs interpolated with <=0.02mm sagitta and <=10deg steps. Full prior paths shown and axis-clipped, never endpoint-filtered.',
        'variants':{}}
    for variant in ('n-type','stock'):
        path=ROOT/'slicer'/variant/'plate_1.gcode'; layers,counts,lengths,es,arcs=parse(path)
        zs=sorted(layers); allpaths=[p for v in layers.values() for p in v]
        modelzs=[z for z in zs if any(not p[0].startswith('Support') and p[0]!='Brim' for p in layers[z])]
        supportzs=[z for z in zs if any(p[0].startswith('Support') for p in layers[z])]
        modelpaths=[p for p in allpaths if not p[0].startswith('Support') and p[0]!='Brim']
        bb=bounds(modelpaths); cx=(bb[0][0]+bb[1][0])/2
        # Infer translation from known original bounds, retain assembly dimensions.
        original_ymin=-141.5 if variant=='n-type' else -130.5
        ty=bb[0][1]-original_ymin-.21 # outer-wall center approx half line width inward
        specs=[('First layer / bed contact',.2,(0,256,0,256)),
            ('Front node-screw ceiling',11.2,(cx-16,cx+16,ty+15,ty+45)),
            ('Rear node-screw ceiling',14.,(cx-16,cx+16,ty-24,ty+6)),
            ('Pylon chamber / nut shoulder',60.,(cx-24,cx+24,0,70)),
            ('Pylon roof underside',64.2 if variant=='n-type' else 65.6,(cx-24,cx+24,0,70)),
            ('Connector bore / crown',67.,(cx-24,cx+24,0,70)),
            ('Cable tie-eye roof',27.8 if variant=='n-type' else 30.,(cx-104,cx-65,ty-105,ty-45)),
            ('Open cable cradle',32. if variant=='n-type' else 34.,(cx-104,cx-65,ty-105,ty-45))]
        fig,axes=plt.subplots(2,4,figsize=(20,11));selected=[]
        for ax,(label,target,lim) in zip(axes.flat,specs):
            z=min(modelzs,key=lambda v:abs(v-target));prev_model=max((v for v in modelzs if v<z-.00001),default=None)
            prev_support=max((v for v in supportzs if v<z-.00001),default=None)
            if prev_model is not None:draw(ax,layers[prev_model],prior=True,support_only=False)
            if prev_support is not None:draw(ax,layers[prev_support],prior=True,support_only=True)
            draw(ax,layers[z]);ax.set(xlim=lim[:2],ylim=lim[2:],aspect='equal',xlabel='Bed X (mm)',ylabel='Bed Y (mm)')
            ax.set_title(f'{label}\nZ={z:.3f} mm; prior model {prev_model}; support {prev_support}',fontsize=10)
            ax.grid(alpha=.13)
            selected.append({'feature':label,'z_mm':z,'previous_model_z':prev_model,'previous_support_z':prev_support,'counts_current':dict(Counter(p[0] for p in layers[z]))})
        handles=[Line2D([0],[0],color=c,lw=2,label=f) for f,c in COLORS.items() if f in counts]
        handles += [Line2D([0],[0],color='#c7cbd0',lw=2,label='Previous model layer'),Line2D([0],[0],color='#e0b67f',lw=2,label='Previous support layer')]
        fig.legend(handles=handles,loc='lower center',ncol=5,fontsize=9)
        fig.suptitle(f'{variant}: actual sliced paths — provisional PETG HF prototype',fontsize=15)
        fig.tight_layout(rect=(0,.09,1,.95));output=ROOT/f'toolpaths-{variant}.png';fig.savefig(output,dpi=180);plt.close(fig)
        report['variants'][variant]={'gcode_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'path_commands_by_feature':counts,'deposited_length_mm_by_feature':lengths,'filament_E_mm_by_feature':es,'arc_commands_by_feature':arcs,'z_levels_with_extrusion':len(zs),'z_bounds_mm':[min(zs),max(zs)],'model_layer_count':len(modelzs),'support_layer_count':len(supportzs),'all_extrusion_centerline_bounds_xy_mm':bounds(allpaths),'model_centerline_bounds_xy_mm':bb,'selected_layers':selected,'preview':output.name}
    report['visual_observations']=[
        'Both first layers show continuous frame/foot paths plus brim and support footprints; all inspected deposition centerlines lie inside 0..256 mm bed coordinates.',
        'Both node-screw pocket crops show support and support-interface paths in the access recesses, alongside bridge/overhang paths near the sloping ceilings. Removal and surface quality require coupon prints.',
        'Both pylons show multiple perimeter paths around the retained connector bore/chamber, with support paths below the roof; stock also shows bridge paths in the rear crown region at Z60.',
        'Previous support ghosting at the top bore views is from the reported lower support Z, not evidence that support reaches the bore top.',
        'These eight crops per variant do not prove every deposited run is anchored; no exhaustive width-aware prior-layer contact analysis was performed.',
        'Final v1.1 slicer diagnostics and metadata are recorded separately; no complete anchoring or physical printing proof follows from these crops.'
    ]
    (ROOT/'toolpath-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
