"""Normalize native exports at downstream float32 precision, with strict checks.

This intentional export step contracts precision-collapsed facets using Manifold;
it does not apply cosmetic smoothing or alter CAD interface parameters.
"""
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as md
from precision_edges import contract_precision_edges

def normalize_export(path):
    source = trimesh.load(path, process=False, force='mesh')
    vertices, inverse = np.unique(source.vertices.astype(np.float32), axis=0, return_inverse=True)
    faces = inverse[source.faces].astype(np.uint32)
    solid = md.Manifold(md.Mesh(vertices, faces, tolerance=0.00002))
    if solid.status() != md.Error.NoError:
        raise ValueError(f'{path}: float32 Manifold conversion failed: {solid.status()}')
    output = solid.to_mesh()
    mesh, contractions = contract_precision_edges(output.vert_properties[:,:3], output.tri_verts)
    if not mesh.is_volume or np.any(mesh.area_faces <= 0):
        raise ValueError(f'{path}: normalized boundary invalid')
    if not np.allclose(source.bounds, mesh.bounds, atol=0.0001, rtol=0):
        raise ValueError(f'{path}: normalization changed bounds')
    volume_error = abs(mesh.volume-source.volume)/source.volume
    if volume_error > .00001:
        raise ValueError(f'{path}: normalization changed volume by {volume_error}')
    # The exported coordinates already have exactly binary STL precision.
    path.write_bytes(trimesh.exchange.stl.export_stl(mesh))
    reopened = trimesh.load(path, process=False, force='mesh')
    v, inv = np.unique(reopened.vertices, axis=0, return_inverse=True)
    reopened = trimesh.Trimesh(v, inv[reopened.faces], process=False)
    if not reopened.is_volume or np.any(reopened.area_faces <= 0):
        raise ValueError(f'{path}: binary roundtrip failed')
    return dict(method='Manifold float32 boundary normalization; no cosmetic smoothing',
                source_triangles=len(source.faces), exported_triangles=len(mesh.faces),
                precision_edge_contractions=contractions,
                relative_volume_delta=float(volume_error), bound_tolerance_mm=.0001,
                binary_roundtrip_valid=True)

if __name__ == '__main__':
    import sys, json
    for arg in sys.argv[1:]:
        print(json.dumps(normalize_export(Path(arg))))
