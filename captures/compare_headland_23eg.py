from pathlib import Path
import json,math
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
e=root/'captures/headland_study_23e';f=root/'captures/headland_study_23g'
old=read(e/'terrain-design.json');new=read(f/'terrain-design.json');layout=read(f/'layout.json')
rows=[]
for k,boundary in enumerate(layout['boundary']):
    x,z=boundary['position'];index=min(range(len(layout['vertices'])),key=lambda i:math.hypot(layout['vertices'][i][0]-x,layout['vertices'][i][2]-z))
    assert math.hypot(layout['vertices'][index][0]-x,layout['vertices'][index][2]-z)<.001
    rows.append({'boundary_index':k,'vertex':index,'role':boundary['role'],'XZ':[x,z],'designed_shore_y':boundary['height'],'original_ground_y':new['original_ground'][index],'23e_y':old['heights'][index],'23g_y':new['heights'][index],'delta':new['heights'][index]-old['heights'][index]})
eligible=[]
def segment_distance(x,z,a,b):
    ax,az=a['position'];bx,bz=b['position'];dx,dz=bx-ax,bz-az
    t=max(0,min(1,((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz)))
    return math.hypot(x-ax-t*dx,z-az-t*dz)
for row in rows:
    if row['role']!='shore':continue
    x,z=row['XZ']
    seam=min(segment_distance(x,z,a,b) for a,b in zip(layout['boundary'],layout['boundary'][1:]+layout['boundary'][:1]) if a['height'] is None or b['height'] is None)
    if seam<24:continue
    expected=max(row['original_ground_y']+.05,row['designed_shore_y'])
    row['expected_shore_y']=expected;row['shore_error']=row['23g_y']-expected;eligible.append(row)
assert eligible and max(abs(r['shore_error']) for r in eligible)<.001, sorted(eligible,key=lambda r:-abs(r['shore_error']))[:3]
report={'scope':'Same-layout source design height comparison; source and actual GLB remain subject to independent verification. Transition endpoints follow source ground and are not all dry-land seams.','boundary':rows,'changed_boundary_vertices':[r for r in rows if abs(r['delta'])>.001],'pads':new['pads'],'shore_constraint_passed':True,'verified_nontransition_shore_vertices':len(eligible),'shore_max_error':max(abs(r['shore_error']) for r in eligible)}
target=root/'reviews/round-23g-shore-source-comparison.json';assert not target.exists();target.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'changed_boundary_vertices':len(report['changed_boundary_vertices']),'boundary37':rows[37],'pad_max_error':max(r['max_height_error'] for r in new['pads'])},ensure_ascii=False))
