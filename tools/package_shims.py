"""Geometry-only 3MF: four named optional calibration shims, mm, no profiles."""
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import trimesh

root=Path(__file__).resolve().parents[1]
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',ns)
def el(name,attrs={},parent=None):
    return ET.SubElement(parent,'{'+ns+'}'+name,attrs) if parent is not None else ET.Element('{'+ns+'}'+name,attrs)
model=el('model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
resources=el('resources',parent=model); build=el('build',parent=model)
for i,t in enumerate([.5,1,1.5,2],1):
    source=root/f'p1-screw-shim-{str(t).replace(".","p")}mm.stl'
    mesh=trimesh.load(source,process=False,force='mesh')
    v,inv=np.unique(mesh.vertices,axis=0,return_inverse=True);f=inv[mesh.faces]
    obj=el('object',{'id':str(i),'type':'model','name':f'Calibration shim {t} mm'},resources)
    m=el('mesh',parent=obj);verts=el('vertices',parent=m);tris=el('triangles',parent=m)
    for p in v:el('vertex',{k:repr(float(x)) for k,x in zip(['x','y','z'],p)},verts)
    for p in f:el('triangle',{k:str(int(x)) for k,x in zip(['v1','v2','v3'],p)},tris)
    el('item',{'objectid':str(i),'transform':f'1 0 0 0 1 0 0 0 1 {10+24*(i-1)} 10 0'},build)
target=root/'p1-screw-shim-calibration-kit.3mf'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
with zipfile.ZipFile(target) as z:
    reopened=ET.fromstring(z.read('3D/3dmodel.model'))
    assert reopened.attrib['unit']=='millimeter'
    objects=reopened.findall('.//{'+ns+'}object');assert len(objects)==4
    for obj in objects:
        v=np.array([[float(p.attrib[k]) for k in ['x','y','z']] for p in obj.findall('.//{'+ns+'}vertex')])
        f=np.array([[int(p.attrib[k]) for k in ['v1','v2','v3']] for p in obj.findall('.//{'+ns+'}triangle')])
        assert trimesh.Trimesh(v,f,process=False).is_volume
print('Geometry-only 3MF reopened with four named valid solids. No printer/material profile or slicing.')
