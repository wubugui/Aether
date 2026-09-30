from pathlib import Path
import json,math
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
e=root/'captures/headland_study_23e';f=root/'captures/headland_study_23f'
old=read(e/'terrain-design.json');new=read(f/'terrain-design.json');layout=read(f/'layout.json')
rows=[]
for k,boundary in enumerate(layout['boundary']):
    x,z=boundary['position'];index=min(range(len(layout['vertices'])),key=lambda i:math.hypot(layout['vertices'][i][0]-x,layout['vertices'][i][2]-z))
    assert math.hypot(layout['vertices'][index][0]-x,layout['vertices'][index][2]-z)<.001
    rows.append({'boundary_index':k,'vertex':index,'role':boundary['role'],'XZ':[x,z],'designed_shore_y':boundary['height'],'original_ground_y':new['original_ground'][index],'23e_y':old['heights'][index],'23f_y':new['heights'][index],'delta':new['heights'][index]-old['heights'][index]})
report={'scope':'Same-layout source design height comparison; source and actual GLB remain subject to independent verification. Transition endpoints follow source ground and are not all dry-land seams.','boundary':rows,'changed_boundary_vertices':[r for r in rows if abs(r['delta'])>.001],'pads':new['pads']}
target=root/'reviews/round-23f-shore-source-comparison.json';assert not target.exists();target.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'changed_boundary_vertices':len(report['changed_boundary_vertices']),'boundary37':rows[37],'pad_max_error':max(r['max_height_error'] for r in new['pads'])},ensure_ascii=False))
