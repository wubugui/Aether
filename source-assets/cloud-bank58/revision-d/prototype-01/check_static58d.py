"""Inspect the saved context-rebuilt D cage without Blender or mesh repair.

The input JSON, not a rebuilt mesh or a bounding box, is the checked geometry.
Every overlapping triangle AABB is narrow-phase tested, including adjacent
faces. Only contact confined to the actual common indexed simplex is allowed.
This is a static source check; it establishes no visual or world acceptance.
"""
import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time
from types import ModuleType

import numpy as np

HERE = Path(__file__).resolve().parent
BANK = HERE.parents[1]
ROOT = BANK.parents[1]
PLAN = HERE.parent / "control-plan58d.json"
CAGE = HERE / "native-cage-input58d.json"
TOPOLOGY = BANK / "revision-c/recovery-02/native_geometry58c.py"
NARROW = BANK / "revision-b/recovery-03/triangle_pairs58b.py"
RAYS = BANK / "revision-c/recovery-02/triangle_checks58c.py"
C_FREEZE = BANK / "revision-c-complete-freeze-20261001T1305Z.json"
CONTACT_EPS = 1e-5


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {k: native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [native(v) for v in value]
    return value


def write(path, value):
    path.write_text(json.dumps(native(value), indent=2, allow_nan=False) + "\n")


def load_pure(path):
    module = ModuleType(path.stem + "_read_only_d")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def volume(vertices, faces):
    tri = vertices[faces]
    return float(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6)


def load_topology():
    # Execute only the existing pure topology function, never its Blender path.
    node = next(n for n in ast.parse(TOPOLOGY.read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name == "_topology")
    scope = dict(defaultdict=defaultdict, np=np, math=math, volume=volume,
                 VOLUME_EPSILON_M3=1e-9)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(TOPOLOGY), "exec"), scope)
    return scope["_topology"]


def common_simplex_contact(result, common):
    if result["classification"] in {"separated_by_triangle_plane", "coplanar_disjoint", "noncoplanar_disjoint"}:
        return True, "disjoint"
    if result["classification"] in {"degenerate_input", "coplanar_area_overlap"}:
        return False, "degenerate_or_positive_area_overlap"
    points = np.asarray(result["points"], float)
    if not len(points) or not len(common) or len(common) > 2:
        return False, "no_legal_common_indexed_simplex"
    if len(common) == 1:
        distances = np.linalg.norm(points - common[0], axis=1)
    else:
        edge = common[1] - common[0]
        t = np.clip((points - common[0]) @ edge / (edge @ edge), 0, 1)
        distances = np.linalg.norm(points - (common[0] + t[:, None] * edge), axis=1)
    valid = bool(np.all(distances <= CONTACT_EPS))
    return valid, "confined_to_common_indexed_simplex" if valid else "contact_extends_beyond_shared_vertex_or_edge"


def checker_examples(helper):
    count = helper.counterexamples()
    a = np.array([[0., 0., 0.], [2., 0., 0.], [0., 2., 0.]])
    cases = [
        ("legal_common_edge", np.array([[0., 0., 0.], [2., 0., 0.], [0., -2., 1.]]), a[:2], True),
        ("legal_common_vertex", np.array([[0., 0., 0.], [-2., 0., 1.], [0., -2., 1.]]), a[:1], True),
        ("adjacent_vertex_fold_through", np.array([[0., 0., 0.], [1., 1., -1.], [1., 1., 1.]]), a[:1], False),
        ("coplanar_adjacent_area_overlap", np.array([[0., 0., 0.], [2., 0., 0.], [1., 1., 0.]]), a[:2], False),
        ("nonindexed_touch_is_not_welded", np.array([[0., 0., 0.], [-2., 0., 1.], [0., -2., 1.]]), [], False),
    ]
    rows = []
    for name, b, common, expect in cases:
        result = helper.narrow_phase(a, b)
        passed, reason = common_simplex_contact(result, np.asarray(common))
        assert passed == expect, (name, result, reason)
        rows.append(dict(name=name, expected_allowed=expect, actual_allowed=passed, classification=result["classification"]))
    return dict(frozen_helper_counterexamples=count, indexed_contact_cases=rows, passed=True)


def intersections(vertices, faces, helper):
    tri = vertices[faces]
    low, high = tri.min(axis=1), tri.max(axis=1)
    classifications = Counter()
    failures, count, adjacent, allowed = [], 0, 0, 0
    for i in range(len(tri)):
        candidates = np.flatnonzero(np.all(high[i] + helper.EPS >= low[i+1:], axis=1)
                                   & np.all(high[i+1:] + helper.EPS >= low[i], axis=1)) + i + 1
        for j0 in candidates:
            j = int(j0)
            count += 1
            shared = sorted(set(faces[i]) & set(faces[j]))
            adjacent += bool(shared)
            origin = tri[i, 0]
            result = helper.narrow_phase(tri[i] - origin, tri[j] - origin)
            if result["points"]:
                result["points"] = (np.asarray(result["points"]) + origin).tolist()
            classifications[result["classification"]] += 1
            okay, reason = common_simplex_contact(result, vertices[shared])
            allowed += okay and reason == "confined_to_common_indexed_simplex"
            if not okay:
                failures.append(dict(triangle_ids=[i, j], shared_vertex_ids=shared, reason=reason,
                                     triangle_a_world=tri[i].tolist(), triangle_b_world=tri[j].tolist(), **result))
    return dict(passed=not failures, tested_aabb_candidate_pairs=count, tested_adjacent_pairs=adjacent,
                excluded_adjacent_pairs=0, permitted_common_simplex_contacts=allowed,
                classification_counts=dict(classifications), failure_count=len(failures), failures=failures,
                narrow_phase_epsilon_m=helper.EPS, common_simplex_contact_epsilon_m=CONTACT_EPS,
                method="All unique AABB candidates including indexed adjacency; actual triangle-plane/clipping intersections. Ordinary indexed shared edge/vertex contact alone is allowed.")


def shared_controls(mesh, plan):
    local = np.asarray(mesh["local_uv_worldY"], float)
    curves = {c["id"]: c for c in plan["curves"]}
    active = [c for c in plan["curves"] if c["role"] in {"primary", "medium"}]
    faces = np.asarray(mesh["faces"], int)
    actual_edges = {tuple(sorted((int(a), int(b)))) for f in faces for a, b in zip(f, np.roll(f, -1))}
    constraints = mesh["upper_constraints"]
    absent_edges = [e for e in constraints if tuple(sorted(e)) not in actual_edges]
    segments, knots = [], []
    for curve in active:
        pts = np.asarray(curve["knots_local_uv_and_worldY_m"], float)
        for i, q in enumerate(pts):
            ids = np.flatnonzero(np.linalg.norm(local - q, axis=1) <= 1e-6).tolist()
            knots.append(dict(curve=curve["id"], knot=i, native_vertex_ids=ids, passed=len(ids) == 1))
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            delta = b - a
            t = (local - a) @ delta / (delta @ delta)
            close = np.linalg.norm(local - (a + t[:, None] * delta), axis=1) < 1e-6
            pieces = []
            for edge in constraints:
                if all(close[v] and -1e-8 <= t[v] <= 1 + 1e-8 for v in edge):
                    pieces.append(dict(interval=sorted(t[edge].tolist()), vertex_ids=edge))
            cursor, gaps = 0., []
            for piece in sorted(pieces, key=lambda p: p["interval"]):
                begin, end = piece["interval"]
                if begin > cursor + 1e-7:
                    gaps.append([cursor, begin])
                cursor = max(cursor, end)
            if cursor < 1 - 1e-7:
                gaps.append([cursor, 1.])
            segments.append(dict(curve=curve["id"], segment=i, pieces=pieces, gaps=gaps, passed=not gaps))
    junctions = []
    for curve in plan["curves"]:
        if "shared_parent_junction" not in curve:
            continue
        j = curve["shared_parent_junction"]
        parent = np.asarray(curves[j["parent_curve"]]["knots_local_uv_and_worldY_m"], float)
        expect = parent[j["parent_segment"]] + j["parameter"] * (parent[j["parent_segment"]+1] - parent[j["parent_segment"]])
        actual = np.asarray(curve["knots_local_uv_and_worldY_m"][0], float)
        ids = np.flatnonzero(np.linalg.norm(local - actual, axis=1) < 1e-6).tolist()
        materialized = curve["role"] in {"primary", "medium"}
        passed = np.linalg.norm(actual - expect) < 1e-8 and (len(ids) == 1 if materialized else True)
        junctions.append(dict(child=curve["id"], parent=j["parent_curve"], error_m=float(np.linalg.norm(actual-expect)),
                              active_in_cage=materialized, native_vertex_ids=ids, passed=bool(passed)))
    return dict(passed=not absent_edges and all(r["passed"] for r in knots + segments + junctions),
                primary_curve_count=3, medium_curve_count=8, guide_only_small_count=12,
                absent_constrained_edges=absent_edges, authored_knots=knots, constrained_segments=segments,
                shared_parent_junctions=junctions,
                side_and_belly_note="Six U curves drive weighted folded side rings; three B curves constrain the underside. They are not asserted to be exact U curve surface traces.")


def geometry(vertices, faces, topology_fn, helper):
    report = topology_fn(vertices, faces)
    tri = vertices[faces]
    areas = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1) * .5
    degenerate = np.flatnonzero(areas <= 1e-8).tolist()
    duplicate = defaultdict(list)
    for i, t in enumerate(tri):
        duplicate[tuple(sorted(tuple(p) for p in t))].append(i)
    duplicate = [ids for ids in duplicate.values() if len(ids) > 1]
    report.update(vertices=len(vertices), triangles=len(faces), world_bounds=[vertices.min(0), vertices.max(0)],
                  degenerate_triangle_ids=degenerate, duplicate_geometric_triangle_groups=duplicate,
                  minimum_triangle_area_m2=float(areas.min()), intersections=intersections(vertices, faces, helper))
    topology_ok = (report["component_count"] == 1 and report["orientable"] and report["consistently_wound"]
                   and not report["nonmanifold_edges"] and not report["nonmanifold_vertices"]
                   and not report["loose_vertex_ids"] and not report["loose_edges"]
                   and report["components"][0]["genus"] == 0 and report["components"][0]["positive_volume"]
                   and not degenerate and not duplicate)
    report["topology_passed"] = bool(topology_ok)
    report["passed"] = bool(topology_ok and report["intersections"]["passed"])
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    paths = [*sorted(HERE.parent.rglob("*.py")), PLAN, CAGE, HERE.parent / "CONTEXT_REBUILD58D.md", TOPOLOGY, NARROW, RAYS, C_FREEZE]
    inputs = {str(p.relative_to(ROOT)): dict(sha256=sha(p), bytes=p.stat().st_size) for p in dict.fromkeys(paths)}
    write(args.output / "input-sha256.json", inputs)
    write(args.output / "process-report.json", dict(status="running", passed=False, started_utc=datetime.now(timezone.utc).isoformat()))
    helper, rays, topology_fn = load_pure(NARROW), load_pure(RAYS), load_topology()
    examples = checker_examples(helper)
    mesh, plan = json.loads(CAGE.read_text()), json.loads(PLAN.read_text())
    vertices, faces = np.asarray(mesh["vertices"], float), np.asarray(mesh["faces"], int)
    assert vertices.shape == (325, 3) and faces.shape == (646, 3), "Scope differs from saved 325/646 cage"
    assert np.isfinite(vertices).all() and faces.min() >= 0 and faces.max() < len(vertices)
    controls = shared_controls(mesh, plan)
    original = geometry(vertices, faces, topology_fn, helper)
    corridors = [dict(id=c["id"], xz=np.asarray(c["knots_godot_world_xyz_m"])[:, [0, 2]].tolist(),
                      half_width_m=c["half_width_m"], intended_floor_y_range_m=c["first_surface_worldY_band_m"])
                 for c in plan["valley_controls"]]
    assert all(c["station_spacing_m"] == 25 and c["first_solid_interval_minimum_m"] == 160 for c in plan["valley_controls"])
    valley = rays.valley_report(vertices[faces], corridors)
    # A separate sensitivity check, not a claim that Blender has stored these.
    origin = np.asarray(plan["anchor_godot_world_xyz"], float)
    rounded = (vertices - origin).astype(np.float32).astype(np.float64) + origin
    prospective = geometry(rounded, faces, topology_fn, helper)
    rounded_valley = rays.valley_report(rounded[faces], corridors)
    unchanged = all(sha(ROOT / path) == row["sha256"] for path, row in inputs.items())
    frozen_c = json.loads(C_FREEZE.read_text())["files"]
    c_rows = []
    for path, expected in frozen_c.items():
        p = ROOT / path
        c_rows.append(dict(path=path, exists=p.exists(), matched=p.exists() and sha(p) == expected["sha256"]))
    c_match = all(r["matched"] for r in c_rows)
    passed = original["passed"] and controls["passed"] and valley["passed"] and prospective["passed"] and rounded_valley["passed"] and unchanged and c_match
    report = dict(status="passed" if passed else "failed", passed=bool(passed), reconstructed_after_workspace_reset=True,
                  scope="Static inspection of the saved 325 vertex / 646 triangle D prototype only; no model edits",
                  checked_geometry="Actual saved JSON world vertices and faces in float64; no regeneration or inferred volume",
                  checker_counterexamples=examples, actual_saved_geometry=original, shared_controls=controls,
                  actual_valleys=valley, prospective_float32_geometry=prospective,
                  prospective_float32_valleys=rounded_valley,
                  prospective_float32_note="Round each coordinate relative to D anchor to float32, then promote. This is sensitivity only, not a Blender readback.",
                  prospective_max_vertex_shift_m=float(np.linalg.norm(rounded-vertices, axis=1).max()),
                  inputs_unchanged=unchanged, protected_c=dict(manifest=str(C_FREEZE.relative_to(ROOT)), count=len(c_rows), all_matched=c_match, failures=[r for r in c_rows if not r["matched"]]),
                  valley_sample_limit="25m stations plus endpoints, three transverse lanes. Not a proof for every continuous point of the full band or flight corridor.",
                  visual_acceptance=False, blender_started=False, world_loaded=False,
                  elapsed_seconds=time.monotonic()-start, maximum_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    write(args.output / "static-proof58d.json", report)
    code = 0 if passed else 1
    write(args.output / "process-report.json", dict(status="completed", passed=bool(passed), exit_code=code,
          elapsed_seconds=report["elapsed_seconds"], maximum_rss_kib=report["maximum_rss_kib"],
          proof_sha256=sha(args.output / "static-proof58d.json"), finished_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(dict(passed=bool(passed), actual_topology=original["topology_passed"],
                         actual_intersections=original["intersections"]["failure_count"], shared_controls=controls["passed"],
                         valleys=[dict(id=c["id"], passing=c["passing_samples"], count=c["sample_count"]) for c in valley["corridors"]],
                         prospective_intersections=prospective["intersections"]["failure_count"], inputs_unchanged=unchanged,
                         c_unchanged=c_match, elapsed_seconds=report["elapsed_seconds"], maximum_rss_kib=report["maximum_rss_kib"])))
    return code


if __name__ == "__main__":
    sys.exit(main())
