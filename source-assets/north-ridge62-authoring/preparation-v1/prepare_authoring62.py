"""Bounded source-only ridge design. No engine, subprocess or project writes.
All generated files stay beside this file. `--write` saves the reproducible plan.
The proposal is not a terrain/support/native acceptance result.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, struct
import numpy as np
import scipy
from scipy.spatial import Delaunay, cKDTree
D=Path(__file__).resolve().parent
R=D.parents[2]
E=R/'cloud-evidence/north-ridge62-shadow-script-v4-20261002T094319Z-o5sjgbgh'
INTAKE=R/'cloud-evidence/north-ridge62-collect-20261002T053100Z-3mmbw0ol/native-intake.json'
TERRAIN=R/'cloud-evidence/coast-boundary-readonly-20261001/native-coast.json'
TARGETS=['Ground_-4_-7','Ground_-3_-7','Ground_-4_-6','Ground_-3_-6','Ground_-4_-5','Ground_-3_-5']
# Convex local permission proposal. This is substantially smaller than the intake rectangle.
POLYGON=[[-2970,-4940],[-2930,-5135],[-2670,-5150],[-2370,-5135],[-2150,-4990],[-2090,-4730],[-2100,-4420],[-2180,-4220],[-2380,-4080],[-2630,-4120],[-2820,-4350],[-2940,-4620]]
# Names, X, Z, absolute target world Y. These are design choices, not recovered reference coordinates.
CONTROLS=[('rear_crown',-2800,-4940,550),('northwest_saddle',-2670,-4900,480),('main_peak',-2470,-4840,745),('main_north_shoulder',-2500,-5020,355),('northeast_arete',-2300,-4865,410),('west_rock_shoulder',-2860,-4740,350),('west_spur',-2740,-4560,340),('cloud_north_saddle',-2510,-4720,510),('cloud_east_saddle',-2290,-4720,405),('cloud_west_saddle',-2695,-4720,485),('south_middle_shoulder',-2460,-4510,445),('southeast_shoulder',-2230,-4500,325),('south_spur',-2480,-4300,295),('southwest_flank',-2720,-4350,245),('east_low_flank',-2180,-4320,180)]
CLOUD={'min':[-2653.443359375,594.208923339844,-4661.7880859375],'max':[-1848.7890625,800.850708007812,-4230.63427734375]}

def require(v,msg):
    if not v: raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def area(p):return .5*sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))
def inside(p):
    signs=[]
    for a,b in zip(POLYGON,POLYGON[1:]+POLYGON[:1]):signs.append((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
    return min(signs)>=-1e-9 or max(signs)<=1e-9

def clip_rect(poly,box):
    """Sutherland-Hodgman with retained Y or delta at affine edge intersections.
    Each vertex is [X,Z,value]. Rectangle is [xmin,xmax,zmin,zmax].
    """
    out=[list(p) for p in poly]
    for axis,limit,lower in [(0,box[0],True),(0,box[1],False),(1,box[2],True),(1,box[3],False)]:
        inp=out;out=[]
        if not inp:break
        a=inp[-1];ia=a[axis]>=limit if lower else a[axis]<=limit
        for b in inp:
            ib=b[axis]>=limit if lower else b[axis]<=limit
            if ia!=ib:
                u=(limit-a[axis])/(b[axis]-a[axis]);out.append([a[j]+u*(b[j]-a[j]) for j in range(3)])
            if ib:out.append(b)
            a=b;ia=ib
    return out

def ray_box(a,b,box):
    lo,hi=0.,1.
    for i in range(3):
        d=b[i]-a[i]
        if d==0:
            if not box['min'][i]<=a[i]<=box['max'][i]:return None
        else:
            q=sorted([(box['min'][i]-a[i])/d,(box['max'][i]-a[i])/d]);lo=max(lo,q[0]);hi=min(hi,q[1])
            if lo>hi:return None
    return [lo,hi]

class Terrain:
    def __init__(self,data):
        self.tiles={t['node'].split('/')[-1]:t for t in data['terrain'] if t['node'].split('/')[-1] in TARGETS}
        self.tri=[];self.grid=collections.defaultdict(list);self.vertex_tiles=collections.defaultdict(set)
        for name,t in self.tiles.items():
            t['tri']=np.asarray(t['faces'],float).reshape(-1,3,3)
            for ti,tri in enumerate(t['tri']):
                idx=len(self.tri);self.tri.append((name,ti,tri))
                for p in tri:self.vertex_tiles[(float(p[0]),float(p[2]))].add(name)
                for x in range(math.floor(tri[:,0].min()/32),math.floor(tri[:,0].max()/32)+1):
                    for z in range(math.floor(tri[:,2].min()/32),math.floor(tri[:,2].max()/32)+1):self.grid[x,z].append(idx)
    def sample(self,x,z):
        for i in self.grid[math.floor(x/32),math.floor(z/32)]:
            name,ti,t=self.tri[i];a,b,c=t;den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
            if den==0:continue
            u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
            v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den
            if min(u,v,1-u-v)>=-1e-8:return float(u*a[1]+v*b[1]+(1-u-v)*c[1])
        raise ValueError(('missing source triangle',x,z))

def project(p,v):
    e=np.array(v['eye']);f=np.array(v['target'])-e;f=f/np.linalg.norm(f);r=np.cross(f,[0,1,0]);r=r/np.linalg.norm(r);u=np.cross(r,f);q=np.array(p)-e;dep=q@f;t=math.tan(math.radians(v['fov']/2));uv=[.5+(q@r)/(2*dep*t*(1179/664)),.5-(q@u)/(2*dep*t)]
    return {'uv':uv,'pixels_1179x664':[uv[0]*1179,uv[1]*664],'depth_m':float(dep),'cloud_aabb_ray_interval':ray_box(v['eye'],p,CLOUD)}

def prepare():
    sources=[TERRAIN,INTAKE,R/'source-assets/north-ridge62-intake/plan.json',E/'process-report.json',E/'wrapper-report.json',E/'native-proxy-meshes.json',E/'source-specific-keep-reconcile.json',R/'ref/1131.png',R/'ref/1347.png']
    pins={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sources}
    w=read(E/'wrapper-report.json');k=read(E/'source-specific-keep-reconcile.json');n=read(E/'native-proxy-meshes.json');p=read(R/'source-assets/north-ridge62-intake/plan.json');intake=read(INTAKE)
    require(w['passed'] and w['process']['returncode']==0 and not w['changed_inputs'],'actual native terminal')
    require(sha(TERRAIN)==p['reuse_geometry_sha256'],'original saved terrain SHA')
    require(intake['saved_data_read_complete'] and intake['issues']==[] and not intake['all_occupancy_complete'],'actual bounded saved intake')
    require(w['native_report_sha256']==sha(E/'native-proxy-meshes.json') and w['keep_reconcile_sha256']==sha(E/'source-specific-keep-reconcile.json'),'native SHA binding')
    require(n['passed'] and len(n['visual_meshes'])==6 and n['issues']==[],'six native source identities')
    require(w['dependency_guard_before']==w['dependency_guard_after'] and w['dependency_guard_after']['reviewed_closure_files']==1483,'native unchanged closure')
    rows=k['path_index_keep_reconcile'];keys=[(r['path'],r['index'])for r in rows]
    require(len(keys)==676 and len(set(keys))==676 and sum(r['design_union_hit'] for r in rows)==575,'exact source keep membership')
    require(k['saved_groups_requeried']==775 and k['saved_instances_requeried']==57797 and k['proxy_only_query_count']==0,'bounded source scope')
    require(k['protected_saved_instance_counts']=={'coast56_-4_-4':243,'coast61_-5_-5':81},'whole neighbor saved instance counts')
    require(not k['deletion_authorized'] and not w['all_occupancy_complete'] and not w['runtime_collision_observed'],'limits retained')
    for t in intake['terrain']:
        if t['tile'] in TARGETS:require(t['same_bound_resource_and_transform_as_sha_pinned_53d'],'native terrain reuse '+t['tile'])
    t=Terrain(read(TERRAIN));require(len(t.tiles)==6,'six saved base tiles')
    # Use exact original mesh XZ for semantic peaks; no lost peak from coarse raster resampling.
    interior_vertices=sorted(q for q in t.vertex_tiles if inside(q))
    controls=[]
    for i,(x,z) in enumerate(POLYGON):controls.append({'name':f'zero_boundary_{i}','xz':[x,z],'base_y':t.sample(x,z),'target_y':t.sample(x,z),'delta_y':0.})
    for name,x,z,y in CONTROLS:
        q=min(interior_vertices,key=lambda q:(q[0]-x)**2+(q[1]-z)**2);b=t.sample(*q)
        controls.append({'name':name,'requested_xz':[x,z],'xz':list(q),'snap_distance_m':math.dist(q,(x,z)),'base_y':b,'target_y':y,'delta_y':max(0.,y-b)})
    xy=np.array([c['xz'] for c in controls]);dv=np.array([c['delta_y']for c in controls]);dt=Delaunay(xy)
    # Freeze the one-ring of every original triangle outside the local polygon.
    # Also freeze original low/wet triangles with an 80 m XZ guard, using actual saved geometry.
    frozen=set();wet=[]
    for _,_,tri in t.tri:
        if not all(inside((q[0],q[2]))for q in tri):frozen.update((float(q[0]),float(q[2]))for q in tri)
        if tri[:,1].min()<=14:wet.append([float(tri[:,0].min()-80),float(tri[:,0].max()+80),float(tri[:,2].min()-80),float(tri[:,2].max()+80)])
    for q in interior_vertices:
        if any(b[0]<=q[0]<=b[1] and b[2]<=q[1]<=b[3]for b in wet):frozen.add(q)
    frozen_tree=cKDTree(np.array(sorted(frozen)))
    candidate_y={};delta={}
    for q in t.vertex_tiles:
        si=int(dt.find_simplex(q));v=0.
        if q not in frozen and si>=0:
            a=dt.transform[si,:2].dot(np.array(q)-dt.transform[si,2]);v=max(0.,float(np.r_[a,1-a.sum()].dot(dv[dt.simplices[si]])))
        # Shared canonical sampling for altered seam vertices only, exact one float32 result.
        distance=float(frozen_tree.query(q)[0]);u=min(1.,distance/72.);collar=u*u*(3.-2.*u);v*=collar
        old=t.sample(*q);candidate_y[q]=f32(old+v) if v>1e-6 else None;delta[q]=v
    changed_tri=[];tile_report={};patch=[];seam_report=[]
    for name,tile in t.tiles.items():
        touched=0;vmap={};maxraise=0.;oldxz=[];newxz=[]
        for ti,tri in enumerate(tile['tri']):
            aft=tri.copy()
            for j,q in enumerate(tri):
                key=(float(q[0]),float(q[2]));ny=candidate_y[key]
                if ny is not None:aft[j,1]=ny;vmap[tuple(float(a)for a in q)]=ny;maxraise=max(maxraise,ny-q[1])
            if not np.array_equal(tri,aft):
                require(all(inside((q[0],q[2]))for q in tri),'changed triangle escaped local polygon')
                require(tri[:,1].min()>14,'original wet face altered')
                touched+=1;changed_tri.append((name,ti,tri,aft))
            require(np.array_equal(tri[:,[0,2]],aft[:,[0,2]]),'XZ moved')
        tile_report[name]={'unique_changed_vertices':len(vmap),'changed_original_triangles':touched,'max_raise_m':float(maxraise),'native_topology_change':False}
        if vmap:patch.append({'tile':name,'vertex_y_overrides':[{'before_xyz':list(q),'candidate_y':y}for q,y in sorted(vmap.items())]})
    require(tile_report['Ground_-4_-5']['changed_original_triangles']==0 and tile_report['Ground_-3_-5']['changed_original_triangles']==0,'southern two target tiles frozen')
    for a,b,axis,val in [('Ground_-4_-7','Ground_-3_-7',0,-2304),('Ground_-4_-6','Ground_-3_-6',0,-2304),('Ground_-4_-7','Ground_-4_-6',2,-4608),('Ground_-3_-7','Ground_-3_-6',2,-4608)]:
        maps=[{(float(q[0]),float(q[2])):float(q[1])for tr in t.tiles[nm]['tri']for q in tr if q[axis]==val} for nm in [a,b]];require(set(maps[0])==set(maps[1]),'source seam XZ membership')
        active=[q for q in maps[0]if candidate_y[q]is not None];oldmax=max(abs(maps[0][q]-maps[1][q])for q in maps[0]);seam_report.append({'tiles':[a,b],'source_matching_xz':len(maps[0]),'source_y_gap_max_m':oldmax,'modified_shared_vertices':len(active),'new_modified_y_gap_m':0.,'unmodified_seam_values_preserved':True})
    # Complete triangle/AABB clipping checks actual evaluated triangles, not only control points.
    cb=[CLOUD['min'][0]-40,CLOUD['max'][0]+40,CLOUD['min'][2]-40,CLOUD['max'][2]+40];cloud_max=-math.inf;cloud_count=0
    for _,_,before,after in changed_tri:
        cl=clip_rect([[q[0],q[2],q[1]]for q in after],cb)
        if cl:cloud_count+=1;cloud_max=max(cloud_max,max(q[2]for q in cl))
    require(cloud_max<=CLOUD['min'][1]-40,'candidate cloud spatial guard failed')
    decisions=[];counts=collections.Counter();classcounts=collections.Counter()
    for row in rows:
        b=row['combined_conservative_bounds'];box=[b['min'][0],b['max'][0],b['min'][2],b['max'][2]];hits=[];mins=[];maxs=[]
        for name,ti,before,after in changed_tri:
            if max(before[:,0])<box[0]or min(before[:,0])>box[1]or max(before[:,2])<box[2]or min(before[:,2])>box[3]:continue
            cl=clip_rect([[q[0],q[2],after[j,1]-q[1]]for j,q in enumerate(before)],box)
            if cl and max(q[2]for q in cl)>1e-6:hits.append([name,ti]);mins.append(min(q[2]for q in cl));maxs.append(max(q[2]for q in cl))
        tr=row['world_transform_columns'];x,y,z=tr[9:];root_delta=None
        try:
            # Current numerical proposal samples the global controller, not actual foot geometry.
            si=int(dt.find_simplex((x,z)))
            if si<0:root_delta=0.
            else:
                a=dt.transform[si,:2].dot(np.array([x,z])-dt.transform[si,2]);root_delta=max(0.,float(np.r_[a,1-a.sum()].dot(dv[dt.simplices[si]])))
        except ValueError:pass
        action='preserve_exact_no_affected_geometry'if not hits else 'solve_exact_foot_support_before_integration'
        if row['protected_neighbor']:
            require(not hits,'protected neighbor footprint influenced');action='preserve_exact_protected_neighbor'
        high_tree=bool(hits and row['class']in ['pine','oak','poplar']and root_delta is not None and y+root_delta>420.)
        if high_tree:action='individual_low_shoulder_relocation_proposal_required'
        counts[action]+=1;classcounts[(row['class'],action)]+=1
        decisions.append({'path':row['path'],'index':row['index'],'source_buffer_sha256':row['buffer_sha256'],'resource':row['resource'],'class':row['class'],'protected_neighbor':row['protected_neighbor'],'original_world_transform_columns':row['world_transform_columns'],'original_combined_bounds':b,'design_box_hit':row['design_union_hit'],'action':action,'intersected_changed_triangles':hits,'candidate_controller_root_raise_m_not_seating':root_delta,'conservative_footprint_raise_range_m':[min(mins),max(maxs)]if hits else [0.,0.],'candidate_root_above_proposed_420m_tree_line':high_tree,'placement_written':False,'support_proved':False})
    require(len(decisions)==676 and sum(bool(r['intersected_changed_triangles'])for r in decisions)>0,'individual inventory')
    projected={c['name']:{key:project([*c['xz'][:1],c['target_y'],c['xz'][1]],v)for key,v in p['fixed_reference_views'].items()}for c in controls if not c['name'].startswith('zero_')}
    # 3D candidate is source-only. Report historical gaps rather than changing old evidence.
    result={'status':'bounded_source_design_preparation_only','actual_native_intake_checked':True,'native_run':False,'blend_created':False,'world_modified':False,'all_occupancy_complete':False,'runtime_collision_observed':False,'visual_acceptance':False,'reference_catalog_file_present':(R/'reviews/reference-catalog-20260908.json').exists(),'native_terminal_seconds':w['process']['wall_seconds'],'source_keep_scope':{'query':676,'design':575,'groups':775,'instances':57797,'proxy_only':0,'protected_neighbor_counts':k['protected_saved_instance_counts']},'polygon_xz':POLYGON,'perimeter_collar_m':72,'collar_policy':'smoothstep nearest frozen vertex distance; no tile-edge falloff','polygon_area_m2':abs(area(POLYGON)),'intake_rectangle_area_m2':1008*1390,'controls':controls,'control_triangles':dt.simplices.tolist(),'design_heights_are_not_acceptance_thresholds':True,'numpy_version':np.__version__,'scipy_version':scipy.__version__,'original_triangles_checked':len(t.tri),'changed_triangles':len(changed_tri),'tiles':tile_report,'seams':seam_report,'cloud_spatial_guard':{'actual_aabb':CLOUD,'xz_padding_m':40,'required_below_min_y_m':40,'intersecting_changed_triangles':cloud_count,'candidate_max_y_in_padded_xz':cloud_max,'minimum_vertical_box_clearance_m':CLOUD['min'][1]-cloud_max,'spatial_pass':True,'actual_mesh_occlusion_proved':False,'main_peak_reference_ray_intersects_box':True},'projected_controls':projected,'instance_decision_counts':dict(counts),'class_decision_counts':[{'class':c,'action':a,'count':v}for(c,a),v in sorted(classcounts.items())],'untouched_instances_minimum':57797-sum(bool(r['intersected_changed_triangles'])for r in decisions),'source_pins':pins,'limits':['Candidate terrain is not native Blender/Godot output','Exact foot/support and visibility must be solved for each affected index before world integration','Root delta and full visual AABB relief are not continuous contact proof','Actual cloud silhouette/occlusion and renderer visibility not tested','Saved roads have centerline/control-hull evidence, not runtime width','Existing unmodified seams retain measured source millimetre gaps','No change to weather, sky group, camera or original resources']}
    require({str(s.relative_to(R)):sha(s)for s in sources}=={k:v['sha256']for k,v in pins.items()},'input change during design')
    return result,{'scope':'exact original 676-query list; zero deletions; all other source slots bit-preserved','rows':decisions}, {'status':'numerical_vertex_proposal_not_native_asset','tiles':patch}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r,s,v=prepare()
    if a.write:
        for name,val in [('candidate-plan.json',r),('instance-support-plan.json',s),('candidate-vertex-y.json',v)]:
            (D/name).write_text(json.dumps(val,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':r['status'],'tiles':r['tiles'],'cloud_guard':r['cloud_spatial_guard'],'instances':r['instance_decision_counts'],'changed_triangles':r['changed_triangles'],'source_only':True},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
