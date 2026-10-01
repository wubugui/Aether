from foot_geometry57b import *

original={};initial={};neighbor_radii={}
for r in rows:
    key=(r['node'],r['index']);original[key]=feet(r,r['before_buffer'],terrain_data[0]);initial[key]=feet(r,r['candidate_buffer'],terrain_data[1])
    poly=np.concatenate(models[r['node']]['polys']);world=actual_world(r['before_buffer'],r['source_group_origin'],poly)
    root=np.array(r['before_position']);neighbor_radii[key]=float(np.linalg.norm(world[:,[0,2]]-root[[0,2]],axis=1).max())

def evaluate(r,dx,dz):
    key=(r['node'],r['index']);b=np.array(r['before_buffer'],np.float32);g=np.array(r['source_group_origin'],np.float32);pos=np.array(r['before_position'],float)
    b[3]=np.float32(b[3]+dx);b[11]=np.float32(b[11]+dz)
    x,z=map(float,(b[[3,11]]+g[[0,2]]).astype(np.float32));hit=height(terrain_data[1],x,z)
    if hit is None:return None
    y,ti=hit;minimum={'pine':3.,'rock':.5,'bush':1.5}[r['kind']]
    if y<minimum:return None
    b[7]=np.float32(y+r['preserved_origin_offset']-float(g[1]))
    base=feet(r,b,terrain_data[1]);seat=max(0.,base['signed_max_gap']+SEAT_PAD)
    model=models[r['node']];scale=abs(float(b[5]));max_extra=(model['first_segment']*.5 if r['kind']=='pine' else model['max_y']/3)*scale
    if seat>max_extra:return None
    b[7]=np.float32(b[7]-seat)
    final=feet(r,b,terrain_data[1])
    max_bury=(model['first_segment']*.5 if r['kind']=='pine' else model['height']*.5)*scale
    if final['max_air_gap_m']>EPS or final['max_penetration_m']>max_bury:return None
    full_foot=actual_world(b,r['source_group_origin'],np.concatenate(model['polys']))
    lo=full_foot.min(0);hi=full_foot.max(0)
    if lo[0]<=box[0] or hi[0]>=box[1] or lo[2]<=box[2] or hi[2]>=box[3]:return None
    if dx or dz:
        for other in rows:
            okey=(other['node'],other['index'])
            if okey==key:continue
            distance=math.hypot(x-other['before_position'][0],z-other['before_position'][2])
            if distance<neighbor_radii[key]+neighbor_radii[okey]+.5:return None
    return {'buffer':b.tolist(),'terrain_height':y,'terrain_triangle':ti,'seat_depth_from_root_point':seat,'horizontal_move':[x-pos[0],z-pos[2]],'horizontal_distance':math.hypot(x-pos[0],z-pos[2]),'max_extra_seat_allowed_by_model':max_extra,'max_burial_allowed_by_model':max_bury,'feet':final}

placements=[];relocations=[]
for r in rows:
    key=(r['node'],r['index']);old=original[key];unseated=initial[key]
    b=np.array(r['before_buffer'],np.float32);pre=np.array(r['candidate_buffer'],np.float32)
    affected=not np.array_equal(b,pre) or abs(unseated['signed_max_gap']-old['signed_max_gap'])>EPS or abs(unseated['max_penetration_m']-old['max_penetration_m'])>EPS
    if not affected:
        placements.append({'node':r['node'],'index':r['index'],'kind':r['kind'],'affected':False,'original':old,'unseated':unseated,'final':unseated,'before_buffer':r['before_buffer'],'candidate_buffer':r['candidate_buffer'],'horizontal_distance':0.})
        continue
    chosen=evaluate(r,0,0)
    if chosen is None:
        candidates=[]
        for dx in range(-44,45,2):
            for dz in range(-24,25,2):
                distance=math.hypot(dx,dz)
                if distance>44 or distance==0:continue
                candidates.append((distance,dx,dz))
        candidates.sort()
        for distance,dx,dz in candidates:
            chosen=evaluate(r,dx,dz)
            if chosen is not None:break
        assert chosen is not None,('No physical support within bounded search',r['node'],r['index'])
        relocations.append({'node':r['node'],'index':r['index'],'kind':r['kind'],**{k:v for k,v in chosen.items() if k not in ['feet','buffer']}})
    r['candidate_buffer']=chosen['buffer'];b=np.array(chosen['buffer'],np.float32);g=np.array(r['source_group_origin'],np.float32);r['candidate_position']=(b[[3,7,11]]+g).astype(np.float32).astype(float).tolist()
    r['xz_relocated']=chosen['horizontal_distance']>0;r['xz_distance']=chosen['horizontal_distance'];r['foot_seat_depth']=chosen['seat_depth_from_root_point'];r['candidate_origin_offset']=r['candidate_position'][1]-chosen['terrain_height'];r['candidate_support']['height']=chosen['terrain_height'];r['candidate_support']['triangle_index']=chosen['terrain_triangle']
    placements.append({'node':r['node'],'index':r['index'],'kind':r['kind'],'affected':True,'original':old,'unseated':unseated,'final':chosen['feet'],'before_buffer':r['before_buffer'],'candidate_buffer':r['candidate_buffer'],**{k:v for k,v in chosen.items() if k not in ['feet','buffer']}})

report={'status':'B source placement candidate; independent visual/native readback still required','foot_contact_method':'Exact convex foot-polygon versus terrain-triangle intersection; extrema of plane differences occur at intersection vertices. Full footprint coverage checked per polygon. Pine actual base ring; rock/bush actual lower surfaces clipped at root plane.','evaluation_bound_metres':EPS,'rounding_seat_pad_metres':SEAT_PAD,'basis_preserved_for_all':all(np.array(r['before_buffer'],np.float32)[[0,1,2,4,5,6,8,9,10]].tobytes()==np.array(r['candidate_buffer'],np.float32)[[0,1,2,4,5,6,8,9,10]].tobytes() for r in rows),'placements':placements,'relocations':relocations,'count':len(rows),'affected_count':sum(p['affected'] for p in placements),'max_final_air_gap_on_affected':max(p['final']['max_air_gap_m'] for p in placements if p['affected']),'unchanged_original_foot_conditions_retained':True,'limits':'Continuous lower-foot contact, not full rigid-body stability or runtime collision. Model-based burial limits prevent solving gaps by hiding most of an object. Existing unaffected placements preserve baseline defects.'}
assert report['basis_preserved_for_all']
(D/'scatter-replacements-seated.json').write_text(json.dumps(rows,indent=2)+'\n')
(D/'diagnostics-foot57b/continuous-foot-support57b.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='placements'},indent=2))
