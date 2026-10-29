"""Compare selected finished-mesh window junctions in millimeters.
No contour smoothing is applied. Polygon joining rounds section endpoints to 1e-6 mm.
"""
import argparse,json
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import LineString
from shapely.ops import polygonize

p=argparse.ArgumentParser()
p.add_argument('meshes',nargs='+',type=Path)
p.add_argument('--out',type=Path)
a=p.parse_args()
results={}
for path in a.meshes:
 mesh=trimesh.load(path,process=False)
 stations=[]
 for z in (3,8,12,16):
  segments=trimesh.intersections.mesh_plane(mesh,[0,0,1],[0,0,z])
  polygons=list(polygonize([LineString(np.round(s[:,:2],6)) for s in segments]))
  candidates=[]
  seen=set()
  for poly in polygons:
   if poly.area<1000:continue
   for loop in [poly.exterior,*poly.interiors]:
    pts=np.asarray(loop.coords[:-1]); u=pts-np.roll(pts,1,axis=0); v=np.roll(pts,-1,axis=0)-pts
    den=np.linalg.norm(u,axis=1)*np.linalg.norm(v,axis=1)
    with np.errstate(invalid='ignore',divide='ignore'):
     angles=np.degrees(np.arccos(np.clip((u*v).sum(1)/den,-1,1)))
    for pt,ang,d,lin,lout in zip(pts,angles,den,np.linalg.norm(u,axis=1),np.linalg.norm(v,axis=1)):
     key=tuple(pt)
     if key in seen or d<1e-12:continue
     seen.add(key)
     if 8<pt[0]<66 and -76<pt[1]<72:
      candidates.append(dict(x=float(pt[0]),y=float(pt[1]),turn_deg=float(ang),incoming_segment_mm=float(lin),outgoing_segment_mm=float(lout)))
  # Focus on previously measured roots; tangent changes elsewhere can include
  # intentional mating edges or intersections of an inclined surface section.
  measured=[]
  for x,y in ((12,-68.874),(12,-23.673),(12,44.5)):
   near=[c for c in candidates if (c['x']-x)**2+(c['y']-y)**2<8**2]
   stable=[c for c in near if min(c['incoming_segment_mm'],c['outgoing_segment_mm'])>=.002]
   measured.append(dict(original_corner_xy=[x,y],max_raw_turn_within8mm=max(near,key=lambda q:q['turn_deg']) if near else None,max_turn_adjacent_segments_ge_0_002mm=max(stable,key=lambda q:q['turn_deg']) if stable else None))
  stations.append(dict(z_mm=z,root_neighborhoods=measured,largest_in_window_region=sorted(candidates,key=lambda q:q['turn_deg'],reverse=True)[:12]))
 results[str(path)]=stations
out=json.dumps(results,indent=2)
if a.out:a.out.write_text(out)
print(out)
