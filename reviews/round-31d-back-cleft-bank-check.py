from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'actual_glb_decoder','exec'))
from shapely.geometry import LineString
from shapely.ops import polygonize
helper=(R/'reviews/round-30b-independent-geometry.py').read_text();exec(helper[helper.index('def section'):helper.index('levels=')])
P=R/'captures/lantern_island_study_31d';e=json.loads((P/'geometry-evidence.json').read_text());new=glb(P/'island_c.glb');old=glb(R/'captures/lantern_island_study_30k/island_c.glb');key=next(k for k in new if 'olive grass' in k);ob=e['additions'][2]['actual_operand_geometry'];v=np.array(ob['vertices']);operand=np.array([v[[f[0],f[j],f[j+1]]] for f in ob['polygons'] for j in range(1,len(f)-1)])
def intervals(g):
 if g.is_empty:return []
 if g.geom_type=='LineString':return [[g.bounds[0],g.bounds[2]]]
 return sorted([i for sub in g.geoms for i in intervals(sub)]) if hasattr(g,'geoms') else []
rows=[]
for z in [2.137,4.137,6.137]:
 a,b,c=section(old[key],z),section(new[key],z),section(operand,z);assert min(a.area,b.area,c.area)>0
 for y in [7.137,9.137,11.137]:
  line=LineString([[-40,y],[40,y]]);oi=intervals(a.intersection(line));ni=intervals(b.intersection(line));ci=intervals(c.intersection(line));gaps=[]
  for left,right in zip(oi,oi[1:]):
   if right[0]-left[1]<1e-5:continue
   gap=LineString([[left[1],y],[right[0],y]]);left_line=LineString([[left[0],y],[left[1],y]]);right_line=LineString([[right[0],y],[right[1],y]])
   lp=left_line.intersection(c).length;rp=right_line.intersection(c).length;missing=gap.difference(b).length;omissing=gap.difference(c).length
   gaps.append({'gap_x_m':[left[1],right[0]],'gap_width_m':gap.length,'operand_overlap_left_bank_length_m':lp,'operand_overlap_right_bank_length_m':rp,'actual_new_unfilled_gap_length_m':missing,'operand_unfilled_gap_length_m':omissing,'both_banks_and_gap_connected_at_this_crosscut':lp>.01 and rp>.01 and missing<1e-5 and omissing<1e-5})
  rows.append({'z_m':z,'y_m':y,'old_solid_x_intervals_m':oi,'new_solid_x_intervals_m':ni,'operand_solid_x_intervals_m':ci,'old_gaps_between_banks':gaps})
out={'scope':'Bounded actual old30k/new31d GLB horizontal cross-sections and local x transects through rear cleft, including native third convex operand. Proves explicitly sampled bilateral bank penetration and old-gap closure, not total crevice or visual acceptance.','rows':rows,'positive_bilateral_transects':sum(any(g['both_banks_and_gap_connected_at_this_crosscut'] for g in row['old_gaps_between_banks']) for row in rows),'full_reference_accepted':False}
out['sampled_bilateral_connection_proven']=out['positive_bilateral_transects']>0
(R/'reviews/round-31d-back-cleft-bank-check.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
p=R/'reviews/round-31d-independent-geometry.json';r=json.loads(p.read_text());r['bounded_back_cleft_both_banks_check']={'report':'reviews/round-31d-back-cleft-bank-check.json','positive_bilateral_transects':out['positive_bilateral_transects'],'scope':out['scope']};p.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
