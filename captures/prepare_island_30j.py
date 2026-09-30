from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=json.loads((R/'captures/island-30i-authored-cut-plan.json').read_text())
rows=[
 [[[-17,-14.8,13],[-4,-12.8,12.5],[5,-10,14]],
  [[-20,-22,6.5],[-5,-17.5,3.6],[4,-17,4.7]],
  [[-28,-35,4],[-6,-35,-3],[12,-30,4]]],
 [[[1.5,-9,14],[8,-7,13.5],[18,-4,14]],
  [[2,-14,4.7],[9,-11,3.4],[21,-8,6]],
  [[-1,-29,4],[12,-29,-2],[34,-15,4]]],
 [[[10,-10,14],[9,-1,13],[8,8,13]],
  [[15,-8,3.8],[15.5,-.5,3.4],[17,9,7]],
  [[36,-17,3],[36,0,-2],[33,18,3]]]]
for c,rs in zip(p['components'],rows):
    c['rows']=rs;c['actual_lower_vertices']=[v for r in rs for v in r]
p.update(scope='30j explicit broad middle break rows relocated to actual visible middle slope; southeast inner edge shifted off measured road cut. Source30d, no30h fluting. Two eastern trees proposed for refit to new lower broad shoulder; actual support and GPU required.',tree_relocations=[dict(old_xy=[14.04,-1.8],new_xy=[16.5,1],scale=.8),dict(old_xy=[15.12,-3.96],new_xy=[17.6,-5],scale=.55)])
dst=R/'captures/island-30j-authored-cut-plan.json';assert not dst.exists();dst.write_text(json.dumps(p,indent=2))
for a,b in [('blender/model_lantern_island_30i.py','blender/model_lantern_island_30j.py'),('captures/check_island_30i.py','captures/check_island_30j.py'),('tools/render_lantern_island_30i.py','tools/render_lantern_island_30j.py')]:
    dst=R/b;assert not dst.exists();dst.write_text((R/a).read_text().replace('30i','30j'))
print('30j explicit middle break rows and proposed eastern tree transforms prepared')
