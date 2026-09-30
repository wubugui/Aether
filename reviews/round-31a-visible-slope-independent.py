from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R/'reviews/round-30d-visible-slope-independent.py').read_text(encoding='utf-8')
src=src.replace('lantern_island_study_30d','lantern_island_study_30k').replace('round-30d-visible-slope-localization.json','round-30k-visible-slope-localization.json').replace('lantern-island-30d-20260908T183203Z-dfad421d9cb14734824e8942e33ac04c','lantern-island-30k-r1-20260908T193210Z-09e7ff871c9941519a561b4fede063ee').replace('round-30d-visible-slope-independent.json','round-31a-visible-slope-independent.json')
exec(compile(src,'31a_current30k_ray_check','exec'))
out=R/'reviews/round-31a-visible-slope-independent.json';report=json.loads(out.read_text());report['scope']='Four current30k pixels: independent inverse projection and nearest actualGLB ray hit plus current protection distance. No full geometry/GPU rerun.'
for row in report['samples']:
 row['projection_note']='Projected triangle area can be zero for a vertical face; it is not a measure of visible image area or the whole broad slope.'
report['limits'].append('Root connected near-coplanar subsets and individual triangle areas must not be treated as all visible sloping slab area.');out.write_text(json.dumps(report,indent=2),encoding='utf-8')
