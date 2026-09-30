from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
specs=[
 dict(name='South short transverse shoulder',vertices=[
 [-18.5,-23,.5],[-12,-24,.5],[-7,-22.7,.5],[-5,-18,.5],[-11,-15.7,.5],[-18,-17.5,.5],
 [-17.8,-21.6,4.3],[-13.8,-22.2,5.8],[-8.5,-21.5,5.2],[-6.1,-19.4,4.8],
 [-15.9,-19.7,7.2],[-10.2,-20.3,7.6],[-8.2,-18.6,8.2],[-13.4,-17.8,8.1],[-17,-18.5,6.8]]),
 dict(name='Southeast cross turned blunt shoulder',vertices=[
 [-2.8,-16.8,.8],[1.5,-19.4,.8],[7.3,-18.4,.8],[9,-14.4,.8],[5.4,-10.8,.8],[-1,-11.2,.8],
 [-2,-15.7,5.1],[.8,-17.8,4.2],[5.6,-17.3,3.8],[7.4,-14.8,4.5],
 [-.4,-12.9,8.1],[2.7,-12,7.5],[5.8,-13.9,6.1],[1.5,-15.2,6.7]]),
 dict(name='North cleft short oblique cross shoulder',vertices=[
 [-7.8,7.4,-2.5],[-7.3,12.3,-2.5],[-3.8,14,-2.5],[1.6,11.7,-2.5],[1.2,6.1,-2.5],[-3.2,5.9,-2.5],
 [-6.9,10.9,3.3],[-3.8,13.4,2.9],[.7,11.2,3.9],
 [-5.4,8.6,6.2],[-2.2,9.7,5.9],[.6,7.5,6.9],[-1.7,6.2,8.8],[-4.1,6.8,7.4]])]
plan=R/'captures/island-31c-convex-shoulder-plan.json';assert not plan.exists()
plan.write_text(json.dumps(dict(scope='31c authored short transverse front shoulder, differently turned middle shoulder, and short oblique rear cleft connection. All three convex operands union into30k actual main exterior. Replaces31b fronts; no31a buttons. Real pad/road/current14tree support require checks; local rear domain y5.9+ is designed from actual31b ray/source evidence, not assumed old cutter attribution.',source='captures/lantern_island_study_30k/island_c.blend',components=specs),indent=2))
for source,target in [
 ('blender/model_lantern_island_31b.py','blender/model_lantern_island_31c.py'),
 ('captures/check_island_31b.py','captures/check_island_31c.py'),
 ('captures/make_island_31b_authoring_workspace.py','captures/make_island_31c_authoring_workspace.py'),
 ('tools/render_lantern_island_31b.py','tools/render_lantern_island_31c.py')]:
    p=R/target;assert not p.exists();s=(R/source).read_text().replace('31b','31c')
    s=s.replace('len(authoring)==2','len(authoring)==len(e[\'additions\'])').replace('len(objects)==2','len(objects)==len(e[\'additions\'])')
    s=s.replace('authoring_two_editable_solids_reopened=True','authoring_editable_solids_reopened=len(authoring)')
    s=s.replace('two_mesh_objects_reopened_in_normal_startup_scene=True','mesh_objects_reopened_in_normal_startup_scene=len(objects)')
    s=s.replace('Two editable shoulder operands','Three editable shoulder operands').replace('two selected editable operands','three selected editable operands')
    s=s.replace('two short broad convex shoulders','three authored front/rear short convex shoulders')
    s=s.replace('Vector((-5,-17,4))','Vector((-5,-5,4))').replace('view_distance=37','view_distance=60')
    if target.startswith('blender/'):
        s=s.replace('Three authored open-sided cutbacks expose existing low rock shoulders.','Three authored convex shoulders refine front rhythm and bridge the rear cleft locally.')
    p.write_text(s)
print('31c three independent editable hulls planned; source remains30k.')
