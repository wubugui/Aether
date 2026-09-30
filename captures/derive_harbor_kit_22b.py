"""Close the measured deck/stringer gap while retaining the four other native assets."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'blender/model_harbor_kit_22b.py';assert not p.exists()
s=(root/'blender/model_harbor_kit_22a.py').read_text(encoding='utf-8')
s=s[:s.index('\nreset()\n# A genuinely open repair awning')]
s=s.replace('harbor_kit_study_22a','harbor_kit_study_22b')
s=s.replace("deck-.31),( .20", "deck-.30),( .20") if "deck-.31),( .20" in s else s
s=s.replace('(x,0,deck-.31),(.20,length+.2,.30)','(x,0,deck-.30),(.20,length+.2,.30)')
s=s.replace("'Recessed nail %02d %s'","'Flush deck nail %02d %s'").replace('(x,y,deck+.002),.018,.012','(x,y,deck-.004),.018,.008')
s+='''
prior=ROOT/'captures/harbor_kit_study_22a'
for asset in json.loads((prior/'model-report.json').read_text(encoding='utf-8'))['assets']:
    if asset['name'] in ['timber_pier','pier_landing']:continue
    for extension in ['.blend','.glb']:shutil.copy2(prior/(asset['name']+extension),OUT/(asset['name']+extension))
    reports.append(asset)
(OUT/'model-report.json').write_text(json.dumps({'label':'22b','production_modified':False,'assets':reports,'scope':'Only two pier modules changed: deck support stringers raised1cm to contact plank underside; nail tops flush. Four other22a modules retained byte-identically. Site ramps and full scene remain incomplete.'},indent=2))
print('HARBOR KIT BUILT22b '+str(sum(r['parts'] for r in reports)),flush=True)
'''
p.write_text(s,encoding='utf-8');print(p)
