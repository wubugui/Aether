from pathlib import Path
src=(Path(__file__).parent/'round-31c-back-cleft-bank-check.py').read_text(encoding='utf-8').split('rows=[]')[0]
exec(compile(src,'31c_actual_section_helpers','exec'))
def parameters(g,line):
 if g.is_empty:return []
 if g.geom_type=='LineString':return [[min(line.project(Point(x)) for x in g.coords),max(line.project(Point(x)) for x in g.coords)]]
 return sorted([i for sub in g.geoms for i in parameters(sub,line)]) if hasattr(g,'geoms') else []
rows=[]
for z in [2.137,4.137,6.137]:
 a,b,c=section(old[key],z),section(new[key],z),section(operand,z)
 for x in [-2.637,-3.637,-4.637]:
  line=LineString([[x,0],[x,20]]);oi=parameters(a.intersection(line),line);ni=parameters(b.intersection(line),line);ci=parameters(c.intersection(line),line);gaps=[]
  for left,right in zip(oi,oi[1:]):
   if right[0]-left[1]<1e-5:continue
   gap=LineString([line.interpolate(left[1]),line.interpolate(right[0])]);ll=LineString([line.interpolate(left[0]),line.interpolate(left[1])]);rl=LineString([line.interpolate(right[0]),line.interpolate(right[1])]);lp=ll.intersection(c).length;rp=rl.intersection(c).length;miss=gap.difference(b).length;cmiss=gap.difference(c).length
   gaps.append({'gap_y_m':[left[1],right[0]],'gap_width_m':gap.length,'operand_overlap_low_y_bank_m':lp,'operand_overlap_high_y_bank_m':rp,'actual_new_unfilled_gap_m':miss,'operand_unfilled_gap_m':cmiss,'both_banks_connected':lp>.01 and rp>.01 and miss<1e-5 and cmiss<1e-5})
  rows.append({'x_m':x,'z_m':z,'old_solid_y_intervals_m':oi,'new_solid_y_intervals_m':ni,'operand_y_intervals_m':ci,'gaps':gaps})
out={'scope':'Bounded Y crosscuts near the two directly located rear-wall pixel positions, which have similar X but separated Y. Actual30k/31c mainGLB sections plus third operand; no whole support rerun.','rows':rows,'positive_bilateral_crosscuts':sum(any(g['both_banks_connected'] for g in r['gaps']) for r in rows)}
(R/'reviews/round-31c-back-cleft-local-crosscheck.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
