"""Read-only reproduction of the finite old-interface incompatibility witness.

Run with --verify to compare the computed geometry with interface-feasibility.json.
This script writes no files and does not invoke Blender, Godot, Git, or a survey.
All arithmetic is finite float64 after the inherited float32 packed decode.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
NAMES = ['CloudSea_1_1', 'CloudSea_0_1', 'CloudSea_1_0', 'CloudSea_1_2', 'CloudSea_2_1']


def need(condition, message):
    if not condition:
        raise ValueError(message)


def decode():
    path = ROOT / 'source-assets/cloud-bank58/revision-k/world-trial-v1/provenance58k.py'
    spec = importlib.util.spec_from_file_location('frozen_provenance58k', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.NEIGHBORS = NAMES.copy()
    return mod.decode_clouds()


def topology(t):
    v, ii = np.unique(t.reshape(-1, 3), axis=0, return_inverse=True)
    f = ii.reshape(-1, 3)
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    eu, ei, ec = np.unique(np.sort(e, axis=1), axis=0, return_inverse=True, return_counts=True)
    signs = np.bincount(ei, weights=np.where(e[:, 0] < e[:, 1], 1, -1))
    graph = coo_matrix((np.ones(len(eu)*2), (np.r_[eu[:, 0], eu[:, 1]], np.r_[eu[:, 1], eu[:, 0]])), shape=(len(v), len(v)))
    components, _ = connected_components(graph)
    bad_links = 0
    for i in range(len(v)):
        faces = f[np.any(f == i, axis=1)]
        le = faces[faces != i].reshape(-1, 2)
        u, count = np.unique(le, return_counts=True)
        seen = {int(u[0])}
        while True:
            new = set(int(b) for a, b in np.concatenate([le, le[:, ::-1]]) if int(a) in seen)
            if new.issubset(seen):
                break
            seen |= new
        bad_links += int(np.any(count != 2) or len(seen) != len(u))
    result = dict(welded_V=len(v), E=len(eu), F=len(f), euler=len(v)-len(eu)+len(f),
                  components=int(components), bad_edge_incidence=int(np.sum(ec != 2)),
                  bad_directed_edges=int(np.sum(signs != 0)), bad_vertex_links=bad_links,
                  duplicate_faces=len(f)-len(np.unique(np.sort(f, axis=1), axis=0)),
                  minimum_triangle_area_m2=float(np.linalg.norm(np.cross(t[:, 1]-t[:, 0], t[:, 2]-t[:, 0]), axis=1).min()/2))
    return result, (v, f, e, eu, ei)


def intersections(a, b, self_test=False):
    lo, hi = b.min(1), b.max(1)
    pairs = []
    for i, tri in enumerate(a):
        js = np.flatnonzero(np.all((hi >= tri.min(0)-1e-8) & (lo <= tri.max(0)+1e-8), axis=1))
        if self_test:
            js = js[js > i]
        pairs.extend((i, int(j)) for j in js)
    pairs = np.asarray(pairs, int)
    ta, tb = a[pairs[:, 0]], b[pairs[:, 1]]
    if self_test:
        keep = ~np.any(np.all(ta[:, :, None, :] == tb[:, None, :, :], axis=-1), axis=(1, 2))
        pairs, ta, tb = [x[keep] for x in (pairs, ta, tb)]
    na = np.cross(ta[:, 1]-ta[:, 0], ta[:, 2]-ta[:, 0]); na /= np.linalg.norm(na, axis=1)[:, None]
    nb = np.cross(tb[:, 1]-tb[:, 0], tb[:, 2]-tb[:, 0]); nb /= np.linalg.norm(nb, axis=1)[:, None]
    da = np.sum((ta-tb[:, 0, None, :])*nb[:, None, :], axis=-1)
    db = np.sum((tb-ta[:, 0, None, :])*na[:, None, :], axis=-1)
    keep = (da.min(1) <= 1e-8) & (da.max(1) >= -1e-8) & (db.min(1) <= 1e-8) & (db.max(1) >= -1e-8)
    pairs, ta, tb, na, nb, da, db = [x[keep] for x in (pairs, ta, tb, na, nb, da, db)]
    direction = np.cross(na, nb); lengths = np.linalg.norm(direction, axis=1)
    coplanar = int(np.sum(lengths < 1e-10))
    keep = lengths >= 1e-10
    pairs, ta, tb, da, db, direction, lengths = [x[keep] for x in (pairs, ta, tb, da, db, direction, lengths)]
    direction /= lengths[:, None]
    if not len(pairs):
        return pairs, np.empty((0, 2, 3)), coplanar
    def cut(tri, d):
        points = []
        for i, j in [(0, 1), (1, 2), (2, 0)]:
            den = d[:, i]-d[:, j]
            good = (np.minimum(d[:, i], d[:, j]) <= 1e-8) & (np.maximum(d[:, i], d[:, j]) >= -1e-8) & (abs(den) > 1e-12)
            u = np.divide(d[:, i], den, out=np.zeros_like(den), where=good)
            p = tri[:, i] + u[:, None]*(tri[:, j]-tri[:, i]); p[~good] = np.nan
            points.append(p)
        return np.stack(points, axis=1)
    ap, bp = cut(ta, da), cut(tb, db)
    av, bv = np.sum(ap*direction[:, None, :], -1), np.sum(bp*direction[:, None, :], -1)
    amin, amax = np.nanmin(av, 1), np.nanmax(av, 1)
    bmin, bmax = np.nanmin(bv, 1), np.nanmax(bv, 1)
    low, high = np.maximum(amin, bmin), np.minimum(amax, bmax)
    keep = high-low > 1e-6
    ids = np.nanargmin(av[keep], axis=1)
    base = ap[keep][np.arange(keep.sum()), ids]
    seg = np.stack([base+(low[keep]-amin[keep])[:, None]*direction[keep], base+(high[keep]-amin[keep])[:, None]*direction[keep]], axis=1)
    return pairs[keep], seg, coplanar


def projection_boundary(t, mesh):
    v, f, e, eu, ei = mesh
    ef = np.tile(np.arange(len(f)), 3)
    fe = ef[np.argsort(ei, kind='stable')].reshape(-1, 2)
    normals = np.cross(t[:, 1]-t[:, 0], t[:, 2]-t[:, 0])
    silhouette = eu[normals[fe[:, 0], 1]*normals[fe[:, 1], 1] <= 0]
    p = t[:, :, [0, 2]]; a = p[:, 0]; b = p[:, 1]-a; c = p[:, 2]-a
    det = b[:, 0]*c[:, 1]-b[:, 1]*c[:, 0]; good = abs(det) > 1e-10
    a, b, c, det = [x[good] for x in (a, b, c, det)]
    def uv(point):
        d = point-a
        return np.c_[(d[:, 0]*c[:, 1]-d[:, 1]*c[:, 0])/det, (b[:, 0]*d[:, 1]-b[:, 1]*d[:, 0])/det]
    segments, source_edges = [], []
    for edge in silhouette:
        p, q = v[edge][:, [0, 2]]; uv0, uv1 = uv(p), uv(q)
        intercept = np.c_[uv0, 1-uv0.sum(1)]-1e-10
        slope = np.c_[uv1-uv0, -(uv1-uv0).sum(1)]
        lo, hi, valid = np.zeros(len(a)), np.ones(len(a)), np.ones(len(a), bool)
        for j in range(3):
            nz = abs(slope[:, j]) > 1e-14
            rhs = np.divide(-intercept[:, j], slope[:, j], out=np.zeros(len(a)), where=nz)
            lo = np.where(slope[:, j] > 1e-14, np.maximum(lo, rhs), lo)
            hi = np.where(slope[:, j] < -1e-14, np.minimum(hi, rhs), hi)
            valid &= nz | (intercept[:, j] > 0)
        valid &= (hi > lo) & (hi > 0) & (lo < 1)
        starts, ends = np.clip(lo[valid], 0, 1), np.clip(hi[valid], 0, 1)
        last = 0.
        for i in np.argsort(starts):
            low, high = starts[i], ends[i]
            if low > last and (low-last)*np.linalg.norm(q-p) > 1e-4:
                segments.append([p+last*(q-p), p+low*(q-p)]); source_edges.append(edge)
            last = max(last, high)
        if last < 1 and (1-last)*np.linalg.norm(q-p) > 1e-4:
            segments.append([p+last*(q-p), q]); source_edges.append(edge)
    seg = np.asarray(segments); endpoints = seg.reshape(-1, 2)
    pairs = cKDTree(endpoints).query_pairs(1e-4, output_type='ndarray')
    graph = coo_matrix((np.ones(len(pairs)*2), (np.r_[pairs[:, 0], pairs[:, 1]], np.r_[pairs[:, 1], pairs[:, 0]])), shape=(len(endpoints), len(endpoints)))
    _, vertex_labels = connected_components(graph)
    edges = vertex_labels.reshape(-1, 2); nv = int(vertex_labels.max()+1)
    graph = coo_matrix((np.ones(len(edges)*2), (np.r_[edges[:, 0], edges[:, 1]], np.r_[edges[:, 1], edges[:, 0]])), shape=(nv, nv))
    count, component_labels = connected_components(graph); labels = component_labels[edges[:, 0]]
    coords = np.array([endpoints[np.flatnonzero(vertex_labels == i)[0]] for i in range(nv)])
    loops = []
    for comp in range(count):
        es = edges[labels == comp]; adjacency = {int(x): [] for x in np.unique(es)}
        for x, y in es:
            adjacency[int(x)].append(int(y)); adjacency[int(y)].append(int(x))
        need(all(len(x) == 2 for x in adjacency.values()), 'Projection-boundary links must be cycles')
        start = int(es[0, 0]); previous, current, order = -1, start, []
        while True:
            order.append(current)
            nxt = adjacency[current][0] if adjacency[current][0] != previous else adjacency[current][1]
            previous, current = current, nxt
            if current == start:
                break
            need(len(order) <= len(adjacency), 'Boundary traversal closed')
        p = coords[order]
        area = abs(np.sum(p[:, 0]*np.roll(p[:, 1], -1)-p[:, 1]*np.roll(p[:, 0], -1)))/2
        loops.append(dict(component=comp, segments=len(es), absolute_area_m2=float(area), perimeter_m=float(np.linalg.norm(seg[labels == comp, 1]-seg[labels == comp, 0], axis=1).sum())))
    return seg, labels, loops, len(silhouette), v[np.asarray(source_edges)]


def vertical_hits(t, xz):
    p = t[:, :, [0, 2]]; a = p[:, 1]-p[:, 0]; b = p[:, 2]-p[:, 0]
    det = a[:, 0]*b[:, 1]-a[:, 1]*b[:, 0]; d = xz-p[:, 0]
    u = np.divide(d[:, 0]*b[:, 1]-d[:, 1]*b[:, 0], det, out=np.zeros(len(t)), where=abs(det) > 1e-10)
    v = np.divide(a[:, 0]*d[:, 1]-a[:, 1]*d[:, 0], det, out=np.zeros(len(t)), where=abs(det) > 1e-10)
    good = (abs(det) > 1e-10) & (u >= -1e-9) & (v >= -1e-9) & (u+v <= 1+1e-9)
    y = t[:, 0, 1]+u*(t[:, 1, 1]-t[:, 0, 1])+v*(t[:, 2, 1]-t[:, 0, 1])
    ids = np.flatnonzero(good); ids = ids[np.argsort(y[ids])]
    return dict(Y_sorted_m=y[ids].tolist(), triangle_indices_sorted=ids.tolist())


def analyze():
    clouds = decode(); selected = clouds[NAMES[0]]['triangles']
    topologies, contacts, witness_pair, witness_segment = {}, {}, None, None
    for name, row in clouds.items():
        t = row['triangles']; topo, mesh = topology(t)
        _, intersections_self, coplanar = intersections(t, t, True)
        topo['nonadjacent_self_segments'] = len(intersections_self); topo['coplanar_candidates'] = coplanar
        topologies[name] = topo
        if name == NAMES[0]:
            selected_mesh = mesh
            continue
        pairs, seg, coplanar = intersections(selected, t)
        contacts[name] = dict(segments=len(seg), summed_segment_length_m=float(np.linalg.norm(seg[:, 1]-seg[:, 0], axis=1).sum()), Y_range_m=[float(seg[:, :, 1].min()), float(seg[:, :, 1].max())], coplanar_candidates=coplanar)
        if name == 'CloudSea_1_2':
            match = np.flatnonzero(np.all(pairs == [530, 4706], axis=1))
            need(len(match) == 1, 'Unique stated lower/lower witness pair')
            witness_pair = pairs[match[0]]; witness_segment = seg[match[0]]
    boundary, labels, loops, candidates, source_edges = projection_boundary(selected, selected_mesh)
    midpoint = witness_segment.mean(0); direction = boundary[:, 1]-boundary[:, 0]
    u = np.clip(np.sum((midpoint[[0, 2]]-boundary[:, 0])*direction, axis=1)/np.sum(direction*direction, axis=1), 0, 1)
    nearest = boundary[:, 0]+u[:, None]*direction; distances = np.linalg.norm(nearest-midpoint[[0, 2]], axis=1); i = int(distances.argmin())
    evidence, gradients = [], []
    for name, face in [('CloudSea_1_1', 530), ('CloudSea_1_2', 4706)]:
        t = clouds[name]['triangles'][face]; edge = np.array([t[1]-t[0], t[2]-t[0]]).T
        bary = []
        for p in [witness_segment[0], midpoint, witness_segment[1]]:
            x, y = np.linalg.lstsq(edge, p-t[0], rcond=None)[0]; b = np.array([1-x-y, x, y])
            bary.append(dict(barycentric=b.tolist(), reconstruction_residual_m=float(np.linalg.norm(b@t-p))))
        n = np.cross(t[1]-t[0], t[2]-t[0]); gradient = -n[[0, 2]]/n[1]; gradients.append(gradient)
        evidence.append(dict(cloud=name, triangle_index_zero_based=face, triangle_world_xyz_m=t.tolist(), barycentrics_endpoint_midpoint_endpoint=bary, height_gradient_xz=gradient.tolist()))
    gradient = gradients[0]-gradients[1]; gradient /= np.linalg.norm(gradient)
    switches = []
    for offset in [-1, 1]:
        p = midpoint[[0, 2]]+offset*gradient
        switches.append(dict(offset_along_height_difference_gradient_m=offset, XZ_m=p.tolist(), selected_bottom_m=vertical_hits(selected, p)['Y_sorted_m'][0], neighbor_bottom_m=vertical_hits(clouds['CloudSea_1_2']['triangles'], p)['Y_sorted_m'][0]))
    return dict(topology=topologies, actual_surface_intersections=contacts,
        actual_projection_boundary=dict(candidate_silhouette_edges=candidates, retained_union_boundary_segments=len(boundary), loops=loops),
        contradiction_witness=dict(segment_world_xyz_m=witness_segment.tolist(), midpoint_world_xyz_m=midpoint.tolist(), triangle_evidence=evidence,
            midpoint_vertical_intersections=dict(selected=vertical_hits(selected, midpoint[[0, 2]]), neighbor=vertical_hits(clouds['CloudSea_1_2']['triangles'], midpoint[[0, 2]])),
            local_exterior_lower_union_seam_test=switches, distance_to_actual_projected_union_boundary_m=float(distances[i]),
            nearest_boundary_point_XZ_m=nearest[i].tolist(), nearest_boundary_segment_XZ_m=boundary[i].tolist(),
            nearest_boundary_original_welded_edge_world_xyz_m=source_edges[i].tolist(), nearest_boundary_component=int(labels[i]),
            whole_witness_segment_distance_lower_bound_m=float(distances[i]-np.linalg.norm((witness_segment[1]-witness_segment[0])[[0, 2]])/2),
            incompatibility_margin_m_at_midpoint=float(midpoint[1]-630), whole_segment_minimum_belly_violation_m=float(witness_segment[:, 1].min()-630)))


def verify(out):
    report = json.loads((HERE/'interface-feasibility.json').read_text())
    for relative, digest in report['input_sha256'].items():
        need(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest, 'Input identity: '+relative)
    def compare(actual, expected, path):
        if isinstance(actual, dict):
            for key, value in actual.items():
                need(key in expected, 'Missing expected field: '+path+'/'+key)
                compare(value, expected[key], path+'/'+key)
        elif isinstance(actual, list):
            need(len(actual) == len(expected), 'List length: '+path)
            for i, value in enumerate(actual):
                compare(value, expected[i], path+'/'+str(i))
        elif isinstance(actual, (float, int)):
            need(abs(actual-expected) < 1e-7, 'Numeric mismatch: '+path)
        else:
            need(actual == expected, 'Value mismatch: '+path)
    compare(out['contradiction_witness'], report['contradiction_witness'], 'witness')
    compare(out['actual_projection_boundary'], report['actual_projection_boundary'], 'boundary')
    for row in report['topology']:
        for key in ['welded_V', 'E', 'F', 'euler']:
            need(row[key] == out['topology'][row['cloud']][key], 'Topology mismatch')
    for row in report['actual_surface_intersections']:
        for key in ['segments', 'summed_segment_length_m', 'Y_range_m']:
            compare(out['actual_surface_intersections'][row['neighbor']][key], row[key], 'contact/'+key)
    return True


if __name__ == '__main__':
    result = analyze()
    if '--verify' in sys.argv:
        result['report_verified'] = verify(result)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
