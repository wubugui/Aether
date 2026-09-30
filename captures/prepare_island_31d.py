from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'captures/island-31d-convex-shoulder-plan.json';assert not p.exists()
plan=json.loads((R/'captures/island-31c-convex-shoulder-plan.json').read_text())
plan['components'][2]=dict(name='North cross cleft thick diagonal shoulder',vertices=[
 [-8,6.3,-2.5],[-7.3,12.3,-2.5],[-3.8,14,-2.5],[1.6,11.7,-2.5],[1.6,5.2,-2.5],[-1,3.9,-2.5],[-5.8,4.1,-2.5],
 [-7.2,9.8,3.4],[-3.8,13.4,2.9],[.7,11.2,3.9],
 [-6.5,6.9,5.9],[-4.5,9.7,5.3],[-.8,8.4,6.5],[1.1,6.4,6.3],[-2.4,4.3,8.8],[-5.1,5.3,7.4]])
plan['scope']='31d retains31c short front and cross-turned middle operands exactly, replaces only rear connection from30k. Rear domain extends across independently measured low-Y gap to thick diagonal root, no whole source vertex displacement. Candidate must prove both-bank connection and preserve actual occupied support; GPU must reject blade, plank or enlarged uniform slope.'
plan['revision_basis']='31c actual local crosscheck found0.87-2.68m low-Y gap. Broad actual rear operand changed; first two exact.'
p.write_text(json.dumps(plan,indent=2))
for a,b in [('blender/model_lantern_island_31c.py','blender/model_lantern_island_31d.py'),('captures/check_island_31c.py','captures/check_island_31d.py'),('captures/make_island_31c_authoring_workspace.py','captures/make_island_31d_authoring_workspace.py'),('tools/render_lantern_island_31c.py','tools/render_lantern_island_31d.py'),('captures/audit_island_31c_runtime.py','captures/audit_island_31d_runtime.py')]:
    p=R/b;assert not p.exists();p.write_text((R/a).read_text().replace('31c','31d'))
print('31d rear thick diagonal connection prepared; fronts exactly31c; native basis30k.')
