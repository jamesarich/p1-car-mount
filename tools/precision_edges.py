"""Targeted contraction of round-off-sized edges on zero-area exported facets.
Only a zero-area face may initiate a contraction, and total vertex motion is
bounded to 1e-6 mm. This does not smooth, rescale or remove nonzero-area faces
unless they collapse onto the contracted edge. Caller must still require
strict topology, positive area, bounds, volume and binary-roundtrip validity.
"""
import numpy as np
import trimesh


def contract_precision_edges(vertices, faces, max_motion_mm=1e-6):
    vertices = np.asarray(vertices)
    faces = np.asarray(faces, dtype=np.int64)
    original_vertices = vertices.copy()
    parent = np.arange(len(vertices))
    contractions = 0
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for iteration in range(8):
        bad = np.where(trimesh.triangles.area(vertices[faces].astype(float)) <= 0)[0]
        if not len(bad):
            result = trimesh.Trimesh(vertices, faces, process=False)
            result.remove_unreferenced_vertices()
            return result, dict(contractions=contractions,
                                max_allowed_motion_mm=max_motion_mm,
                                max_actual_motion_mm=float(np.linalg.norm(
                                    original_vertices-original_vertices[np.array([find(i) for i in range(len(parent))])],axis=1).max()))
        for j in bad:
            face = faces[j]
            lengths = np.linalg.norm(vertices[face].astype(float) -
                                     np.roll(vertices[face].astype(float), -1, axis=0), axis=1)
            k = int(lengths.argmin())
            if lengths[k] > max_motion_mm:
                raise ValueError('Zero-area face has no precision-sized edge to contract')
            a, b = find(int(face[k])), find(int(face[(k+1)%3]))
            if a == b:
                continue
            # Representatives remain existing float32 coordinates.
            a, b = sorted((a, b))
            parent[b] = a
            contractions += 1
        mapping = np.array([find(i) for i in range(len(parent))])
        motion = np.linalg.norm(original_vertices - original_vertices[mapping], axis=1)
        if motion.max() > max_motion_mm:
            raise ValueError('Precision contraction exceeded its vertex-motion bound')
        faces = mapping[faces]
        keep = np.all(np.diff(np.sort(faces,axis=1),axis=1) != 0, axis=1)
        faces = faces[keep]
    raise ValueError('Zero-area contraction did not converge')


