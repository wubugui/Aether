from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1];out=R/'captures/village_grading_design_25e';assert not out.exists();out.mkdir()
shutil.copy2(R/'captures/village_grading_design_25d/grading.json',out/'grading.json')
shutil.copy2(R/'tools/prepare_village_grading_25d.py',out/'prepare-design.py')
p=(R/'tools/solve_village_earthworks_25d.py').read_text().replace("label='25d'","label='25e'")
p=p.replace("op,oh,ot,orr=prepare(rows);",'''# Identify the connected core; separate overlapping rocks are retained assets,
# not the original bedrock height field being edited by the Blender builder.
parent=list(range(len(rows)));lookup={}
def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
for i,row in enumerate(rows):
    for v in row['v']:
        key=tuple(v)
        if key in lookup:parent[find(i)]=find(lookup[key])
        else:lookup[key]=i
counts=Counter(find(i) for i in range(len(rows)));core=max(counts,key=counts.get)
core_rows=[r for i,r in enumerate(rows) if find(i)==core]
op,oh,ot,orr=prepare(core_rows);''')
(R/'tools/solve_village_earthworks_25e.py').write_text(p,encoding='utf-8')
shutil.copy2(R/'blender/grade_village_earthworks_25d.py',R/'blender/grade_village_earthworks_25e.py')
