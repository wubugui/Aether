"""Read saved text and previously exported native arrays; never invoke Godot."""
from pathlib import Path
import base64, collections, hashlib, json, re
import numpy as np
from read_multimesh_binary import read_multimesh

D = Path(__file__).resolve().parent
R = Path('/workspace/scratch/a29d03198654/Aether')
P = R / 'candidates/round40-exclusive-20260930/project'
OLD = R / 'cloud-evidence/coast-boundary-readonly-20261001'
BOX = [-3440., -3090., -3816., -3430.]
TARGET = 'Ground_-5_-5'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
raw = json.loads((OLD / 'native-coast.json').read_text())
source = P / 'scenes/candidate53d-west/Game53dWest.tscn'
assert sha(source) == raw['source_sha256']
text = source.read_text()
blocks = re.split(r'\n(?=\[(?:node|sub_resource|ext_resource) )', text)
resources = {}
external_resources = {}
nodes = {}
for b in blocks:
    h = b.split('\n', 1)[0]
    if h.startswith('[sub_resource '):
        resources[re.search(r'id="([^"]+)"', h)[1]] = b
    if h.startswith('[ext_resource '):
        external_resources[re.search(r'id="([^"]+)"',h)[1]] = re.search(r'path="([^"]+)"',h)[1]
    if not h.startswith('[node '):
        continue
    name = re.search(r'name="([^"]+)"', h)[1]
    pm = re.search(r'parent="([^"]+)"', h)
    path = name if pm is None else (name if pm[1] == '.' else pm[1] + '/' + name)
    if pm is None:
        path = '.'
    nodes[path] = b

def local_transform(b):
    m = re.search(r'^transform = Transform3D\(([^)]+)\)', b, re.M)
    t = np.eye(4, dtype=np.float32)
    if m:
        a = np.fromstring(m[1], sep=',', dtype=np.float32)
        t[:3, :3] = a[:9].reshape(3, 3).T
        t[:3, 3] = a[-3:]
    return t

global_transforms = {}
def global_transform(path):
    if path in global_transforms:
        return global_transforms[path]
    assert path in nodes, 'Missing ancestor: ' + path
    local = local_transform(nodes[path])
    parent = path.rsplit('/', 1)[0] if '/' in path else '.'
    g = local if path == '.' else global_transform(parent) @ local
    global_transforms[path] = g.astype(np.float32)
    return global_transforms[path]

def box_hits(a, b, box=BOX):
    return bool(b[0] >= box[0] and a[0] <= box[1] and b[2] >= box[2] and a[2] <= box[3])

def box_distance(a, b):
    dx = max(BOX[0] - b[0], a[0] - BOX[1], 0.)
    dz = max(BOX[2] - b[2], a[2] - BOX[3], 0.)
    return float(np.hypot(dx, dz))

terr = {m['node'].split('/')[-1]: m for m in raw['terrain']}
tris = {k: np.array(m['faces'], dtype=np.float32).reshape(-1, 3, 3) for k, m in terr.items()}
cols = {m['node'].split('/')[-3]: np.array(m['faces'], dtype=np.float32).reshape(-1, 3, 3) for m in raw['collision']}
tri = tris[TARGET]
def height(t, x, z):
    a = t[:, 0].astype(float)
    u = t[:, 1].astype(float) - a
    v = t[:, 2].astype(float) - a
    qx, qz = x - a[:, 0], z - a[:, 2]
    det = u[:, 0] * v[:, 2] - u[:, 2] * v[:, 0]
    ok = abs(det) > 1e-8
    s = np.divide(qx*v[:, 2] - qz*v[:, 0], det, out=np.zeros(len(t)), where=ok)
    w = np.divide(u[:, 0]*qz - u[:, 2]*qx, det, out=np.zeros(len(t)), where=ok)
    ids = np.flatnonzero(ok & (s >= -1e-7) & (w >= -1e-7) & (s+w <= 1+1e-7))
    if not len(ids):
        return None
    i = ids[0]
    return {'triangle': int(i), 'y': float(a[i, 1]+s[i]*u[i, 1]+w[i]*v[i, 1])}

scatter = []
mm_scanned = instance_scanned = 0
missing = []
external_authority = []
for path, b in nodes.items():
    h = b.split('\n', 1)[0]
    if 'type="MultiMeshInstance3D"' not in h:
        continue
    mm_scanned += 1
    mid = re.search(r'^multimesh = SubResource\("([^"]+)"\)', b, re.M)
    if mid:
        rb = resources[mid[1]]
        cm = re.search(r'^instance_count = (\d+)', rb, re.M)
        bm = re.search(r'^buffer = PackedFloat32Array\(([^)]+)\)', rb, re.M)
        count = int(cm[1]) if cm else 0
        buf = np.fromstring(bm[1], sep=',', dtype=np.float32) if bm else np.empty(0,dtype=np.float32)
        transform_format = 1 if re.search(r'^transform_format = 1$',rb,re.M) else 0
        stride = 12 + 4*bool(re.search(r'^use_colors = true$',rb,re.M)) + 4*bool(re.search(r'^use_custom_data = true$',rb,re.M))
        resource_id = mid[1]
    else:
        eid = re.search(r'^multimesh = ExtResource\("([^"]+)"\)',b,re.M)
        assert eid, path
        resource_id = external_resources[eid[1]]
        ep = P/resource_id.removeprefix('res://')
        props = read_multimesh(ep)
        count = props.get('instance_count',0)
        buf = props.get('buffer',np.empty(0,dtype=np.float32))
        transform_format = props.get('transform_format',0)
        stride = 12 + 4*props.get('use_colors',False) + 4*props.get('use_custom_data',False)
        external_authority.append({'node':path,'path':resource_id,'sha256':sha(ep),'instance_count':count,'buffer_float_count':len(buf),'full_buffer_sha256':hashlib.sha256(buf.astype('<f4').tobytes()).hexdigest()})
    instance_scanned += count
    if count == 0:
        continue
    assert transform_format == 1, path
    assert len(buf) == count*stride, (path, count, len(buf), stride)
    a = buf.reshape(count, stride)
    g = global_transform(path)
    roots = (a[:, [3, 7, 11]] @ g[:3, :3].T + g[:3, 3]).astype(np.float32)
    selected = np.flatnonzero((roots[:, 0] >= BOX[0]) & (roots[:, 0] <= BOX[1]) & (roots[:, 2] >= BOX[2]) & (roots[:, 2] <= BOX[3]))
    if not len(selected):
        continue
    km = re.search(r'^metadata/asset_kind = "([^"]+)"', b, re.M)
    rows = []
    for i in selected:
        x, y, z = map(float, roots[i]); mh = height(tri, x, z); ch = height(cols[TARGET], x, z)
        rows.append({'index': int(i), 'world_position': [x,y,z], 'original_buffer': a[i].tolist(), 'mesh_support': mh, 'shape_support': ch, 'root_minus_mesh': y-mh['y'] if mh else None})
    scatter.append({'node': path, 'kind': km[1] if km else None, 'multimesh_id': resource_id, 'group_total': count, 'group_world_transform': g.tolist(), 'full_original_buffer_sha256': hashlib.sha256(buf.astype('<f4').tobytes()).hexdigest(), 'instances': rows})

# A triangle belongs to the possible interior pool only when all corners lie in the box.
inside_vertices = (tri[:, :, 0] >= BOX[0]) & (tri[:, :, 0] <= BOX[1]) & (tri[:, :, 2] >= BOX[2]) & (tri[:, :, 2] <= BOX[3])
inside_faces = np.all(inside_vertices, axis=1)
overlap_aabb = (tri[:, :, 0].max(1) >= BOX[0]) & (tri[:, :, 0].min(1) <= BOX[1]) & (tri[:, :, 2].max(1) >= BOX[2]) & (tri[:, :, 2].min(1) <= BOX[3])
boundary_cross = overlap_aabb & ~inside_faces
contour = []
for i,t in enumerate(tri):
    hits = []
    for a,b in zip(t, np.roll(t,-1,axis=0)):
        if (a[1] <= 0 < b[1]) or (b[1] <= 0 < a[1]):
            p = a.astype(float) + (b.astype(float)-a.astype(float)) * (-float(a[1])/(float(b[1])-float(a[1])))
            hits.append(p.tolist())
    if len(hits) == 2:
        contour.append({'triangle': i, 'points': hits})
points = np.array([p for row in contour for p in row['points']])
points = points[(points[:,0] >= BOX[0]) & (points[:,0] <= BOX[1]) & (points[:,2] >= BOX[2]) & (points[:,2] <= BOX[3])]
coef = np.polyfit(points[:,2], points[:,0], 1)
res = points[:,0] - np.polyval(coef, points[:,2])

unique, inverse = np.unique(tri.reshape(-1,3), axis=0, return_inverse=True)
faces = inverse.reshape(-1,3)
edges = collections.Counter(tuple(sorted((int(a),int(b)))) for f in faces for a,b in zip(f,np.roll(f,-1)))
boundary = [(a,b) for (a,b),n in edges.items() if n == 1]
seams = []
for axis, value, neighbor in [(0,-3840.,'Ground_-6_-5'),(0,-3072.,'Ground_-4_-5'),(2,-3840.,'Ground_-5_-6'),(2,-3072.,'Ground_-5_-4')]:
    a = unique[unique[:,axis] == value]
    other = np.unique(tris[neighbor].reshape(-1,3),axis=0)
    b = other[other[:,axis] == value]
    tangent = 2 if axis == 0 else 0
    aa = {float(p[tangent]):float(p[1]) for p in a}; bb = {float(p[tangent]):float(p[1]) for p in b}
    common = sorted(set(aa)&set(bb))
    seams.append({'axis':axis,'value':value,'neighbor':neighbor,'target_boundary_vertices':len(a),'neighbor_boundary_vertices':len(b),'exact_common_horizontal_coordinates':len(common),'common_coordinate_max_height_difference':max((abs(aa[k]-bb[k]) for k in common),default=None)})

other = []
for m in raw['other_meshes']:
    row = dict(m); row['distance_xz_to_box'] = box_distance(m['min'],m['max'])
    other.append(row)
other.sort(key=lambda m:m['distance_xz_to_box'])
routes = []
for path,b in nodes.items():
    if 'type="Path3D"' not in b.split('\n',1)[0]:
        continue
    rid = re.search(r'^curve = SubResource\("([^"]+)"',b,re.M)[1]
    points = np.fromstring(re.search(r'"points": PackedVector3Array\(([^)]+)\)',resources[rid])[1],sep=',',dtype=np.float32).reshape(-1,3,3)
    controls = np.concatenate([points[:,2],points[:,2]+points[:,0],points[:,2]+points[:,1]])
    g = global_transform(path); world_controls = controls@g[:3,:3].T+g[:3,3]
    width = float(re.search(r'^metadata/width_metres = ([^\n]+)',b,re.M)[1])
    amin = world_controls.min(0)-width/2; amax=world_controls.max(0)+width/2
    routes.append({'node':path,'curve':rid,'width':width,'bezier_control_hull_bounds_including_width':[amin.tolist(),amax.tolist()],'intersects_box':box_hits(amin,amax),'distance_xz_to_box_lower_bound':box_distance(amin,amax)})
target_node = 'World/Terrain/'+TARGET+'/Model/'+TARGET
mb = nodes[target_node]
mesh_id = re.search(r'^mesh = SubResource\("([^"]+)"',mb,re.M)[1]
mesh = resources[mesh_id]
shape_node = 'World/Terrain/'+TARGET+'/Collision/Shape'
shape_id = re.search(r'^shape = SubResource\("([^"]+)"',nodes[shape_node],re.M)[1]
fields = {}
for field in ['vertex_count','index_count','format','aabb','lods','shadow_mesh']:
    m = re.search(r'^"?'+field+r'"?:? =? ?(.*)$',mesh,re.M)
    fields[field] = m[1] if m else None
for field in ['vertex_data','attribute_data','index_data']:
    m = re.search(r'^"'+field+r'": PackedByteArray\("([^"]*)"\)',mesh,re.M)
    if m:
        by = base64.b64decode(m[1]); fields[field] = {'bytes':len(by),'sha256':hashlib.sha256(by).hexdigest()}
authority = {
    'source_world_path':str(source.relative_to(R)), 'source_world_sha256':sha(source),
    'native_export_path':str((OLD/'native-coast.json').relative_to(R)), 'native_export_sha256':sha(OLD/'native-coast.json'),
    'mesh_id':mesh_id, 'shape_id':shape_id, 'mesh_block_sha256':hashlib.sha256(mesh.encode()).hexdigest(), 'shape_block_sha256':hashlib.sha256(resources[shape_id].encode()).hexdigest(),
    'mesh_fields':fields, 'world_bounds':[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],
    'source_export_method':'surface_get_arrays indexed native geometry, transformed to float32 world coordinates; direct Shape.get_faces; prior outside-tree CPU export, not Mesh.get_faces or new engine run',
    'current_inheritance':'56 -> 55 -> saved53; neither 55 nor 56 overrides this tile or its scatter groups',
    'inherited_scene_hashes':{p:sha(P/p) for p in ['scenes/candidate55-observation/Game55Observation.tscn','scenes/candidate56-coast/Game56Coast.tscn']},
}
out = {
 'mode':'Read-only static intake. No engine/world/GPU run and no native resource writes.', 'survey_box_xmin_xmax_zmin_zmax':BOX,
 'box_is_not_edit_authorization':True, 'authority':authority,
 'triangle_scope':{'total':len(tri),'wholly_inside_box':int(inside_faces.sum()),'boundary_crossing_or_aabb_overlap':int(boundary_cross.sum()),'outside_interior_pool':int((~inside_faces).sum()),'wholly_inside_triangle_ids':np.flatnonzero(inside_faces).tolist()},
 'topology':{'welded_points':len(unique),'boundary_edges':len(boundary),'nonmanifold_edges':sum(n>2 for n in edges.values()),'zero_area_faces':int((np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)<1e-8).sum()),'open_heightfield':len(boundary)>0},
 'shore_fit':{'sample_count':len(points),'bounds':[points.min(0).tolist(),points.max(0).tolist()],'x_equals_a_z_plus_b':coef.tolist(),'rms_x_residual':float(np.sqrt(np.mean(res*res))),'max_abs_x_residual':float(abs(res).max())},
 'shore_segments':contour,'seams':seams,
 'scatter':{'all_source_MM_nodes_scanned':mm_scanned,'all_source_instances_scanned':instance_scanned,'external_binary_resource_count':len(external_authority),'unsupported_MM_nodes':missing,'groups':scatter,'total_roots_inside_box':sum(len(g['instances']) for g in scatter)},
 'other_meshes_intersect_box':[m for m in other if m['distance_xz_to_box']==0], 'nearest_other_meshes':other[:20],
 'saved_road_routes':routes,
 'original_native_mesh_shape_max_world_component_difference':float(abs(tri-cols[TARGET]).max()),
 'cross_sections':[{'z':z,'samples':[{'x':x,'mesh':height(tri,x,z)} for x in range(-3440,-3119,20)]} for z in [-3740.,-3680.,-3620.,-3560.,-3500.,-3440.]],
 'limits':['No new local-position/GPU-attribute authority export or editable source reconstruction','Native export world floats suffice for survey; future native edits require direct local GPU arrays and zero-change source roundtrip','Other-mesh AABBs are conservative; scatter root support is not full footprint clearance','No resource edit, camera move, weather change, visual acceptance or flight test'],
}
(D/'intake.json').write_text(json.dumps(out,indent=2)+'\n')
(D/'external-multimesh-authority.json').write_text(json.dumps(external_authority,indent=2)+'\n')
print(json.dumps({'authority':authority,'triangle_scope':{k:v for k,v in out['triangle_scope'].items() if k!='wholly_inside_triangle_ids'},'topology':out['topology'],'shore_fit':out['shore_fit'],'scatter':{'groups':[{k:v for k,v in g.items() if k not in ['instances','group_world_transform']}|{'roots':len(g['instances'])} for g in scatter],'roots':out['scatter']['total_roots_inside_box'],'nodes_scanned':mm_scanned,'instances_scanned':instance_scanned,'unsupported':missing},'intersecting_meshes':out['other_meshes_intersect_box'],'nearest_other':other[:5],'seams':seams},indent=2))
