from foot_geometry57b import *
ROOT=D.parents[2]
fresh=json.loads((D/'candidate-blend-readback.json').read_text())
zero=json.loads((D/'zero-change-readback.json').read_text())
props=json.loads((D/'candidate-props-readback.json').read_text())
seated=json.loads((D/'scatter-replacements-seated.json').read_text())
placement_scope=json.loads((D/'placement-scope57b.json').read_text())
design=json.loads((D/'static-design-checks.json').read_text())
checks=[];notes={}
def check(name,condition,details=None):
    checks.append({'name':name,'passed':bool(condition),'details':details})
    if not condition:raise AssertionError(name)
def native(a,i):return np.array(a,np.int32 if i==12 else np.float32)
A=source['surfaces'][0]['arrays'];B=fresh['arrays'];p=native(A[0],0);q=native(B[0],0);f=native(A[12],12).reshape(-1,3)
for i in [0,1,2,3,12]:
    check('Original Blender native field '+str(i)+' exact',native(zero['arrays'][i],i).tobytes()==native(A[i],i).tobytes())
    check('Fresh candidate native field '+str(i)+' matches planned',native(B[i],i).tobytes()==native(candidate['surface_arrays'][i],i).tobytes())
check('Original absent fields remain absent',A[4:12]==B[4:12]==[None]*8)
moved=np.any(p!=q,1);changed=moved[f].any(1);fixed=np.unique(f[~changed]);w=p.astype(float)+origin
inside=(w[:,0]>box[0])&(w[:,0]<box[1])&(w[:,2]>box[2])&(w[:,2]<box[3]);protected=~inside[f].all(1)
for i in [0,1,2,3]:
    a=native(A[i],i);b=native(B[i],i)
    if i==2:a=a.reshape(-1,4);b=b.reshape(-1,4)
    check('Unchanged faces preserve all raw field '+str(i),a[fixed].tobytes()==b[fixed].tobytes())
check('Original XZ exactly retained',p[:,[0,2]].tobytes()==q[:,[0,2]].tobytes())
check('Original indices and colors exactly retained',native(A[12],12).tobytes()==native(B[12],12).tobytes() and native(A[3],3).tobytes()==native(B[3],3).tobytes())
check('No modified face crosses expanded envelope',not np.any(changed&protected),int(protected.sum()))
boundary=np.any((p[:,[0,2]]==0)|(p[:,[0,2]]==768),1)
check('All four tile edges exactly retained',p[boundary].tobytes()==q[boundary].tobytes())
check('Open native topology retained',design['old_topology']==design['candidate_topology'])
c0=np.array(source['collider_faces'],np.float32);c1=np.array(candidate['collider_faces'],np.float32);flat=f.ravel();cm=moved[flat]
check('Changed collision corners directly match native vertices',c1[cm].tobytes()==q[flat[cm]].tobytes())
check('Every other original collision corner exact',c0[~cm].tobytes()==c1[~cm].tobytes())
check('Original mesh/collider difference not enlarged',np.max(abs(c1-q[flat]))<=np.max(abs(c0-p[flat])))
check('Target original mesh has no alternate LOD/shadow geometry',source['shadow_mesh_absent'] and source['stored_surface_lod_counts']==[0])

intake=json.loads((D/'intake/intake.json').read_text());original_rows={(g['node'],r['index']):r for g in intake['scatter']['groups'] for r in g['instances']}
declared={(r['node'],r['index']):r for r in placement_scope['relocations']}
sr={(r['node'],r['index']):r for r in seated};check('All sixty actual roots retained',len(sr)==len(original_rows)==60)
for key,r in sr.items():
    old=np.array(r['before_buffer'],np.float32);new=np.array(r['candidate_buffer'],np.float32);basis=[0,1,2,4,5,6,8,9,10]
    check('Native source buffer exact '+str(key),old.tobytes()==np.array(original_rows[key]['original_buffer'],np.float32).tobytes())
    check('Basis preserved '+str(key),old[basis].tobytes()==new[basis].tobytes())
    if key in declared:
        check('Declared XZ candidate exact '+str(key),new.tobytes()==np.array(declared[key]['candidate_buffer'],np.float32).tobytes())
    else:check('Other XZ exact '+str(key),old[[3,11]].tobytes()==new[[3,11]].tobytes())
    minimum={'pine':3.,'bush':1.5,'rock':.5}[r['kind']]
    check('Original minimum shore-height guard '+str(key),r['candidate_support']['height']>=minimum)
check('Exactly seven individually declared relocations',len(declared)==7 and sum(r['xz_relocated'] for r in seated)==7)

geoms={g['mesh']:g for g in geometry['groups']}
for path,g in geoms.items():
    data=props['meshes'][path];s=g['surfaces'][0]
    for field in ['vertices','indices','colors','normals']:
        dt=np.int32 if field=='indices' else np.float32
        check('Fresh prop mesh '+path+' '+field,np.array(data[field],dt).tobytes()==np.array(s[field],dt).tobytes())

seen=set();max_matrix_delta=0.;fresh_feet=[]
for r in props['placements']:
    key=(r['node'],r['index']);planned=sr[key];phase=r['phase'];expected=np.array(planned['candidate_buffer' if phase=='Candidate' else 'before_buffer'],np.float32);stored=np.array(r['stored_native_buffer'],np.float32);matrix=np.array(r['matrix_native_buffer'],np.float32)
    check('Fresh raw native placement buffer exact '+phase+str(key),stored.tobytes()==expected.tobytes())
    check('Fresh Blender translation exact '+phase+str(key),matrix[[3,7,11]].tobytes()==expected[[3,7,11]].tobytes())
    delta=float(np.max(abs(matrix-expected)));max_matrix_delta=max(max_matrix_delta,delta)
    # Blender's displayed object rotation decomposes to quaternion/scale. Original
    # native buffer above remains byte-exact authority; actual display pose is also checked.
    bound=16*np.finfo(np.float32).eps*max(1,float(abs(expected[[0,1,2,4,5,6,8,9,10]]).max()))
    check('Blender display pose finite float32 decomposition '+phase+str(key),delta<=bound,delta)
    seen.add((key,phase))
    if phase=='Candidate':
        actual=feet(planned,matrix,terrain_data[1]);record={'node':key[0],'index':key[1],'matrix_delta_max':delta,'actual_fresh_feet':actual};fresh_feet.append(record)
        if expected.tobytes()!=np.array(planned['before_buffer'],np.float32).tobytes():check('Actual fresh full foot contact '+str(key),actual['max_air_gap_m']<=EPS,actual)
check('Fresh original and candidate props complete',len(seen)==120 and len(fresh_feet)==60)
notes['max_blender_display_matrix_component_delta']=max_matrix_delta
notes['matrix_delta_does_not_relax_native_buffers']='Original and candidate native buffers were separately compared byte-for-byte. Blender display matrix decomposition is verified through the actual rendered foot surfaces.'

# Relocated bases must remain mutually clear after all relocations, not just
# relative to old neighboring positions during the search.
clearances=[]
for key,rr in declared.items():
    r=sr[key];model=models[r['node']];world=actual_world(r['candidate_buffer'],r['source_group_origin'],np.concatenate(model['polys']));root=np.array(r['candidate_position']);radius=float(np.linalg.norm(world[:,[0,2]]-root[[0,2]],axis=1).max())
    nearest=None
    for okey,other in sr.items():
        if okey==key:continue
        ow=actual_world(other['candidate_buffer'],other['source_group_origin'],np.concatenate(models[other['node']]['polys']));op=np.array(other['candidate_position']);other_radius=float(np.linalg.norm(ow[:,[0,2]]-op[[0,2]],axis=1).max());distance=float(np.linalg.norm(root[[0,2]]-op[[0,2]]));gap=distance-radius-other_radius
        if nearest is None or gap<nearest['clearance_m']:nearest={'other':str(okey),'clearance_m':gap}
    check('Relocated foot neighborhood final clearance '+str(key),nearest['clearance_m']>=.5,nearest);clearances.append({'node':key[0],'index':key[1],**nearest})

lineage=json.loads((D/'lineage.json').read_text())
for path,digest in lineage['immutable_project_files'].items():check('Existing project preserved '+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest)
frozen=json.loads((D.parent/'freeze-manifest57a.json').read_text())
check('Every frozen57A file byte-identical',all(hashlib.sha256((D.parent/path).read_bytes()).hexdigest()==digest for path,digest in frozen['files'].items()))
report={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'notes':notes,'changed_triangles':int(changed.sum()),'unchanged_triangles':int((~changed).sum()),'protected_triangles':int(protected.sum()),'moved_saved_vertices':int(moved.sum()),'fresh_feet':fresh_feet,'final_relocation_neighbor_clearance':clearances,'limits':'Static exact native source plus actual fresh Blender pose/foot geometry, not saved Godot world integration, runtime collision, visual or flight acceptance.'}
(D/'verified-saved57b.json').write_text(json.dumps(report,indent=2)+'\n')
print('SAVED57B_VERIFIED',report['passed'],report['check_count'],report['notes'])
