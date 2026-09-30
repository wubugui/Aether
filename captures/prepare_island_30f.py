from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]
p=R/'captures/island-30f-faceted-cut-plan.json';assert not p.exists();shutil.copy2(R/'captures/island-30e-faceted-cut-plan.json',p)
s=(R/'blender/model_lantern_island_30e.py').read_text().replace('30e','30f')
s=s.replace("mod.solver='EXACT'","mod.solver='MANIFOLD'")
s=s.replace('min(old_height,a*p.x+b*p.y+c)','(a*p.x+b*p.y+c)')
s=s.replace('plan.update(scope=',"plan.update(boolean_solver='MANIFOLD',lower_floor_clamped_to_source=False,scope=")
p=R/'blender/model_lantern_island_30f.py';assert not p.exists();p.write_text(s)
for a,b in [('captures/check_island_30e.py','captures/check_island_30f.py'),('tools/render_lantern_island_30e.py','tools/render_lantern_island_30f.py')]:
    p=R/b;assert not p.exists();p.write_text((R/a).read_text().replace('30e','30f'))
print('30f prepared: same projected design; unconstrained desired floor; manifold boolean')
