"""Preserve the completed six geological assets; fix the keeper's side-pane basis."""
from pathlib import Path
root=Path(__file__).resolve().parents[1];target=root/'blender/model_lantern_islands_20c.py';assert not target.exists()
text=(root/'blender/model_lantern_islands_20b.py').read_text()
text=text.replace("OUT=ROOT/'captures/lantern_islands_study_20b'","OUT=ROOT/'captures/lantern_islands_study_20c'")
start=text.index("island('island_a',1.,1.,24.,0)")
end=text.index("reset()\nbox('Keeper broad masonry footing'",start)
text=text[:start]+'''# These already checked geological assets retain their exact native/export identity.
prior=ROOT/'captures/lantern_islands_study_20b'
for record in json.loads((prior/'model-report.json').read_text())['assets']:
    if record['name']=='keeper_house':continue
    for extension in ['.blend','.glb']:shutil.copy2(prior/(record['name']+extension),OUT/(record['name']+extension))
    reports.append(record)

'''+text[end:]
old="beam(name+' window glazing '+str(k),p((a+b)/2,c,.04),p((a+b)/2,d,.04),b-a,.035,glass)"
new="""pane=[p(u,z,depth) for depth in [.025,.06] for u,z in [(a,c),(b,c),(b,d),(a,d)]]
            mesh(name+' window glazing '+str(k),pane,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],glass)"""
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace("'label':'20b'","'label':'20c'")
target.write_text(text);print(target)
