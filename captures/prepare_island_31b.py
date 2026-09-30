from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
specs=[
 dict(name='South oblique convex shoulder',vertices=[
 [-19,-23,.5],[-12,-26,.5],[-5,-23,.5],[-3.5,-17,.5],[-11,-14.9,.5],[-18.5,-17,.5],
 [-18,-22.8,3.8],[-13,-24,4],[-6.5,-22,4.4],[-4.8,-18.8,5.4],
 [-16.2,-20.8,6.8],[-11,-22,5.7],[-7.6,-20.7,6.2],[-6.5,-16.2,9],[-12,-15.8,9.3],[-17,-18,7.9]]),
 dict(name='Southeast offset slanted knuckle',vertices=[
 [0,-19,1],[7,-19,1],[10,-14,1],[6.5,-9.7,1],[1,-10.5,1],[-1,-14,1],
 [1.2,-18.3,3.8],[6.5,-17.3,4.6],[8.8,-14.4,5.2],
 [6,-10.4,8.4],[1.5,-10.8,8.1],[-.5,-13.8,6.5],[2.4,-15.8,6.5],[5.5,-14.7,7]])]
p=R/'captures/island-31b-convex-shoulder-plan.json';assert not p.exists()
p.write_text(json.dumps(dict(scope='31b two authored irregular slanted convex shoulders united into30k main exterior. No31a flat heptagonal caps or equal-XY vertical rings retained. Broad roots and uneven rear-to-front slopes; current road/pad/14trees and17rocks require checks.',source='captures/lantern_island_study_30k/island_c.blend',components=specs),indent=2))
for a,b in [('blender/model_lantern_island_31a.py','blender/model_lantern_island_31b.py'),('captures/check_island_31a.py','captures/check_island_31b.py'),('captures/make_island_31a_authoring_workspace.py','captures/make_island_31b_authoring_workspace.py'),('tools/render_lantern_island_31a.py','tools/render_lantern_island_31b.py')]:
    p=R/b;assert not p.exists();p.write_text((R/a).read_text().replace('31a','31b').replace('NATIVE CUTBACKS SAVED','NATIVE CONVEX SHOULDERS SAVED'))
print('31b oblique short-rooted convex assets prepared from30k, not31a')
