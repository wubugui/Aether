from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'blender/model_headland_23f.py').read_text(encoding='utf-8').replace('headland_study_23f','headland_study_23g').replace("'label':'23f'","'label':'23g'")
old='target=max(old+.05,ridge_height)'
new='''# Rock spines rise behind the shore; they must not silently lift its authored edge.
    ridge_height=authored+(ridge_height-authored)*smooth(d/16)
    target=max(old+.05,ridge_height)'''
assert old in code;code=code.replace(old,new)
(root/'blender/model_headland_23g.py').write_text(code,encoding='utf-8')
for folder,name in [('captures','headland_runtime_23f.gd'),('tools','render_headland_23f.py')]:
    code=(root/folder/name).read_text(encoding='utf-8').replace('23f','23g')
    (root/folder/name.replace('23f','23g')).write_text(code,encoding='utf-8')
code=(root/'captures/compare_headland_23ef.py').read_text(encoding='utf-8').replace('headland_study_23f','headland_study_23g').replace('23f','23g')
anchor="report={'scope':"
validation='''eligible=[]
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
'''
code=code.replace(anchor,validation+anchor).replace("'pads':new['pads']","'pads':new['pads'],'shore_constraint_passed':True,'verified_nontransition_shore_vertices':len(eligible),'shore_max_error':max(abs(r['shore_error']) for r in eligible)")
(root/'captures/compare_headland_23eg.py').write_text(code,encoding='utf-8')
