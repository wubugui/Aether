"""Pure reconstruction/GLB inspection; no native launch or GLB modification."""
import json
from pathlib import Path
import sys
import numpy as np
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'source-assets/cloud-bank58/revision-k/normal-readback-v1'))
import guard58k as g
c = g.c


def main():
    verified = c.source_preconditions(); vertices, faces = g.reconstructed_source(verified)
    c.require(c.sha(g.FAILED_GLB) == g.FAILED_GLB_SHA, 'Failed GLB identity')
    document, raw, material = c.parse_glb(g.FAILED_GLB)
    normal_view = document['bufferViews'][document['accessors'][1]['bufferView']]
    normal_begin = normal_view.get('byteOffset', 0); normal_end = normal_begin + normal_view['byteLength']
    normal_nonoverlap = all(index == document['accessors'][1]['bufferView'] or
                           view.get('byteOffset', 0) + view['byteLength'] <= normal_begin or
                           view.get('byteOffset', 0) >= normal_end
                           for index, view in enumerate(document['bufferViews']))
    c.require(normal_nonoverlap, 'NORMAL view does not overlap any other buffer view')
    source = dict(positions=vertices.tolist(), triangles=faces.tolist(), material=dict(
        base_color_linear_rgba=np.asarray([.56, .60, .67, 1], np.float32).astype(float).tolist(),
        roughness=float(np.float32(.9)), metallic=0., double_sided=True))
    material_result = c.validate_material(material, source)
    expected = c.mapped(vertices); v = np.asarray(raw['positions']); n = np.asarray(raw['normals']); ix = np.asarray(raw['indices']).reshape(-1, 3)
    distances = np.max(np.abs(v[:, None] - expected), axis=2); mapping = distances.argmin(axis=1)
    actual = mapping[ix]; by_face = {c.canonical(f): j for j, f in enumerate(faces)}
    c.require(sorted(map(c.canonical, actual)) == sorted(by_face), 'Triangle bijection')
    norm = np.cross(expected[faces[:, 1]] - expected[faces[:, 0]], expected[faces[:, 2]] - expected[faces[:, 0]])
    norm /= np.linalg.norm(norm, axis=1, keepdims=True)
    predicted_source = g.replay_newell(vertices, faces)
    predicted = g.replay_exporter(predicted_source)
    cross_prediction = g.replay_exporter(norm @ c.MAP)
    cyclic_prediction = g.replay_exporter(g.replay_newell(vertices, faces, False))
    rows = []
    for index, (face, idx) in enumerate(zip(actual, ix)):
        native_face = by_face[c.canonical(face)]
        rows.append(dict(export_triangle=index, source_triangle=native_face, source_face=faces[native_face].tolist(),
                         mapped_actual_face=face.tolist(), render_indices=idx.tolist(),
                         glb_normal=n[idx[0]].tolist(), cross_float64_normal=norm[native_face].tolist(),
                         component_error=float(np.max(np.abs(n[idx] - norm[native_face]))),
                         all_corners_equal=np.array_equal(n[idx], np.repeat(n[idx[0]][None, :], 3, axis=0)),
                         predicted_source_normal_float32=predicted_source[native_face].astype(float).tolist(),
                         predicted_export_normal=predicted[native_face].astype(float).tolist(),
                         predicted_export_error=float(np.max(np.abs(n[idx] - predicted[native_face])))))
    def method_summary(pred):
        differences = [float(np.max(np.abs(n[idx] - pred[by_face[c.canonical(face)]]))) for face, idx in zip(actual, ix)]
        return dict(exact_faces=sum(x == 0 for x in differences), max_component_error=max(differences),
                    nonexact_faces=[i for i, x in enumerate(differences) if x != 0])
    try:
        c.validate_geometry(raw, source)
        raise RuntimeError('The original failed contract unexpectedly passed')
    except ValueError as error:
        failure = str(error)
        c.require(failure == 'Flat outward corner normals changed', 'Same original failure')
    addon = c.BLENDER.parent / '4.5/scripts/addons_core/io_scene_gltf2'
    primary = {str(path.relative_to(c.ROOT.parent)): dict(bytes=path.stat().st_size, sha256=c.sha(path)) for path in [addon / '__init__.py', addon / 'blender/exp/primitive_extract.py', addon / 'io/com/constants.py']}
    result = dict(version='cloud58k-normal-diagnosis-20261002', passed=True, diagnosis_only=True,
                  native_readback_performed=False, native_source_normal_proven=False, transfer_passed=False,
                  source_sha256=c.SOURCE_SHA, saved_geometry_fingerprint=verified['native_identity']['mesh'],
                  failed_glb_sha256=c.sha(g.FAILED_GLB), failed_glb_bytes=g.FAILED_GLB.stat().st_size,
                  original_contract_failure=failure, original_normal_epsilon=c.NORMAL_EPS,
                  original_position_epsilon=c.POSITION_EPS, render_vertex_count=len(v), authored_vertex_count=len(vertices), triangle_count=len(faces),
                  maximum_position_error=float(distances[np.arange(len(v)), mapping].max()),
                  authored_positions_all_used=set(mapping) == set(range(194)), render_positions_all_used=set(ix.ravel()) == set(range(len(v))),
                  oriented_triangle_bijection=True, all_triangles_flat=all(row['all_corners_equal'] for row in rows),
                  maximum_unit_error=float(np.max(np.abs(np.linalg.norm(n, axis=1) - 1))),
                  failed_faces=[row['source_triangle'] for row in rows if row['component_error'] > c.NORMAL_EPS],
                  maximum_normal_error=max(row['component_error'] for row in rows), first_failure=next(row for row in rows if row['component_error'] > c.NORMAL_EPS),
                  maximum_error_face=max(rows, key=lambda row: row['component_error']),
                  source_normal_prediction_vs_math_max=float(np.max(np.abs(c.mapped(predicted_source) - norm))),
                  methods=dict(cross_float64_then_round=method_summary(cross_prediction), newell_float32_cyclic_start_then_round=method_summary(cyclic_prediction),
                               newell_float32_last_first_start_then_round=method_summary(predicted)),
                  material_validation=material_result, local_primary_source_identities=primary,
                  official_normal_source='https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenkernel/intern/mesh_normals.cc',
                  official_vector_source='https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenlib/intern/math_vector_inline.cc',
                  normal_accessor=document['accessors'][1], normal_buffer_view=document['bufferViews'][1],
                  normal_buffer_view_nonoverlapping=normal_nonoverlap, native_processes_started=0, images=0, world_loaded=False, per_face=rows)
    c.require(result['methods']['newell_float32_last_first_start_then_round']['exact_faces'] == 384, 'Full numerical replay')
    target = Path(__file__).resolve().parent / 'diagnosis.json'
    c.write(target, result)
    print(json.dumps({key: value for key, value in result.items() if key not in ['per_face', 'first_failure', 'maximum_error_face']}, indent=2))


if __name__ == '__main__':
    main()
