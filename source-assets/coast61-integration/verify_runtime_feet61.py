"""Reconcile real GL61 exported arrays after its fresh runtime process has exited."""
from pathlib import Path
import argparse,sys,json,hashlib,numpy as np
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'source-assets/coast57/revision-b'
sys.dont_write_bytecode=True
sys.path.insert(0,str(S))
import foot_geometry57b as fg
import visible_geometry_core57b as vg

def terrain(faces,transform):
    t=np.array(faces,np.float32).astype(float).reshape(-1,3,3);m=np.array(transform,np.float32).reshape(3,4).astype(float)
    t=(t.reshape(-1,3)@m[:,:3].T+m[:,3]).reshape(-1,3,3);xz=t[:,:,[0,2]]
    return {'tri':t,'xz':xz,'min':xz.min(1),'max':xz.max(1),'planes':np.array([fg.plane(p) for p in t])}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('evidence',type=Path);args=ap.parse_args();E=args.evidence
    report=json.loads((E/'verify-report61.json').read_text());actual=json.loads((E/'runtime-native61.json').read_text());manifest=json.loads((D/'preparation-manifest.json').read_text());static=json.loads((D/'static-multimesh-authority.json').read_text())
    rows=json.loads((S/'scatter-replacements-seated.json').read_text());scope=json.loads((S/'placement-scope57b.json').read_text());allowed={(r['node'],r['index']) for r in scope['relocations']};checklist=[]
    def check(name,value,detail=None):
        checklist.append({'name':name,'passed':bool(value),'detail':detail})
        if not value:raise AssertionError(name)
    check('Actual terminal61 renderer gate required',report['passed'] and report['strict_saved_readback'] and report['live_support_cache_collision'] and report['inherited_1128_1216_toggle_passed'])
    check('Runtime export hash matches process report',hashlib.sha256((E/'runtime-native61.json').read_bytes()).hexdigest()==report['runtime_native_sha256'])
    candidate=json.loads((S/'candidate-native.json').read_text());source=json.loads((S/'native-authority/authority.json').read_text());idx=np.array(candidate['surface_arrays'][12],np.int32)
    expected_faces=np.array(candidate['surface_arrays'][0],np.float32)[idx]
    check('Actual indexed61 GPU faces exact original-order source mapping',np.array(actual['mesh_faces_source_order'],np.float32).tobytes()==expected_faces.tobytes())
    check('Actual native shape faces exact replacement',np.array(actual['shape_faces'],np.float32).tobytes()==np.array(candidate['collider_faces'],np.float32).tobytes())
    expected_transform=np.array([1,0,0,-3840,0,1,0,0,0,0,1,-3840],np.float32)
    check('Target actual world transform exact',np.array(actual['terrain_transform'],np.float32).tobytes()==expected_transform.tobytes() and np.array(actual['shape_transform'],np.float32).tobytes()==expected_transform.tobytes())
    native_mesh=terrain(actual['mesh_faces_source_order'],actual['terrain_transform']);native_shape=terrain(actual['shape_faces'],actual['shape_transform'])
    original_shape=terrain(source['collider_faces'],actual['shape_transform'])
    source_geometry={g['node']:g for g in json.loads((S/'diagnostics-foot57b/prop-foot-geometry.json').read_text())['groups']}
    for path,data in actual['groups'].items():
        check('Actual native instance and surface counts: '+path,int(data['instance_count'])==int(static[path]['instance_count']) and len(data['surfaces'])==len(source_geometry[path]['surfaces']))
        expected=np.array(static[path]['buffer'],np.float32)
        for change in static[path]['changed_rows']:
            for slot in change['changed_slots']:expected[int(change['index'])*12+int(slot)]=np.float32(change['after_buffer'][int(slot)])
        check('All81 actual GL instance buffers exact: '+path,np.array(data['buffer'],np.float32).tobytes()==expected.tobytes())
        check('Actual group world transform exact: '+path,np.array(data['global_transform'],np.float32).tobytes()==expected_transform.tobytes())
        for before,after in zip(source_geometry[path]['surfaces'],data['surfaces']):
            for field in ['vertices','indices','colors','normals']:
                dt=np.int32 if field=='indices' else np.float32
                check('Actual inherited native prop mesh '+path+' '+field,np.array(before[field],dt).tobytes()==np.array(after[field],dt).tobytes())
    check('Exactly four actual GL groups',set(actual['groups'])==set(static))
    outputs=[];radii={};positions={}
    for row in rows:
        key=(row['node'],row['index']);data=actual['groups'][row['node']];buffer=np.array(data['buffer'],np.float32).reshape(-1,12)[row['index']];planned=np.array(row['candidate_buffer'],np.float32);before=np.array(row['before_buffer'],np.float32)
        check('Actual root buffer matches declared61 placement '+str(key),buffer.tobytes()==planned.tobytes())
        check('Actual basis unchanged '+str(key),buffer[[0,1,2,4,5,6,8,9,10]].tobytes()==before[[0,1,2,4,5,6,8,9,10]].tobytes())
        if key not in allowed:check('Other XZ slots unchanged '+str(key),buffer[[3,11]].tobytes()==before[[3,11]].tobytes())
        mesh_foot=fg.feet(row,buffer,native_mesh);shape_foot=fg.feet(row,buffer,native_shape);original_foot=fg.feet(row,before,fg.terrain_data[0]);original_shape_foot=fg.feet(row,before,original_shape)
        affected=buffer.tobytes()!=before.tobytes()
        if affected:
            check('Continuous actual GL mesh/physics shape foot contact '+str(key),mesh_foot['max_air_gap_m']<=.001 and shape_foot['max_air_gap_m']<=.001,[mesh_foot,shape_foot])
            model=fg.models[row['node']];scale=abs(float(buffer[5]));max_extra=(model['first_segment']*.5 if row['kind']=='pine' else model['max_y']/3)*scale;max_bury=(model['first_segment']*.5 if row['kind']=='pine' else model['height']*.5)*scale
            check('Actual burial respects native model limits '+str(key),row.get('foot_seat_depth',0)<=max_extra and mesh_foot['max_penetration_m']<=max_bury+.001 and shape_foot['max_penetration_m']<=max_bury+.001)
        else:
            check('Original unaffected foot conditions retained '+str(key),mesh_foot['max_air_gap_m']<=original_foot['max_air_gap_m']+.001 and abs(mesh_foot['max_penetration_m']-original_foot['max_penetration_m'])<=.001 and shape_foot['max_air_gap_m']<=original_shape_foot['max_air_gap_m']+.001)
        visible_before=vg.measure(row,before,fg.terrain_data[0]);visible_after=vg.measure(row,buffer,native_mesh);area_ratio=visible_after['area_above_terrain_m2']/visible_before['area_above_terrain_m2'];top_ratio=visible_after['top_above_terrain_at_root_m']/visible_before['top_above_terrain_at_root_m']
        if affected:check('Actual visible geometry retention '+str(key),area_ratio>=(.95 if row['kind']=='pine' else .75)-.00001 and top_ratio>=(.95 if row['kind']=='pine' else 2/3)-.00001,[area_ratio,top_ratio])
        pos=(buffer[[3,7,11]]+np.array(row['source_group_origin'],np.float32)).astype(np.float32);positions[key]=pos
        world=fg.actual_world(buffer,row['source_group_origin'],np.concatenate(fg.models[row['node']]['polys']));radii[key]=float(np.linalg.norm(world[:,[0,2]]-pos[[0,2]],axis=1).max())
        root_height,_=fg.height(native_mesh,float(pos[0]),float(pos[2]));check('Original actual shore-height guard '+str(key),root_height>={'pine':3.,'rock':.5,'bush':1.5}[row['kind']])
        outputs.append({'node':row['node'],'index':row['index'],'kind':row['kind'],'affected':affected,'world_root':pos.tolist(),'actual_mesh_foot':mesh_foot,'actual_shape_foot':shape_foot,'above_terrain_area_ratio':area_ratio,'top_clearance_ratio':top_ratio,'visible_before':visible_before,'visible_after':visible_after,'native_buffer':buffer.tolist()})
    clearance=[]
    for key in sorted(allowed):
        others=[(float(np.linalg.norm(positions[key][[0,2]]-positions[o][[0,2]]))-radii[key]-radii[o],o) for o in positions if o!=key];gap,other=min(others)
        check('Actual final relocation-neighbor clearance '+str(key),gap>=.5,[other,gap]);clearance.append({'node':key[0],'index':key[1],'nearest':list(other),'clearance_m':gap})
    check('Actual60 roots,40 affected and7 relocations',len(outputs)==60 and sum(p['affected'] for p in outputs)==40 and len(allowed)==7)
    phases={r['phase'] for r in actual['support_phases']};check('Caches/physics tested before and after inherited views',phases=={'initial_coast','returned_after_1128_1216'} and len(actual['support_phases'])==120)
    for phase in phases:
        phase_rows=[r for r in actual['support_phases'] if r['phase']==phase]
        check('Actual native prop collider recipes '+phase,sum(r['native_prop_body']=='native pine capsule' for r in phase_rows)==51 and sum(r['native_prop_body']=='native rock mesh body' for r in phase_rows)==7 and sum(r['native_prop_body']=='bush intentionally has no native prop body' for r in phase_rows)==2)
    for path,digest in manifest['immutable_inputs'].items():check('Immutable source after GL+offline gate: '+Path(path).name,hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest)
    result={'passed':True,'check_count':len(checklist),'checks':checklist,'actual_native_data_sha256':report['runtime_native_sha256'],'placements':outputs,'relocation_clearances':clearance,'world_visual_acceptance':False,'limits':'Actual real-renderer buffers/native meshes/physics shape continuous foot geometry and cached root rays; not61 flight, hardware GPU, self-occlusion or all-reference visual acceptance.'}
    (E/'full-foot-report61.json').write_text(json.dumps(result,indent=2)+'\n');print('COAST61_ACTUAL_FULL_FOOT_PASS',len(checklist));return 0
if __name__=='__main__':raise SystemExit(main())
