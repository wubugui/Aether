"""Read-only Blender mesh validation for C controls and the continuous lower bank.

``geometry(ob)`` returns (report, world_vertices, triangle_ids, triangles, BVH).
The report's ``passed``/``closed_geometry_passed`` gate requires a single closed,
orientable, consistently wound genus-zero surface with positive signed volume.
This checks the object's stored native mesh after matrix_world, not an evaluated
modifier result. Apply modifiers before validation; enabled modifiers fail the
gate. No mesh, file, scene, normals or winding is repaired by this module.

Self-intersection scope is NONADJACENT triangle pairs: pairs sharing even one
native vertex index are excluded. This intentionally excludes normal topological
contacts, but also means fold-through intersections between such adjacent faces
are not proved absent. That limitation remains explicit in every report.
"""
from collections import Counter, defaultdict
import hashlib
import math
from pathlib import Path
from types import ModuleType

import numpy as np

from geometry58c import volume, world_coordinate


AREA_EPSILON_M2 = 1e-8
VOLUME_EPSILON_M3 = 1e-9
_HELPER_PATH = Path(__file__).resolve().parents[2] / "revision-b/recovery-03/triangle_pairs58b.py"
_HELPER = None


def _json_native(value):
    """Promote NumPy scalar flags without rounding actual diagnostic values."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_native(item) for item in value]
    return value


def _narrow_helper():
    """Load the frozen helper without importing/writing a B __pycache__."""
    global _HELPER
    if _HELPER is None:
        source = _HELPER_PATH.read_bytes()
        module = ModuleType("_frozen_triangle_pairs58b_for_58c")
        module.__file__ = str(_HELPER_PATH)
        exec(compile(source, str(_HELPER_PATH), "exec"), module.__dict__)
        _HELPER = module, hashlib.sha256(source).hexdigest()
    return _HELPER


def mesh_data(ob):
    """Real stored native triangles, transformed into the authored Godot world."""
    if ob.type != "MESH":
        raise TypeError("geometry(ob) requires a Blender MESH object")
    ob.data.calc_loop_triangles()
    vertices = np.asarray(
        [world_coordinate(ob.matrix_world @ vertex.co) for vertex in ob.data.vertices],
        dtype=np.float64,
    ).reshape((-1, 3))
    triangle_ids = np.asarray(
        [tuple(triangle.vertices) for triangle in ob.data.loop_triangles],
        dtype=np.int64,
    ).reshape((-1, 3))
    return vertices, triangle_ids, vertices[triangle_ids]


def _topology(vertices, triangle_ids, native_edges=()):
    """Triangulated 2-manifold checks, including vertex links and orientability."""
    edge_faces = defaultdict(list)
    vertex_faces = defaultdict(list)
    for tid, ids in enumerate(triangle_ids):
        for vertex in set(map(int, ids)):
            vertex_faces[vertex].append(tid)
        for a, b in zip(ids, np.roll(ids, -1)):
            a, b = int(a), int(b)
            edge_faces[tuple(sorted((a, b)))].append((tid, 1 if a < b else -1))

    boundary = [list(edge) for edge, rows in edge_faces.items() if len(rows) == 1]
    overfull = [dict(vertices=list(edge), triangle_ids=[r[0] for r in rows])
                for edge, rows in edge_faces.items() if len(rows) > 2]
    sign_errors = [dict(vertices=list(edge), triangle_ids=[r[0] for r in rows])
                   for edge, rows in edge_faces.items()
                   if len(rows) == 2 and rows[0][1] == rows[1][1]]
    native_edges = {tuple(sorted(map(int, edge))) for edge in native_edges}
    loose_edges = sorted(native_edges - set(edge_faces))
    loose_vertices = sorted(set(range(len(vertices))) - set(vertex_faces))

    # A manifold closed vertex has one connected circular link. Edge incidence
    # alone misses two closed surfaces pinched together at one vertex.
    bad_links = []
    for vertex, face_ids in vertex_faces.items():
        link = defaultdict(list)
        invalid = False
        for tid in face_ids:
            others = [int(i) for i in triangle_ids[tid] if int(i) != vertex]
            if len(others) != 2 or others[0] == others[1]:
                invalid = True
                continue
            a, b = others
            link[a].append(b)
            link[b].append(a)
        remaining = set(link)
        link_components = 0
        while remaining:
            link_components += 1
            stack = [remaining.pop()]
            while stack:
                for other in link[stack.pop()]:
                    if other in remaining:
                        remaining.remove(other)
                        stack.append(other)
        if invalid or link_components != 1 or any(len(v) != 2 for v in link.values()):
            bad_links.append(dict(vertex_id=vertex, triangle_ids=face_ids,
                                  link_components=link_components,
                                  link_degrees={str(k): len(v) for k, v in link.items()}))

    adjacency = defaultdict(list)
    for rows in edge_faces.values():
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, sign_a = rows[i]
                b, sign_b = rows[j]
                # Equal directed-edge signs require one face to be flipped.
                parity = int(sign_a == sign_b)
                adjacency[a].append((b, parity))
                adjacency[b].append((a, parity))
    remaining = set(range(len(triangle_ids)))
    components = []
    bad_vertex_ids = {r['vertex_id'] for r in bad_links}
    while remaining:
        first = min(remaining)
        remaining.remove(first)
        stack, flips, component_ids = [first], {first: 0}, []
        orientation_conflicts = set()
        while stack:
            tid = stack.pop()
            component_ids.append(tid)
            for other, parity in adjacency[tid]:
                required = flips[tid] ^ parity
                if other in flips:
                    if flips[other] != required:
                        orientation_conflicts.add(tuple(sorted((tid, other))))
                else:
                    flips[other] = required
                    remaining.discard(other)
                    stack.append(other)
        component_ids.sort()
        faces = triangle_ids[component_ids]
        vids = set(map(int, faces.ravel()))
        edges = {tuple(sorted((int(a), int(b))))
                 for ids in faces for a, b in zip(ids, np.roll(ids, -1))}
        closed = all(len(edge_faces[e]) == 2 for e in edges)
        vertex_manifold = not (vids & bad_vertex_ids)
        orientable = closed and vertex_manifold and not orientation_conflicts
        chi = len(vids) - len(edges) + len(faces)
        genus_value = (2 - chi) / 2 if orientable else None
        genus = int(genus_value) if genus_value is not None and genus_value >= 0 and genus_value.is_integer() else None
        # Translation to a nearby origin improves floating-point volume stability.
        reference = vertices[min(vids)] if vids else np.zeros(3)
        signed = volume(vertices - reference, faces)
        wound = all(edge_faces[e][0][1] != edge_faces[e][1][1]
                    for e in edges if len(edge_faces[e]) == 2)
        components.append(dict(
            triangle_ids=component_ids, vertices=len(vids), edges=len(edges),
            triangles=len(faces), euler_characteristic=chi, closed=closed,
            vertex_manifold=vertex_manifold, orientable=orientable,
            orientation_conflict_triangle_pairs=[list(p) for p in sorted(orientation_conflicts)],
            consistently_wound=wound, genus=genus, signed_volume_m3=signed,
            positive_volume=bool(math.isfinite(signed) and signed > VOLUME_EPSILON_M3),
        ))
    return dict(
        components=components, component_count=len(components),
        boundary_edges=len(boundary), boundary_edge_vertex_ids=boundary,
        nonmanifold_edges=len(boundary) + len(overfull) + len(loose_edges),
        overfull_edges=len(overfull), overfull_edge_rows=overfull,
        edge_orientation_errors=len(sign_errors), edge_orientation_error_rows=sign_errors,
        nonmanifold_vertices=len(bad_links), nonmanifold_vertex_rows=bad_links,
        loose_vertex_ids=loose_vertices, loose_edges=[list(e) for e in loose_edges],
        orientable=bool(components and all(c['orientable'] for c in components)),
        consistently_wound=not sign_errors,
    )


def geometry(ob):
    """Validate native geometry without fixing it; return report and real arrays."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    vertices, triangle_ids, triangles = mesh_data(ob)
    if not np.isfinite(vertices).all():
        raise ValueError("Non-finite native world vertex coordinates cannot form a valid BVH")
    report = _topology(vertices, triangle_ids, [edge.vertices for edge in ob.data.edges])
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    areas = np.linalg.norm(cross, axis=1) * .5
    degenerate_ids = np.flatnonzero(areas <= AREA_EPSILON_M2).tolist()
    exact_zero_ids = np.flatnonzero(areas == 0).tolist()
    indexed = defaultdict(list)
    geometric = defaultdict(list)
    for tid, (ids, tri) in enumerate(zip(triangle_ids, triangles)):
        indexed[tuple(sorted(map(int, ids)))].append(tid)
        # No rounding or approximate welding: retain exact promoted native values.
        geometric[tuple(sorted(tuple(map(float, p)) for p in tri))].append(tid)
    indexed_duplicates = [ids for ids in indexed.values() if len(ids) > 1]
    geometric_duplicates = [ids for ids in geometric.values() if len(ids) > 1]

    tree = BVHTree.FromPolygons([Vector(tuple(v)) for v in vertices],
                                [tuple(map(int, ids)) for ids in triangle_ids],
                                all_triangles=True, epsilon=0) if len(triangle_ids) else None
    raw_pairs = sorted({tuple(sorted((int(a), int(b))))
                        for a, b in tree.overlap(tree) if a != b}) if tree else []
    adjacent_pairs, candidate_pairs = [], []
    for a, b in raw_pairs:
        shared = sorted(set(map(int, triangle_ids[a])) & set(map(int, triangle_ids[b])))
        if shared:
            adjacent_pairs.append(dict(triangle_ids=[a, b], shared_vertex_ids=shared))
        else:
            candidate_pairs.append((a, b))
    helper, helper_sha = _narrow_helper()
    results = []
    for a, b in candidate_pairs:
        result = _json_native(helper.narrow_phase(triangles[a], triangles[b]))
        # All non-topological contacts fail as well as proper crossings. In
        # particular coplanar-area overlap is never excused as a faceting seam.
        disjoint = result['classification'] in {
            'separated_by_triangle_plane', 'coplanar_disjoint', 'noncoplanar_disjoint'}
        results.append(dict(triangle_ids=[a, b], triangle_a_world=triangles[a].tolist(),
                            triangle_b_world=triangles[b].tolist(),
                            gate_failure=not disjoint, **result))
    failures = [row for row in results if row['gate_failure']]
    proper = [r for r in results if r['classification'] == 'proper_nonadjacent_segment_crossing']
    coplanar = [r for r in results if r['classification'] == 'coplanar_area_overlap']
    modifiers = [modifier.name for modifier in ob.modifiers
                 if modifier.show_viewport or modifier.show_render]
    reference = vertices[0] if len(vertices) else np.zeros(3)
    signed = volume(vertices - reference, triangle_ids) if len(triangle_ids) else 0.
    report.update(
        name=ob.name, vertices=len(vertices), triangles=len(triangle_ids),
        geometry_source='Stored Blender object mesh after matrix_world, then geometry58c.world_coordinate',
        unapplied_enabled_modifiers=modifiers,
        world_bounds=[vertices.min(0).tolist(), vertices.max(0).tolist()] if len(vertices) else None,
        signed_volume_m3=signed, volume_epsilon_m3=VOLUME_EPSILON_M3,
        zero_area_triangles=len(degenerate_ids), degenerate_triangle_ids=degenerate_ids,
        exact_zero_area_triangle_ids=exact_zero_ids, area_epsilon_m2=AREA_EPSILON_M2,
        duplicate_triangles=sum(len(ids) - 1 for ids in geometric_duplicates),
        exact_geometric_duplicate_triangle_groups=geometric_duplicates,
        duplicate_index_triangle_groups=indexed_duplicates,
        broad_phase_unique_pair_count=len(raw_pairs),
        excluded_topologically_adjacent_pair_count=len(adjacent_pairs),
        excluded_topologically_adjacent_pairs_first32=adjacent_pairs[:32],
        nonadjacent_bvh_candidate_count=len(candidate_pairs),
        nonadjacent_narrow_phase_results=results,
        nonadjacent_classification_counts=dict(Counter(r['classification'] for r in results)),
        proper_nonadjacent_crossing_count=len(proper), coplanar_area_overlap_count=len(coplanar),
        nonadjacent_contact_or_intersection_count=len(failures),
        narrow_phase_helper=str(_HELPER_PATH), narrow_phase_helper_sha256=helper_sha,
        narrow_phase_epsilon_m=helper.EPS,
        intersection_check_scope='Every unique BVH candidate without a shared native vertex index is narrow-phase classified; full actual triangle coordinates and every returned intersection/contact point are retained',
        adjacent_pair_limitation='Pairs sharing any native vertex index are excluded, including triangles meeting only at a vertex. Their ordinary topological contact is expected; crossing away from that shared vertex/edge is NOT ruled out by this nonadjacent test',
        coplanar_policy='No blanket allowance: positive-area coplanar overlap and zero-area non-topological contacts fail; only classified disjoint pairs pass',
        gate_contract='Exactly one closed orientable consistently wound genus0 component; positive volume; no loose/pinched topology, duplicates, degenerate triangles, enabled modifiers, or nonadjacent contacts/intersections',
    )
    topology_passed = bool(
        report['component_count'] == 1 and report['orientable']
        and report['consistently_wound'] and not report['boundary_edges']
        and not report['nonmanifold_edges'] and not report['nonmanifold_vertices']
        and not report['loose_vertex_ids'] and not report['loose_edges']
        and report['components'][0]['genus'] == 0
        and report['components'][0]['positive_volume'])
    passed = bool(topology_passed and len(triangle_ids) and not modifiers
                  and not degenerate_ids and not geometric_duplicates and not failures)
    report.update(topology_passed=topology_passed, closed_geometry_passed=passed,
                  passed=passed, visual_acceptance=False)
    return report, vertices, triangle_ids, triangles, tree
