"""Give overlapping tile courses explicit vertical separation; retain all six landforms."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lantern_islands_20h.py';assert not target.exists()
text=(root/'blender/model_lantern_islands_20g.py').read_text()
text=text.replace('lantern_islands_study_20g','lantern_islands_study_20h').replace("'label':'20g'","'label':'20h'")
start=text.index('# Rebuild only the C island:')
end=text.index("reset()\nbox('Keeper broad masonry footing'",start)
text=text[:start]+'''# All landforms are retained from the seven-view 20g candidate.
prior=ROOT/'captures/lantern_islands_study_20g'
for record in json.loads((prior/'model-report.json').read_text())['assets']:
    if record['name']=='keeper_house':continue
    for extension in ['.blend','.glb']:shutil.copy2(prior/(record['name']+extension),OUT/(record['name']+extension))
    reports.append(record)

'''+text[end:]
old='        z0,z1=6.85-2.65*lo,6.85-2.65*hi'
new='        bias=(6-row)*.018\n        z0,z1=6.85-2.65*lo+bias,6.85-2.65*hi+bias'
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace('(x1,ym,z1+.035)','(x1,ym,z1+.009)').replace('(x0,ym,z0+.035)','(x0,ym,z0+.009)')
text=text.replace('cross=[(-.19,6.78),(.19,6.78),(.18,6.89),(0,7.02),(-.18,6.89)]','cross=[(-.19,6.88),(.19,6.88),(.18,6.99),(0,7.12),(-.18,6.99)]')
text=text.replace('C island house pad repair and detailed keeper roof; five prior landforms byte-identical.','Overlapping roof courses have a measured vertical clearance; all six prior landforms byte-identical.')
target.write_text(text);print(target)
