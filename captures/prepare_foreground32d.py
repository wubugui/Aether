from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];plan=json.loads((R/'captures/foreground32c-design-plan.json').read_text(encoding='utf-8'));plan['scope']=plan['scope'].replace('32c','32d')+'32c stopped before save/export because CDT also retained exterior faces from crossing grading constraints;32d explicitly retains only triangles inside the authored crest boundary.'
p=R/'captures/foreground32d-design-plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2),encoding='utf-8')
s=(R/'blender/model_foreground_island_32c.py').read_text(encoding='utf-8').replace('32c','32d')
s=s.replace("tris=[list(f) for f in pt];assert all(len(f)==3 for f in tris)","tris=[list(f) for f in pt if inside(sum((pv[i] for i in f),Vector((0,0)))/len(f),boundary)];assert all(len(f)==3 for f in tris)")
s=s.replace("x,y,z=top[vi];dist,i,t,h=near_edge(x,y);assert dist<1e-4", "x,y,z=top[vi];dist,i,t,h=near_edge(x,y);assert dist<1e-4,('Unexpected nonshore boundary',vi,[x,y,z],dist)")
p=R/'blender/model_foreground_island_32d.py';assert not p.exists();p.write_text(s,encoding='utf-8')
