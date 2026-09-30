from pathlib import Path
R=Path(__file__).resolve().parents[1]
original_print=print
print=lambda *args,**kwargs:None
src=(R/'reviews/round-30j-plan-independent.py').read_text(encoding='utf-8').replace('30j','30k')
exec(compile(src,'30k_plan_independent','exec'))
print=original_print
prior=json.loads((R/'captures/island-30j-authored-cut-plan.json').read_text());current=json.loads((R/'captures/island-30k-authored-cut-plan.json').read_text());edits=[]
for a,b in zip(prior['components'],current['components']):
 assert a['actual_lower_triangles']==b['actual_lower_triangles']
 for i,(va,vb) in enumerate(zip(a['actual_lower_vertices'],b['actual_lower_vertices'])):
  if va!=vb:edits.append({'component':b['name'],'vertex':i,'old':va,'new':vb})
report['independent_plan_changes_from30j']=edits
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'changed_vertices':edits,'road_pad_true_cut_free':report['road_pad_true_cut_free'],'component_support':[{'name':c['component'],'road':{k:v for k,v in c['protection_linear_height_intersections']['actual_road'].items() if k!='cut_patches'},'pads':{k:v for k,v in c['protection_linear_height_intersections']['expanded_pads'].items() if k!='cut_patches'}} for c in report['components']],'targets':report['six_visible_target_predicted_depths'],'new_trees':report['new_tree_trunk_radius_0_3m_top_envelope_support']},indent=2))
