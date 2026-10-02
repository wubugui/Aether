"""Read only the four relevant cloud nodes and their two saved mesh resources."""
from pathlib import Path
import base64
import hashlib
import json
import re
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROJECT = ROOT / 'candidates/round40-exclusive-20260930/project'
NATIVE = ROOT / 'cloud-evidence/cloudbank58k-cache-readback-v3-20261002T103637Z-zfmq_a2d'
SCENE = PROJECT / 'scenes/candidate53d-west/Game53dWest.tscn'
ANCHOR = np.array([3958, 0, 3667], dtype=np.float32)
SELECTED = 'CloudSea_1_1'
NEIGHBORS = ['CloudSea_0_0', 'CloudSea_0_1', 'CloudSea_1_0', SELECTED]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def need(v, why):
    if not v:
        raise ValueError(why)


def block(text, prefix):
    start = text.index(prefix)
    end = text.find('\n[', start + 1)
    return text[start:end if end >= 0 else len(text)]


def array(block_text, key):
    return base64.b64decode(re.search('"' + key + '": PackedByteArray\\("([A-Za-z0-9+/=]+)"\\)', block_text)[1], validate=True)


def decode_clouds():
    text = SCENE.read_text()
    result = {}
    for name in NEIGHBORS:
        rb = block(text, '[node name="' + name + '" type="Node3D" parent="SkyRegion39"]')
        transform = np.array([float(x) for x in re.search(r'Transform3D\((.*?)\)', rb)[1].split(',')], np.float32)
        pattern = r'\[node name="([^"]+)" type="MeshInstance3D" parent="SkyRegion39/' + name + r'"\]'
        children = list(re.finditer(pattern, text))
        need(len(children) == 1, 'Exactly one actual current-61 cloud mesh per selected root')
        node = block(text, children[0][0])
        mesh_id = re.search(r'mesh = SubResource\("(.*?)"\)', node)[1]
        mb = block(text, '[sub_resource type="ArrayMesh" id="' + mesh_id + '"]')
        material_id = re.search(r'material_override = SubResource\("(.*?)"\)', node)[1]
        material = block(text, '[sub_resource type="StandardMaterial3D" id="' + material_id + '"]')
        number = lambda k: int(re.search('"' + k + '": (\\d+)', mb)[1])
        fmt, n, ni = number('format'), number('vertex_count'), number('index_count')
        need(fmt == 34896613391 and number('primitive') == 3, 'Fixed compressed V/N/T/color/index surface schema')
        bounds = np.array([float(x) for x in re.search(r'"aabb": AABB\((.*?)\)', mb)[1].split(',')], np.float32)
        vdata, idata = array(mb, 'vertex_data'), array(mb, 'index_data')
        need(len(vdata) == n * 12 and len(idata) == ni * 2 and ni % 3 == 0, 'Fixed saved payload layout')
        q = np.frombuffer(vdata[:n * 8], '<u2').reshape(n, 4)[:, :3]
        vertices = (q.astype(np.float32) / np.float32(65535) * bounds[3:] + bounds[:3]).astype(np.float32)
        indices = np.frombuffer(idata, '<u2').reshape(-1, 3)
        need(int(indices.max()) < n, 'Index range')
        basis = transform[:9].reshape(3, 3).T
        # Float64 world arithmetic is explicit: these are offline geometric
        # estimates, not a claim that a new native API returned these vertices.
        world = vertices.astype(float) @ basis.astype(float).T + transform[9:].astype(float)
        result[name] = dict(path='SkyRegion39/' + name + '/' + children[0][1],
            root_transform=transform.astype(float).tolist(), mesh_id=mesh_id,
            vertex_count=n, index_count=ni, format=fmt,
            vertex_data_sha256=hashlib.sha256(vdata).hexdigest(), index_data_sha256=hashlib.sha256(idata).hexdigest(),
            material_block=material.strip(), node_block=node.strip(),
            world_bounds=[world.min(0).tolist(), world.max(0).tolist()],
            root_anchor_distance_xz_m=float(np.linalg.norm(transform[9:][[0, 2]] - ANCHOR[[0, 2]])),
            triangles=world[indices])
    return result


def ray_hits(origin, target, triangles):
    """Diagnostic Moller-Trumbore samples; never a geometry-acceptance gate."""
    direction = target - origin
    limit = float(np.linalg.norm(direction))
    direction /= limit
    a = triangles[:, 0]; e1 = triangles[:, 1] - a; e2 = triangles[:, 2] - a
    p = np.cross(direction, e2); det = np.einsum('ij,ij->i', e1, p)
    valid = np.abs(det) > 1e-10
    inv = np.divide(1, det, out=np.zeros_like(det), where=valid)
    delta = origin - a
    u = np.einsum('ij,ij->i', delta, p) * inv
    q = np.cross(delta, e1); v = q @ direction * inv
    dist = np.einsum('ij,ij->i', e2, q) * inv
    valid &= (u >= 0) & (v >= 0) & (u+v <= 1) & (dist > 0) & (dist < limit - 1e-7)
    return float(dist[valid].min()) if valid.any() else None


def analyze():
    need(sha(NATIVE/'roundtrip.tscn') == '91ab3412c67b5f82449396677a30a9bbe1542a338c00150dc1822910cdf7f789', 'Successful native K scene identity')
    native = json.loads((NATIVE/'native-reload.json').read_text())
    p = np.array(native['geometry']['positions'], float) + ANCHOR
    indices = np.array(native['geometry']['indices']).reshape(-1, 3)
    kt = p[indices]; center = (p.min(0) + p.max(0))/2
    clouds = decode_clouds()
    need(min(clouds, key=lambda x: clouds[x]['root_anchor_distance_xz_m']) == SELECTED, 'Explicit nearest-root design selection')
    front = np.array([3000, 1150, 4300], float)
    samples = kt.mean(1)
    sample_rows = []
    for i, target in enumerate(samples):
        self_hidden = ray_hits(front, target, np.concatenate([kt[:i], kt[i+1:]])) is not None
        hits = [name for name, row in clouds.items() if ray_hits(front, target, row['triangles']) is not None]
        sample_rows.append(dict(face=i, self_hidden=self_hidden, old_cloud_hits=hits,
            clear_after_single_replacement=not self_hidden and not any(name != SELECTED for name in hits)))
    for name, row in clouds.items():
        lo, hi = np.array(row['world_bounds'])
        gap = np.maximum(np.maximum(lo-p.max(0), p.min(0)-hi), 0)
        row['aabb_gap_m'] = float(np.linalg.norm(gap))
        row['k_aabb_contained'] = bool(np.all(p.min(0) >= lo) and np.all(p.max(0) <= hi))
        row['front_ray_to_k_bounds_center_first_hit_m'] = ray_hits(front, center, row['triangles'])
        row['k_triangle_centroid_segments_blocked'] = sum(ray_hits(front, target, row['triangles']) is not None for target in samples)
        del row['triangles']
    frame = json.loads((HERE.parent/'import-v1/basis-provenance58k.json').read_text())
    old_lo, old_hi = np.array(clouds[SELECTED]['world_bounds'])
    k_span = p.max(0)-p.min(0); old_span = old_hi-old_lo
    design = json.loads((HERE.parent.parent/'revision-d/control-plan58d.json').read_text())
    cam = np.array(design['camera']['camera_transform'])
    camera_points = (p-cam[9:]) @ np.linalg.inv(cam[:9].reshape(3,3).T).T
    f = 1/np.tan(np.deg2rad(62)/2)
    ndc = camera_points[:,:2]/-camera_points[:,2,None] * [f/(1180/664),f]
    screen = (ndc+1)/2*[1180,664]; screen[:,1] = 664-screen[:,1]
    return dict(version='cloud58k-world-trial-v1', native_acceptance='source-bound saved/fresh-reloaded asset only',
        inherited_scene='res://scenes/candidate61-coast/Game61Coast.tscn',
        current_cloud_source=str(SCENE.relative_to(ROOT)), current_cloud_source_sha256=sha(SCENE),
        historical_52f_is_not_current_61=True, selected_root=SELECTED,
        selection_basis='New bounded design choice: closest of four original roots to the unchanged K world anchor; no historical unique-root claim',
        anchor_world_xyz=ANCHOR.tolist(), world_basis=[[1,0,0],[0,1,0],[0,0,1]],
        apply_local_uv_again=False, recenter=False, scale=[1,1,1],
        placement='CloudKTrial under identity SkyRegion39; identity basis plus anchor, outside old root rotation',
        k_world_bounds=[p.min(0).tolist(),p.max(0).tolist()],
        current_clouds=clouds, original_front_position=front.tolist(),
        coverage_mismatch=dict(old_world_span_xyz=old_span.tolist(), k_world_span_xyz=k_span.tolist(),
          k_to_old_span_ratio_xyz=(k_span/old_span).tolist(), k_to_old_xz_aabb_area_ratio=float(k_span[0]*k_span[2]/old_span[0]/old_span[2]),
          suitability_proven=False, warning='Only about 7.49% of old XZ AABB area; replacing this bank unit may open a conspicuous gap. Bounds containment is not semantic equivalence.'),
        original_front_projected_k=dict(pixel_bounds=[screen.min(0).tolist(),screen.max(0).tolist()],
          resolution=[1180,664],fov_degrees=62,depth_range_m=[float((-camera_points[:,2]).min()),float((-camera_points[:,2]).max())],
          all_vertices_in_front=bool(np.all(camera_points[:,2]<0)),
          self_clear_centroid_samples=sum(not r['self_hidden'] for r in sample_rows),
          clear_centroid_samples_after_single_replacement=sum(r['clear_after_single_replacement'] for r in sample_rows),
          samples=sample_rows, pixel_coverage_proven=False,
          caveat='A limited nonzero open sample set means not fully buried in these four fixed meshes; other world geometry and actual pixels remain untested.'),
        diagnostic_scope='Four relevant current-61 meshes/two fixed compressed resources, offline indexed triangle segment samples. Not all-world visibility, actual pixel coverage, minimum surface distance, or native readback.',
        material=dict(k_actual=native['material'], k_diffuse_mode='Burley default (0), no property serialized',
          k_vertex_color_use_as_albedo=False, k_roughness=native['material']['roughness'],
          old_diffuse_mode='Lambert wrap (2)', old_vertex_color_use_as_albedo=True,
          old_roughness='1.0 default, not serialized', old_albedo='white default multiplied by packed vertex colors',
          common='Opaque, two-sided, per-pixel StandardMaterial; shared World3D Sun/ambient/fog and spatial lightning',
          retained='K actual authored material; old shared override is not assigned to K',
          weather='SceneEnvironment42b registers ShaderMaterial only; StandardMaterial is lit by shared native environment. cloud_tint is not applied to these StandardMaterial instances.'),
        inherited_source_frame=frame['source_frame'], world_loaded=False, images=0, visual_acceptance=False)


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2, allow_nan=False))
