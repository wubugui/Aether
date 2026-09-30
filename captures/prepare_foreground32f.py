from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];p=R/'captures/foreground32f-design-plan.json';assert not p.exists();plan=json.loads((R/'captures/foreground32e-design-plan.json').read_text(encoding='utf-8'));plan['scope']=plan['scope'].replace('32e','32f')+'32f corrects the exterior multiple-pad interpolation: inverse-distance weights tend continuously to each complete flat pad height at its boundary, rather than jumping from a conflicting averaged exterior target to the hard inner value. No pad, house, tree, coast, or rock design change.';p.write_text(json.dumps(plan,indent=2),encoding='utf-8')
s=(R/'blender/model_foreground_island_32e.py').read_text(encoding='utf-8').replace('32e','32f')
s=s.replace("if dist<3:changes.append((pad['height'],1-smooth(dist/3)))", "if dist<3:\n   t=dist/3;changes.append((pad['height'],(1-t)**2/(t*t+1e-12)))")
s=s.replace("w=max(v[1] for v in changes);h=sum(h*w for h,w in changes)/sum(w for h,w in changes);value=value*(1-w)+h*w", "value=(value+sum(h*w for h,w in changes))/(1+sum(w for h,w in changes))")
p=R/'blender/model_foreground_island_32f.py';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(R/'tools/render_foreground_island_32e.py').read_text(encoding='utf-8').replace('32e','32f');p=R/'tools/render_foreground_island_32f.py';assert not p.exists();p.write_text(s,encoding='utf-8')
