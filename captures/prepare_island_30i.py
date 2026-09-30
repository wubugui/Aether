from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
specs=[
 dict(name='South broad oblique saddle',rows=[
  [[-16,-15,13],[-7,-14.8,12.7],[3,-12,14]],
  [[-20,-21,9],[-7,-21,3.8],[5,-19,8]],
  [[-28,-35,7],[-6,-35,-3],[12,-30,5]]]),
 dict(name='Southeast staggered apron',rows=[
  [[-1,-8,14],[8,-7,13.5],[18,-4,14]],
  [[0,-15,7.4],[9,-15,4.4],[22,-10,9]],
  [[-1,-29,4],[12,-29,-2],[34,-15,4]]]),
 dict(name='East broad turning shoulder',rows=[
  [[9,-9,14],[10,-1,13.5],[8,7,13.5]],
  [[18,-12,7.2],[20,-2,4],[17,9,8.4]],
  [[36,-17,4],[36,0,-2],[33,18,5]]])]
for spec in specs:
    v=[p for row in spec['rows'] for p in row];f=[]
    for row in range(2):
        for col in range(2):
            a=row*3+col;b=a+1;c=a+4;d=a+3
            f.extend([[a,b,d],[b,c,d]] if (row+col)%2 else [[a,b,c],[a,c,d]])
    # All lower facets have positive XY orientation for one-sided height comparisons.
    for tri in f:
        a,b,c=[v[i] for i in tri]
        if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:tri.reverse()
    spec.update(actual_lower_vertices=v,actual_lower_triangles=f)
plan=dict(scope='30i three authored broad bent lower surfaces, eight triangles each, independent middle break rows and no distance-to-boundary blend. Source30d; no30h fluted geometry retained. Tree relocation only if actual revised support requires it.',source='captures/lantern_island_study_30d/island_c.blend',components=specs)
p=R/'captures/island-30i-authored-cut-plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2))
s=(R/'blender/model_lantern_island_30h.py').read_text().replace('30h','30i')
start=s.index('input_plan=');end=s.index('    count=len(bottom);',start)
s=s[:start]+'''input_plan=json.loads((R/'captures/island-30i-authored-cut-plan.json').read_text())
cutters=input_plan['components']
for spec in cutters:
    bottom=spec['actual_lower_vertices'];faces=spec['actual_lower_triangles']
'''+s[end:]
s=s.replace("scope='30i independently tessellated southern/eastern visible main-slope faceted cutbacks. Real transition-bottom meshes taper from original surface to authored lower facets. Actual road/pad/tree masks subtracted with0.4m nominal margin. Complete path and17rocks retained; actual support, visible shape and runtime require checks.'", "scope=input_plan['scope']")
p=R/'blender/model_lantern_island_30i.py';assert not p.exists();p.write_text(s)
for a,b in [('captures/check_island_30h.py','captures/check_island_30i.py'),('tools/render_lantern_island_30h.py','tools/render_lantern_island_30i.py')]:
    p=R/b;assert not p.exists();p.write_text((R/a).read_text().replace('30h','30i'))
print('30i explicit3D cutter plan and native builder prepared')
