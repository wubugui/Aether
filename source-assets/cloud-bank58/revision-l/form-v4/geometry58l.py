"""Isolated L author-source geometry gates. No engine import or launch.

The actual source is a two-sheet PL disk with shared rim vertices. Its
self-intersection proof is specific: a nonoverlapping planar triangulation,
strict positive interior thickness, and identical XZ across the two sheets.
No neighbor contact/world acceptance is inferred from that fact.
"""
from __future__ import annotations
import hashlib, json, math, struct, importlib.util
from pathlib import Path
from collections import defaultdict, Counter
from fractions import Fraction
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
VERSION='cloudbank58l-form-v4'
SOURCE=HERE/'cloud_bank58l_form_v4.blend'
CANDIDATE_PATH=HERE/'candidate.json'
BINDING_PATH=HERE/'bindings.json'
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
BLENDER_SHA='050c02562f81fe80ba616a80198fa02d381e60f8b61b8d39add881f4bca0d7d8'
ANCHOR=[3958.,0.,3667.]
CONTROL_IDS=['C01_Crown_A','C02_Crown_B','C03_Return_C','C04_Shoulder_D','C05_Main_Valley','C06_Belly','C07_Meso_Relief']
def require(ok,message):
    if not ok: raise ValueError(message)
def read(p): return json.loads(Path(p).read_text())
def write(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def f32(v):return np.asarray(v,dtype='<f4').astype(float)
def local(v):
    a=np.asarray(v,float);return np.stack((a[...,0]-3958.,3667.-a[...,2],a[...,1]),axis=-1)
def world(v):
    a=np.asarray(v,float);return np.stack((a[...,0]+3958.,a[...,2],3667.-a[...,1]),axis=-1)
def native_world(v):return world(f32(local(v)))
def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
def orient(a,b,c):
    v=float(cross(b-a,c-a));err=16*np.finfo(float).eps*(abs((b[0]-a[0])*(c[1]-a[1]))+abs((b[1]-a[1])*(c[0]-a[0])))
    if abs(v)>err:return 1 if v>0 else -1
    a,b,c=[[Fraction(float(x)) for x in p] for p in (a,b,c)]
    q=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);return (q>0)-(q<0)
def rim_distance(points,rim):
    p=np.asarray(points,float);r=np.asarray(rim,float);a=r;b=np.roll(r,-1,axis=0);d=b-a
    out=[]
    for q in p:
        t=np.clip(np.sum((q-a)*d,axis=1)/np.sum(d*d,axis=1),0,1);out.append(float(np.linalg.norm(q-a-t[:,None]*d,axis=1).min()))
    return np.array(out)
def planar_certificate(xz,tri,rim_count):
    """All edge pairs broad phase + adaptive exact crossing/overlap predicates."""
    xz=np.asarray(xz,float);tri=np.asarray(tri,int);edges=defaultdict(list)
    require(all(orient(*xz[t])==1 for t in tri),'PLANAR_INVERTED_OR_ZERO_TRIANGLE')
    for k,t in enumerate(tri):
        for a,b in zip(t,np.roll(t,-1)):edges[tuple(sorted((int(a),int(b))))].append(k)
    expected={tuple(sorted((i,(i+1)%rim_count))) for i in range(rim_count)}
    require({e for e,v in edges.items() if len(v)==1}==expected,'PLANAR_BOUNDARY_IDENTITY')
    require(all(len(v) in (1,2) for v in edges.values()),'PLANAR_EDGE_INCIDENCE')
    el=np.array(list(edges),int);p=xz[el];lo=p.min(1);hi=p.max(1);tested=0
    for i,(a,b) in enumerate(el):
        js=np.flatnonzero(np.all(hi[i]>=lo,1)&np.all(hi>=lo[i],1));A,B=xz[a],xz[b]
        for j in js:
            if j<=i:continue
            c,d=el[j];C,D=xz[c],xz[d];shared=set((a,b))&set((c,d));tested+=1
            o1,o2=orient(A,B,C),orient(A,B,D);o3,o4=orient(C,D,A),orient(C,D,B)
            if shared:
                if o1==o2==0:
                    axis=int(np.argmax(abs(B-A)));overlap=min(max(A[axis],B[axis]),max(C[axis],D[axis]))-max(min(A[axis],B[axis]),min(C[axis],D[axis]));require(overlap==0,'PLANAR_COLLINEAR_EDGE_OVERLAP')
            else: require(not(o1*o2<=0 and o3*o4<=0),'PLANAR_EDGE_INTERSECTION')
    require(len(xz)-len(edges)+len(tri)==1,'PLANAR_DISK_EULER')
    adjacency=defaultdict(set)
    for vs in edges.values():
        if len(vs)==2:a,b=vs;adjacency[a].add(b);adjacency[b].add(a)
    seen={0};todo=[0]
    while todo:
        for j in adjacency[todo.pop()]:
            if j not in seen:seen.add(j);todo.append(j)
    require(len(seen)==len(tri),'PLANAR_DISCONNECTED')
    # Noncrossing embedded connected oriented disk with one boundary rules out
    # containment/overlap without ever replacing a concave boundary by a hull.
    return dict(passed=True,all_planar_edges_tested=len(edges),aabb_edge_pairs_tested=tested,adaptive_exact_predicates=True,nonoverlap_proof='connected consistently oriented disk; one prescribed simple boundary; no intersecting or overlapping embedded edges')
def solid_arrays(c,vertices=None):
    v=np.asarray(c['vertices_world'] if vertices is None else vertices,float);n=c['planar_vertex_count'];r=c['rim_count'];T=v[:n];B=np.vstack((v[:r],v[n:]));return v,T,B

def spatial_gate(c,vertices=None,check_planar=True):
    v,T,B=solid_arrays(c,vertices);tri=np.asarray(c['planar_triangles'],int);r=c['rim_count'];n=c['planar_vertex_count'];f=np.asarray(c['faces'],int)
    require(len(v)==2*n-r and f.shape==(2*len(tri),3),'TWO_SHEET_LAYOUT')
    require(np.array_equal(T[:,[0,2]],B[:,[0,2]]),'TWO_SHEET_XZ_IDENTITY')
    require(np.all(T[r:,1]>B[r:,1]) and np.array_equal(T[:r],B[:r]),'POSITIVE_INTERIOR_THICKNESS')
    # Verify actual face indexing, not just the recipe description.
    bottom_ids=np.r_[np.arange(r),np.arange(n,2*n-r)]
    expected=np.vstack((tri[:,[0,2,1]],bottom_ids[tri]));require(np.array_equal(f,expected),'SHELL_FACES_NOT_SHARED_DISK')
    xz=T[:,[0,2]];pc=planar_certificate(xz,tri,r) if check_planar else None
    rim=np.asarray(c['external_rim_authority_float64_xz'],float);require(rim.shape==(r,2),'SOURCE_RIM_SHAPE');distance=rim_distance(xz,rim);thick=T[:,1]-B[:,1]
    exempt=[];core=[]
    for i,t in enumerate(tri):
        # Max distance anywhere in a triangle to one selected rim segment is
        # bounded by the maximum of its vertices' distances to that segment.
        # Minimum over all segments stays a conservative global upper bound.
        q=xz[t];a=rim;b=np.roll(rim,-1,axis=0);d=b-a
        u=np.clip(np.sum((q[:,None,:]-a)*d,axis=2)/np.sum(d*d,axis=1),0,1)
        upper=float(np.linalg.norm(q[:,None,:]-a-u[:,:,None]*d,axis=2).max(0).min())
        valid=bool(B[t,1].min()>=560 and B[t,1].max()<=630 and thick[t].min()>=120)
        if valid:core.append(i)
        else:
            # Clip the actual affine inequality regions, rather than incorrectly
            # requiring a whole straddling triangle to be an edge exception.
            bounds=[]
            for name,scalar in [('low_belly',560-B[t,1]),('high_belly',B[t,1]-630),('thin',120-thick[t])]:
                if scalar.max()<=0:continue
                polygon=[]
                for k in range(3):
                    j=(k+1)%3;P,Q=q[k],q[j];v0,v1=float(scalar[k]),float(scalar[j])
                    if v0>=0:polygon.append(P)
                    if (v0<0<v1) or (v1<0<v0):
                        fraction=Fraction(v0)/(Fraction(v0)-Fraction(v1))
                        polygon.append(P+float(fraction)*(Q-P))
                poly=np.asarray(polygon);u2=np.clip(np.sum((poly[:,None,:]-a)*d,axis=2)/np.sum(d*d,axis=1),0,1)
                bound=float(np.linalg.norm(poly[:,None,:]-a-u2[:,:,None]*d,axis=2).max(0).min())
                require(bound<80,'CORE_VOLUME_VIOLATION triangle='+str(i)+' kind='+name+' bound='+str(bound)+' bottom='+str(B[t,1].tolist())+' thick='+str(thick[t].tolist()))
                bounds.append(bound)
            exempt.append(dict(triangle=i,external_distance_upper_m=max(bounds)))
    require(v[:,1].min()>=533.4189910888672 and v[:,1].max()<=1057.0673217773438,'ABSOLUTE_Y_ENVELOPE')
    if '_EMBEDDED_TOPOLOGY' in globals():
        topology=_EMBEDDED_TOPOLOGY['topology']
    else:
        spec=importlib.util.spec_from_file_location('l58_topology',ROOT/'source-assets/cloud-bank58/revision-k/poly58k.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);topology=m.topology
    topo=topology(f32(local(v)),f,dict(maximum_vertices=2584,maximum_triangles=5164,minimum_area_m2=1e-8,minimum_edge_m=1e-5))
    return dict(passed=True,topology=topo,planar_embedding=pc,non_self_intersection=True,intersection_method='actual paired PL heightfield; exact XZ identity, positive interior thickness, prescribed nonoverlapping disk; upper/bottom meet only at shared simple rim',guarded_triangles=len(core),outer_return_triangles=len(exempt),outer_return_max_bound_m=max((x['external_distance_upper_m'] for x in exempt),default=0),core_rule='Clip each actual affine violation region against560/630/120. Every nonempty violation polygon lies wholly strictly within80m of true rim by convex point-to-segment distance upper bound; no interior seam/hole exemption',contact_acceptance=False,world_acceptance=False,global_GOAL=False)

def evaluate(c,values=None):
    values=values or {r['id']:r['default'] for r in c['controls']}
    if not isinstance(values,dict):values=dict(zip(CONTROL_IDS,values))
    v=np.asarray(c['vertices_world'],float).copy()
    for r in c['controls']:
        a=float(values.get(r['id'],r['default']));require(math.isfinite(a) and r['min']<=a<=r['max'],'CONTROL_RANGE:'+r['id'])
        v+=np.asarray(r['displacements_world'])*(a-r['default'])
        for extra in r.get('secondary_parameters',[]):
            key=r['id']+'.'+extra['id'];a=float(values.get(key,extra['default']));require(math.isfinite(a) and extra['min']<=a<=extra['max'],'CONTROL_RANGE:'+key)
            v+=np.asarray(extra['displacements_world'])*(a-extra['default'])
    v=native_world(v);spatial_gate(c,v,check_planar=False);return v

def validate_candidate(c=None):
    c=read(CANDIDATE_PATH) if c is None else c
    require(c['version']==VERSION and c['stage']=='isolated_author_candidate','ISOLATED_SOURCE_IDENTITY')
    require(c['anchor_world']==[3958,0,3667] and c['scale']==[1,1,1],'FRAME_IDENTITY')
    require(not any(c[k] for k in ('contact_acceptance','world_acceptance','global_GOAL')),'FALSE_WORLD_CLAIM')
    require([r['id'] for r in c['controls']]==CONTROL_IDS,'SEVEN_CONTROLS')
    v=np.asarray(c['vertices_world']);require(np.array_equal(v,native_world(v)),'CANDIDATE_NOT_ACTUAL_FLOAT32')
    binding=read(BINDING_PATH);_,T,B=solid_arrays(c)
    require(np.array_equal(c['external_rim_authority_float64_xz'],binding['external_rim_authority_float64_xz']),'BOUND_SOURCE_RIM_IDENTITY')
    require(np.array_equal(T[:c['rim_count'],:][:,[0,2]],binding['actual_rim_world_xz']),'FROZEN_RIM_XZ')
    for r in binding['baseline_authority']:
        i=r['vertex_index'];require(np.array_equal(T[i],native_world(r['top_world'])) and np.array_equal(B[i],native_world(r['bottom_world'])),'FORM_V4_BOUND_LOCAL_KNOT_IDENTITY')
    for name,r in binding['baseline_nodes'].items():require(np.array_equal(T[r['vertex_index']],native_world(r['world_xyz'])),'BASELINE_NODE_IDENTITY:'+name)
    validate_form_scope(c,binding)
    proof=spatial_gate(c)
    for r in c['controls']:
        w=np.asarray(r['weights']);d=np.asarray(r['displacements_world']);require(w.shape==(len(v),) and d.shape==v.shape,'CONTROL_FIELD_SHAPE');require(np.array_equal(w,f32(w)) and np.all((w>=0)&(w<=1)),'CONTROL_WEIGHTS_F32');require(np.all(d[w==0]==0) and np.any(d!=0),'CONTROL_GENUINE_SUPPORT');require(np.all(d[:c['rim_count']]==0),'CONTROL_RIM_FIXED')
    return proof

def validate_evaluated(candidate,vertices_world,values=None):
    if values is not None:
        if not isinstance(values,dict):values=dict(zip(CONTROL_IDS,values))
        for r in candidate['controls']:
            val=values.get(r['id'],r['default']);require(r['min']<=val<=r['max'],'CONTROL_RANGE:'+r['id'])
            for extra in r.get('secondary_parameters',[]):
                key=r['id']+'.'+extra['id'];val=values.get(key,extra['default']);require(extra['min']<=val<=extra['max'],'CONTROL_RANGE:'+key)
    v=np.asarray(vertices_world,float)
    require(np.array_equal(v,native_world(v)),'EDIT_NOT_FLOAT32')
    require(np.array_equal(v[:,[0,2]],np.asarray(candidate['vertices_world'])[:,[0,2]]),'XZ_LAYOUT_LOCKED_HEIGHT_EDIT_ONLY')
    return spatial_gate(candidate,v,check_planar=False)

def validate_native_raw(raw,candidate,binding):
    import native_support58l as support
    report=support.validate_capture(raw,candidate,binding,support.expected_texts(HERE,candidate,binding))
    v=world(np.asarray(raw['mesh']['vertices']));report['geometry']=spatial_gate(candidate,v)
    return report


def validate_form_scope(c,binding):
    """One explicit full A/B crown-waist and real near-front authored edit."""
    scope=binding['form_v4'];prior=np.asarray(scope['prior_vertices_world'],float);v=np.asarray(c['vertices_world'],float);n=c['planar_vertex_count'];r=c['rim_count']
    require(v.shape==prior.shape,'FORM_V4_POINT_COUNT_FIXED')
    require(hashlib.sha256(json.dumps(c['faces'],separators=(',',':')).encode()).hexdigest()==scope['prior_faces_sha256'],'FORM_V4_TOPOLOGY_FIXED')
    require(np.array_equal(v[:r],prior[:r]),'FORM_V4_TRUE_RIM_XYZ_FIXED')
    xz=prior[:n][:,[0,2]];inside=np.zeros(n,dtype=bool);near=np.zeros(n,dtype=bool)
    for region in scope['regions_world_xz']:
        if region['shape']=='ellipse':
            included=np.linalg.norm((xz-np.asarray(region['center']))/np.asarray(region['radii']),axis=1)<=region['support_scale']
        else:
            x0,x1,z0,z1=region['bounds'];included=(xz[:,0]>=x0)&(xz[:,0]<=x1)&(xz[:,1]>=z0)&(xz[:,1]<=z1);near|=included
        inside|=included
    require(np.array_equal(v[~np.r_[inside,inside[r:]]],prior[~np.r_[inside,inside[r:]]]),'FORM_V4_OUTSIDE_XYZ_FIXED')
    require(np.array_equal(v[~np.r_[near,near[r:]]][:,[0,2]],prior[~np.r_[near,near[r:]]][:,[0,2]]),'FORM_V4_XZ_NEAR_ONLY')
    require(float(np.linalg.norm(v[:,[0,2]]-prior[:,[0,2]],axis=1).max())<=35,'FORM_V4_PLAN_SHIFT_MAX_35M')
    _,T,B=solid_arrays(c);_,oldT,oldB=solid_arrays(c,prior);rim=np.asarray(c['external_rim_authority_float64_xz']);old_d=rim_distance(oldT[:,[0,2]],rim);new_d=rim_distance(T[:,[0,2]],rim)
    edge=(old_d<80)&(new_d<80)&near
    require(np.array_equal(B[~edge,1],oldB[~edge,1]),'FORM_V4_CORE_AND_OUTSIDE_BELLY_Y_FIXED')
    require(float(abs(B[:,1]-oldB[:,1]).max())<=35,'FORM_V4_EDGE_BELLY_Y_MAX_35M')
    require(float(abs(T[:,1]-oldT[:,1]).max())<=120,'FORM_V4_TOP_Y_MAX_120M')
    require(c['controls'][2:]==scope['prior_controls'][2:],'FORM_V4_OTHER_FIVE_CONTROLS_FIXED')
    require(c['section_paths']==scope['prior_section_paths'],'FORM_V4_SECTION_PATHS_FIXED')
    fixed=np.asarray(scope['preserved_valley_vertices'],int)
    require(np.array_equal(T[fixed],oldT[fixed]) and np.array_equal(B[fixed],oldB[fixed]),'FORM_V4_VALLEY_FLOOR_FIXED')
    for name,oldrow in scope['prior_named_nodes'].items():
        i=oldrow['vertex_index'];row=c['named_nodes'][name]
        require(row['vertex_index']==i and np.array_equal(B[i],oldB[i]),'FORM_V4_NAMED_BOTTOM_FIXED:'+name)
        if name in ('A','B'):
            expected=945 if name=='A' else 975
            require(np.array_equal(T[i],np.array([oldT[i,0],expected,oldT[i,2]])) and row['world_xyz']==T[i].tolist(),'FORM_V4_AB_TRUE_ABSOLUTE_HEIGHT:'+name)
        else:
            require(row==oldrow and np.array_equal(T[i],oldT[i]),'FORM_V4_OTHER_NAMED_NODES_FIXED:'+name)
    for index,name in enumerate(('A','B')):
        row=c['controls'][index];old=scope['prior_controls'][index];delta=scope['AB_control_parameter_shifts'][name];i=c['named_nodes'][name]['vertex_index']
        for key in ('default','min','max','exercise_value'):
            require(row[key]==old[key]+delta,'FORM_V4_AB_PARAMETER_SEMANTICS:'+row['id']+':'+key)
        require(row['position_world']==c['named_nodes'][name]['world_xyz'] and row['default']==T[i,1],'FORM_V4_AB_HANDLE_DEFAULT_MATCH')
        require(row['weights'][i]==1 and row['displacements_world'][i]==[0,1,0],'FORM_V4_AB_UNIT_CREST_BINDING')
        require(np.all(np.asarray(row['displacements_world'])[:,[0,2]]==0),'FORM_V4_AB_HEIGHT_EDIT_ONLY')
        require(np.all(np.asarray(row['displacements_world'])[n:]==0),'FORM_V4_AB_BELLY_UNCHANGED')
    require(c['form_v4']['old_AB_crown_height_width_support_identity'] is False and c['form_v4']['old_two_rectangle_patch_identity'] is False and c['form_v4']['core80m_rule_unchanged'] is True,'FORM_V4_EXPLICIT_SCOPE')
    return True
