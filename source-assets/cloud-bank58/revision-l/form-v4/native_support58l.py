"""Pure source58L edit/capture checks. No engine import, launch or old L helper use."""
from __future__ import annotations
import hashlib, json, math, struct
from fractions import Fraction
from pathlib import Path

MASTER='L58_EDITABLE_MASTER'
EXPORT='L58_DERIVED_EXPORT'
MESH='L58_CANONICAL_MESH'
MATERIAL='L58_K_LINEAR_MATERIAL'
CONTROL_PREFIX='L58_CONTROL_'
CAMERA_PREFIX='L58_ABSOLUTE_'
BASE='l58_authored_base'
LAST='l58_last_evaluated'
INDEX='l58_vertex_index'
FACE='l58_face_index'
DIAGNOSTIC_MODE='api_consistency_isolated_diagnostic_v1'
FAILURE_ADMISSIONS=('3fc9d27fe46f83fc279b0902a852ac895c8c59a2d77e93f66a1fa651c5fee597','b8cc9985e206be4fc8f69b80c6e51ebebccaac4e8b1eb177ad6ced4784efe814','8216396cd70064b29057ed32fcd8c8f61eecaf1ccab4a949bc065c7ccb3d2e87')
HISTORICAL_DEFAULT_FAILURE=dict(raw_sha256='0b39aa841519b65874e24d219c4e74d3063daa8dfd9bdf86b15fdb90e9b5a99c',original_corner_geometry_passed=False,faces_over_3e_5=22,max_abs=0.00015941344933428914,max_angle_degrees=0.009158468662372497)
HISTORICAL_FORM_V2_DEFAULT_FAILURE=dict(raw_sha256='8ad8010e94bd7d9edcabe794ffb18c99a7519e50c34a37f20c1e3c8bdcfaafa7',original_corner_geometry_passed=False,faces_over_3e_5=23,max_abs=0.0005249128728819219,max_angle_degrees=0.03410575291451074)
HISTORICAL_FORM_V3_DEFAULT_FAILURE=dict(raw_sha256='3c9a563225a3e0205dec2caee37521169756489b2e7183dbf4654b298e01113b',original_corner_geometry_passed=False,faces_over_3e_5=24,max_abs=0.0005249128728819219,max_angle_degrees=0.03410575291451074)
NORMAL_LIMIT=3e-5
FLAGS=('world_loaded','world_integration_allowed','contact_acceptance','world_acceptance',
       'global_GOAL','visual_acceptance','weather_acceptance','auto_rebuild','full_native_acceptance')
IDENTITY=[[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
EDIT_TEXT='''# Explicit editing only. This Text is not an auto-run module.\nimport bpy\nns = {"__name__": "l58_embedded_support"}\nexec(compile(bpy.data.texts["NATIVE_SUPPORT58L.py"].as_string(), "NATIVE_SUPPORT58L.py", "exec"), ns)\nps = {"__name__": "l58_embedded_topology"}\nexec(compile(bpy.data.texts["POLY58K.py"].as_string(), "POLY58K.py", "exec"), ps)\ngs = {"__name__": "l58_embedded_geometry", "__file__": "/isolated/source-assets/cloud-bank58/revision-l/form-v4/geometry58l.py", "_EMBEDDED_TOPOLOGY": ps}\nexec(compile(bpy.data.texts["GEOMETRY58L.py"].as_string(), "GEOMETRY58L.py", "exec"), gs)\nns2 = {"__name__": "l58_explicit_edit", "_EMBEDDED_SUPPORT": ns, "_EMBEDDED_GEOMETRY": gs}\nexec(compile(bpy.data.texts["NATIVE58L.py"].as_string(), "NATIVE58L.py", "exec"), ns2)\nns2["rebuild_from_controls"]()\n'''
README_TEXT='''Form-v4 revises overall crown, shoulder and belly proportions after visually rejected form-v3. Exact candidate and bindings define the authored baseline and scope; original core80m, belly560-630 and thickness>=120 gates remain unchanged.\nThe immediate predecessor is the genuinely completed form-v3 source and four views. Its default original corner geometry gate failed on 24 faces, max 0.0005249128728819219, angle 0.03410575291451074 degrees.\nThe separate historical form-v2 default failed on 23 faces with the same maxima; its whole source stage remains failed. The older 22-face failure is also retained below.\nAPI-consistency isolated diagnostic source; full_native_acceptance=false.\nThe original corner-to-mathematical-geometry 3e-5 criterion failed in the historical default: 22 faces, max 0.00015941344933428914, angle 0.009158468662372497 degrees.\nThis criterion is remeasured per state, never relabelled by the new corner-to-float32-Newell API consistency test.\nPolygon-to-geometry, outward direction, flat shading, equal three corners and API consistency are separate checks.\nIsolated cloud58L editable source. Not contact, world, weather or GOAL acceptance.\nL58_EDITABLE_MASTER is the sole author mesh. L58_DERIVED_EXPORT shares its one mesh and is hidden and selection-locked.\nEdit master vertex heights without changing topology, or change the seven CONTROL custom value properties.\nThen explicitly Run EDIT58L.py. Invalid control/geometry edits are rejected, not clamped.\nDirect point offsets are reconciled into authored-base attributes. Repeated rebuilds do not accumulate controls.\nThe complete candidate, bindings, native edit source, support and geometry validator are embedded as non-auto-run Texts.\nNo handlers, drivers, save, render or export are invoked by EDIT58L.py. Saving edits is a separate user action.\nThe four source cameras retain the original absolute Godot camera transforms under the fixed author frame.\nTwo original front records are intentionally identical; neither is reframed to center this isolated source.\n1179x664 sampling uses a disclosed non-square pixel aspect derived from all four identical original projection ratios; no camera pose or frustum is refitted.\nK linear material is retained. Blender inspection lighting is a source diagnostic, not equivalent world/weather evidence.\n'''

def require(ok, message):
    if not ok: raise ValueError(message)

def f32(v): return struct.unpack('<f', struct.pack('<f',float(v)))[0]
def local(p): return [f32(p[0]-3958.),f32(3667.-p[2]),f32(p[1])]
def world(p): return [p[0]+3958.,p[2],3667.-p[1]]
def vector(p): return [p[0],-p[2],p[1]]
def digest(data): return hashlib.sha256(data).hexdigest()
def identity(raw): return {k:v for k,v in raw.items() if k not in ('pid','cpu_affinity','opened_filepath')}
def json_bytes(value): return (json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def schemas(candidate):
    return [(BASE,'FLOAT_VECTOR','POINT'),(LAST,'FLOAT_VECTOR','POINT'),(INDEX,'INT','POINT'),(FACE,'INT','FACE')]+[(f'l58_disp_{r["id"]}','FLOAT_VECTOR','POINT') for r in candidate['controls']]+[(f'l58_disp_{r["id"]}_{p["id"]}','FLOAT_VECTOR','POINT') for r in candidate['controls'] for p in r.get('secondary_parameters',[])]

def groups(candidate):
    n=len(candidate['vertices_world'])
    rows=[('CONTROL_'+r['id'],r['weights']) for r in candidate['controls']]
    for r in candidate.get('groups',[]):
        indices=set(r['indices']); rows.append((r['name'],[float(i in indices) for i in range(n)]))
    require(len({r[0] for r in rows})==len(rows),'Unique group names')
    return rows

def edit(candidate,current,base,last,values,secondary_values=None):
    """Float32 manual offsets + full per-unit fields, recomputed without drift."""
    n=len(candidate['vertices_world']); rows=candidate['controls']; secondary_values=secondary_values or {}
    require(len(current)==len(base)==len(last)==n and len(values)==len(rows)==7,'Edit cardinality')
    for r,v in zip(rows,values):
        require(type(v) in (int,float) and math.isfinite(v) and r['min']<=v<=r['max'],'Control range '+r['id'])
    for r in rows:
        for p in r.get('secondary_parameters',[]):
            v=secondary_values.get(r['id']+'.'+p['id'],p['default'])
            require(type(v) in (int,float) and math.isfinite(v) and p['min']<=v<=p['max'],'Secondary control range '+p['id'])
    authored=[[f32(base[i][j]+current[i][j]-last[i][j]) for j in range(3)] for i in range(n)]
    result=[]
    for i,p in enumerate(authored):
        q=p[:]
        for r,v in zip(rows,values):
            d=vector(r['displacements_world'][i]); delta=v-r['default']
            q=[a+delta*b for a,b in zip(q,d)]
        for r in rows:
            for p in r.get('secondary_parameters',[]):
                v=secondary_values.get(r['id']+'.'+p['id'],p['default']);d=vector(p['displacements_world'][i]);delta=v-p['default'];q=[a+delta*b for a,b in zip(q,d)]
        q=list(map(f32,q)); require(all(math.isfinite(x) for x in q),'Finite actual edited positions');result.append(q)
    return authored,result

def camera_matrix(record):
    b=bytes.fromhex(record['camera_transform'])
    require(len(b)==52 and b[:4]==struct.pack('<I',18),'Original Transform3D bytes')
    a=struct.unpack('<12f',b[4:]); r=[a[:3],a[3:6],a[6:9]]
    p=local(a[9:12])
    return [list(r[0])+[p[0]],[-x for x in r[2]]+[p[1]],list(r[1])+[p[2]],[0.,0.,0.,1.]]

def projection(record):
    b=bytes.fromhex(record['camera_projection'])
    require(len(b)==68 and b[:4]==struct.pack('<I',19),'Original Projection bytes')
    a=struct.unpack('<16f',b[4:])
    return [[a[j*4+i] for j in range(4)] for i in range(4)]

def calibrated_pixel_aspect(binding):
    """All four ORIGINAL frusta must independently demand the same exact ratio.

    P11/P00 = width*pixel_aspect_x/(height*pixel_aspect_y). Never infer a
    reference image size, average distinct frusta, or refit a camera matrix.
    Blender stores pixel aspects as float32; compare that actual representation.
    """
    cameras=binding['world_cameras'];require(len(cameras)==4,'Exactly four fixed calibration records')
    ratios=[]
    for record in cameras:
        p=projection(record)
        require(math.isfinite(p[0][0]) and math.isfinite(p[1][1]) and p[0][0]>0 and p[1][1]>0,'Finite positive original projection scales')
        ratios.append(Fraction(p[1][1])/Fraction(p[0][0]))
    require(all(r==ratios[0] for r in ratios),'Four frozen projections must share one exact sampling ratio; no averaging')
    ratio=ratios[0]*Fraction(664,1179)
    require(1<=ratio<=200,'Original common aspect within Blender pixel-aspect range')
    return [f32(float(ratio)),1.]

def capture_projection_args(settings):
    width,height=settings['resolution'];percentage=settings['percentage'];x,y=settings['pixel_aspect']
    require(type(width) is int and type(height) is int and type(percentage) is int and width>0 and height>0 and 0<percentage<=100,'Actual positive render sampling dimensions')
    require(all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in (x,y)),'Actual positive pixel aspect')
    return dict(x=width*percentage//100,y=height*percentage//100,scale_x=x,scale_y=y)

def render_projection_args(render):
    """Read actual RNA used by render, including actual stored float32 aspects."""
    return capture_projection_args(dict(resolution=[render.resolution_x,render.resolution_y],percentage=render.resolution_percentage,pixel_aspect=[render.pixel_aspect_x,render.pixel_aspect_y]))

def expected_texts(here,candidate,binding):
    here=Path(here)
    return {'CANDIDATE58L.json':json_bytes(candidate),'BINDINGS58L.json':json_bytes(binding),
      'NATIVE58L.py':(here/'native58l.py').read_bytes(),'NATIVE_SUPPORT58L.py':(here/'native_support58l.py').read_bytes(),
      'GEOMETRY58L.py':(here/'geometry58l.py').read_bytes(),'POLY58K.py':(here.parents[3]/'source-assets/cloud-bank58/revision-k/poly58k.py').read_bytes(),'EDIT58L.py':EDIT_TEXT.encode(),'README58L.txt':README_TEXT.encode()}

def nested_max(a,b):
    require(len(a)==len(b),'Matrix dimensions');return max(abs(x-y) for ra,rb in zip(a,b) for x,y in zip(ra,rb))

def validate_capture(raw,candidate,binding,expected=None,*,manual_base=None):
    """Check actual native readback. This never claims topology/contact acceptance."""
    n=len(candidate['vertices_world']); faces=candidate['faces']; controls=candidate['controls']; baseline=[local(p) for p in candidate['vertices_world']]
    require(raw['version']==candidate['version'] and raw['scene_flags']['source_version']==candidate['version'] and raw['scene_flags']['source_diagnostic_only'] is True,'Actual isolated source identity')
    require(raw['blender_version']==[4,5,14],'Pinned Blender runtime')
    require(raw['scene_flags']['acceptance_mode']==DIAGNOSTIC_MODE and raw['scene_flags']['historical_default_corner_geometry_passed'] is False,'Explicit API diagnostic scene scope and preserved historical failure')
    require(all(raw['scene_flags'][k] is False for k in FLAGS),'Source-only acceptance flags remain false')
    require(raw['scene_flags']['anchor_world_json']=='[3958, 0, 3667]' and raw['scene_flags']['scale_one'] is True,'Original fixed frame')
    require(raw['canonical_mesh_shared'] and raw['mesh_names']==[MESH] and raw['material_names']==[MATERIAL],'One canonical editable mesh')
    mesh=raw['mesh']; require(mesh['name']==MESH and mesh['faces']==faces,'Actual topology order')
    require(mesh['polygon_loop_counts']==[3]*len(faces) and mesh['polygon_loop_starts']==list(range(0,3*len(faces),3)) and mesh['loop_vertex_indices']==[i for f in faces for i in f],'Actual triangle loops')
    require(mesh['flat']==[True]*len(faces) and mesh['material_indices']==[0]*len(faces) and mesh['material_slots']==[MATERIAL],'Actual flat K material assignment')
    attrs=mesh['attributes']; expected_schemas=schemas(candidate)
    require(set(attrs)=={s[0] for s in expected_schemas},'Complete authored attributes')
    for name,kind,domain in expected_schemas:
        require(attrs[name]['data_type']==kind and attrs[name]['domain']==domain,'Attribute RNA schema '+name)
    require(attrs[INDEX]['values']==list(range(n)) and attrs[FACE]['values']==list(range(len(faces))),'Stable canonical indices')
    base=baseline if manual_base is None else manual_base
    require(attrs[BASE]['values']==base,'Actual authored-base identity')
    vals=[r['value'] for r in raw['controls']]
    secondary={r['id']+'.'+p['id']:p['value'] for r in raw['controls'] for p in r['secondary_parameters']}
    _,points=edit(candidate,base,base,base,vals,secondary)
    require(mesh['vertices']==points and attrs[LAST]['values']==points,'Actual evaluated positions/last attributes')
    require(raw['scene_flags']['edited_after_frozen_build']==(points!=baseline or base!=baseline),'Actual edit-state flag')
    gs=groups(candidate);require(mesh['group_names']==[g[0] for g in gs],'Actual vertex group identities')
    expected_weights=[[f32(w[i]) for _,w in gs] for i in range(n)]
    require(mesh['weights']==expected_weights,'Actual RNA group weights')
    require(mesh['memberships']==[[[j,w] for j,w in enumerate(row) if w] for row in expected_weights],'Actual sparse memberships')
    for r in controls:
        require(attrs['l58_disp_'+r['id']]['values']==[list(map(f32,vector(v))) for v in r['displacements_world']],'Actual semantic displacement attribute')
        for p in r.get('secondary_parameters',[]):
            require(attrs['l58_disp_'+r['id']+'_'+p['id']]['values']==[list(map(f32,vector(v))) for v in p['displacements_world']],'Actual secondary displacement attribute')
    require(len(raw['controls'])==7,'Seven actual controls')
    for row,spec in zip(raw['controls'],controls):
        require(row['name']==CONTROL_PREFIX+spec['id'] and row['location']==local(spec['position_world']),'Semantic control identity/position')
        require(all(row[k]==spec[k] for k in ('id','default','min','max','semantic','units')),'Control metadata')
        require(len(row['secondary_parameters'])==len(spec.get('secondary_parameters',[])),'Secondary control count')
        for got,want in zip(row['secondary_parameters'],spec.get('secondary_parameters',[])):
            require(all(got[k]==want[k] for k in ('id','default','min','max','semantic')) and got['last_applied_value']==got['value'],'Actual secondary control metadata/sync')
        require(row['last_applied_value']==row['value'] and row['lock_location']==row['lock_rotation']==row['lock_scale']==[True]*3,'Actual control locks/sync')
    mats=binding['material'];mat=raw['material']
    require(mat['name']==MATERIAL and mat['use_nodes'] and mat['base_color_linear_rgba']==list(map(f32,mats['linear_rgba'])) and mat['roughness']==f32(mats['roughness']) and mat['metallic']==f32(mats['metallic']) and mat['backface_culling']==mats['backface_culling'],'K linear material actual sockets')
    require(mat['node_types']==['ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial'] and mat['links']==[['ShaderNodeBsdfPrincipled','BSDF','ShaderNodeOutputMaterial','Surface']],'No diagnostic shader replacement')
    require(mat['emission_color']==[0.,0.,0.,1.] and mat['emission_strength']==0.,'No emissive material alteration')
    cam_errors=[]; expected_cameras=binding['world_cameras']
    require([r['name'] for r in raw['cameras']]==[r['name'] for r in expected_cameras],'Original four cameras')
    for got,want in zip(raw['cameras'],expected_cameras):
        require(got['declared_transform_hex']==want['camera_transform'] and got['declared_projection_hex']==want['camera_projection'],'Exact embedded original camera bytes')
        require(got['projection_sampling']==capture_projection_args(raw['settings']),'Projection evaluated with actual captured render sampling')
        t=nested_max(got['matrix_world'],camera_matrix(want));p=nested_max(got['projection_matrix'],projection(want))
        # Matrix decomposition/projection are actual float32 RNA operations; the
        # original bytes remain exact. These bounds are diagnostics, not refits.
        require(t<=2e-6 and p<=2e-5,'Actual fixed camera numerical transform/projection')
        require(got['type']=='PERSP' and got['sensor_fit']=='VERTICAL' and got['sensor_height']==32. and got['clip_start']==f32(want['near']) and got['clip_end']==f32(want['far']),'Original absolute camera settings')
        cam_errors.append({'name':want['name'],'transform_max_abs':t,'projection_max_abs':p})
    expected_names=sorted([MASTER,EXPORT,'L58_K_FIXED_SUN']+[CONTROL_PREFIX+r['id'] for r in controls]+[CAMERA_PREFIX+r['name'] for r in expected_cameras])
    require([o['name'] for o in raw['objects']]==expected_names,'No hidden/foreign geometry')
    for ob in raw['objects']:
        require(ob['parent'] is None and not ob['modifiers'] and not ob['constraints'] and ob['driver_count']==0,'No transforms/modifiers/constraints/drivers')
        if ob['type']=='MESH':
            require(ob['name'] in (MASTER,EXPORT) and ob['matrix_world']==IDENTITY and ob['mesh_name']==MESH and ob['vertex_group_names']==[g[0] for g in gs],'Mesh identity and canonical sharing')
            require(ob['hide_render']==(ob['name']==EXPORT) and ob['hide_viewport']==(ob['name']==EXPORT) and ob['hide_select']==(ob['name']==EXPORT),'Sole visible editable master')
    s=raw['settings']; require(s==dict(render_filepath='',engine='CYCLES',device='CPU',samples=8,denoising=False,threads_mode='FIXED',threads=2,resolution=[1179,664],percentage=100,pixel_aspect=calibrated_pixel_aspect(binding),view_transform='AgX',look='None',exposure=0.,gamma=1.,use_nodes=False,use_compositing=False,use_sequencer=False,transparent=False,active_camera=CAMERA_PREFIX+expected_cameras[0]['name']),'Bound source diagnostic render setup')
    lit=binding['source_inspection_lighting']; actual=raw['lighting']
    require(actual==dict(world_color=list(map(f32,lit['world_linear_rgba'])),world_strength=f32(lit['world_strength']),sun_type='SUN',sun_energy=f32(lit['sun_energy']),sun_angle=f32(lit['sun_angle_radians']),sun_rotation=list(map(f32,lit['sun_source_rotation_xyz_radians']))),'Fixed source inspection lighting')
    require(not raw['external_libraries'] and not raw['images'] and not raw['autoexec_enabled'],'No external native dependencies/autoexecution')
    if expected is not None:
        want=[dict(name=k,sha256=digest(v),bytes=len(v),is_in_memory=True,filepath='',use_module=False) for k,v in sorted(expected.items())]
        require(raw['texts']==want,'Complete exact internal reconstruction Texts')
    else:require(len(raw['texts'])==8 and all(t['is_in_memory'] and not t['filepath'] and not t['use_module'] for t in raw['texts']),'Internal non-auto-run Texts')
    normals=validate_normals(mesh)
    return dict(api_diagnostic_rna_passed=True,acceptance_mode=DIAGNOSTIC_MODE,full_native_acceptance=False,normals=normals,cameras=cam_errors,contact_acceptance=False,world_acceptance=False,global_GOAL=False)


def float32_newell(triangle):
    """Sequential float32 Newell accumulate/normalize; stdlib only, no RNA writes.

    Blender 4.5.14 cached face/flat-corner path. Normalization roundoff may
    differ by an ULP; the separately disclosed API comparison bound is 3e-5.
    """
    require(len(triangle)==3 and all(len(v)==3 and all(type(x) in (int,float) and math.isfinite(x) for x in v) for v in triangle),'Finite actual triangle coordinates')
    q=[0.,0.,0.];previous=triangle[-1]
    for current in triangle:
        for axis in range(3):
            j=(axis+1)%3;k=(axis+2)%3
            q[axis]=f32(q[axis]+f32(f32(previous[j]-current[j])*f32(previous[k]+current[k])))
        previous=current
    squares=[f32(x*x) for x in q]
    length=f32(math.sqrt(f32(f32(squares[0]+squares[1])+squares[2])))
    require(math.isfinite(length) and length>0,'Nonzero finite float32 Newell normal')
    return [f32(x/length) for x in q]


def validate_normals(mesh):
    """Actual raw normals only. Do not manufacture normals, clamp or change mesh.

    This is an explicitly new diagnostic oracle, NOT an old full-native pass.
    Original corner-to-geometry results are measured and retained for EVERY
    state, even when true in a particular edit/control test.
    """
    faces=mesh['faces'];points=mesh['vertices'];polygons=mesh['polygon_normals'];corners=mesh['corner_normals']
    require(len(polygons)==len(faces) and len(corners)==3*len(faces),'Actual normal counts')
    require(mesh['flat']==[True]*len(faces),'Actual polygons must remain flat')
    require(all(len(v)==3 and all(type(x) in (int,float) and math.isfinite(x) for x in v) for v in points+polygons+corners),'Finite actual positions and normals')
    polygon_max=corner_max=api_max=angle_max=unit_max=0.;dot_min=1.;failed=[]
    for i,face in enumerate(faces):
        require(len(face)==3,'Actual triangular normal face')
        triangle=[points[k] for k in face];a,b,c=triangle
        u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
        q=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        length=math.sqrt(sum(x*x for x in q));require(math.isfinite(length) and length>0,'Nondegenerate actual triangle')
        geometric=[x/length for x in q];newell=float32_newell(triangle)
        pc=corners[3*i:3*i+3]
        require(pc[0]==pc[1]==pc[2],'Actual three flat corners must be equal')
        pg=max(abs(x-y) for x,y in zip(polygons[i],geometric));cg=max(abs(x-y) for n in pc for x,y in zip(n,geometric));ng=max(abs(x-y) for n in pc for x,y in zip(n,newell))
        polygon_max=max(polygon_max,pg);corner_max=max(corner_max,cg);api_max=max(api_max,ng)
        if cg>NORMAL_LIMIT:failed.append(i)
        for actual in [polygons[i]]+pc:
            size=math.sqrt(sum(x*x for x in actual));require(math.isfinite(size) and size>0,'Nonzero actual normals')
            unit_max=max(unit_max,abs(size-1.));dot=sum(x*y for x,y in zip(actual,geometric))/size
            require(dot>0,'Actual normals must point outward with original oriented geometry')
            dot_min=min(dot_min,dot)
        normal=[x/math.sqrt(sum(z*z for z in pc[0])) for x in pc[0]]
        cross=[normal[1]*geometric[2]-normal[2]*geometric[1],normal[2]*geometric[0]-normal[0]*geometric[2],normal[0]*geometric[1]-normal[1]*geometric[0]]
        angle_max=max(angle_max,math.degrees(math.atan2(math.sqrt(sum(x*x for x in cross)),sum(x*y for x,y in zip(normal,geometric)))))
    require(polygon_max<=NORMAL_LIMIT,'Actual polygon-to-mathematical-geometry 3e-5 criterion')
    require(unit_max<=NORMAL_LIMIT,'Actual polygon/corner unit normals')
    require(api_max<=NORMAL_LIMIT,'Actual flat corner-to-float32-Newell API consistency 3e-5 criterion')
    return dict(acceptance_mode=DIAGNOSTIC_MODE,diagnostic_normal_acceptance=True,full_native_acceptance=False,
      polygon_geometry_passed=True,polygon_geometry_max_abs=polygon_max,flat=True,three_corners_equal=True,outward=True,unit_length_error_max=unit_max,geometric_direction_dot_min=dot_min,
      corner_newell_api_passed=True,corner_newell_api_max_abs=api_max,comparison_limit=NORMAL_LIMIT,
      original_corner_geometry_passed=not failed,original_corner_geometry_max_abs=corner_max,original_corner_geometry_faces_over_limit=failed,original_corner_geometry_max_angle_degrees=angle_max,
      historical_default_failure=dict(HISTORICAL_DEFAULT_FAILURE))


def state_values(raw):
    values={r["id"]:r["value"] for r in raw["controls"]}
    values.update({r["id"]+"."+p["id"]:p["value"] for r in raw["controls"] for p in r["secondary_parameters"]})
    return values
