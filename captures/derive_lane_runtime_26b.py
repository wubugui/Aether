from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'tools/render_village_paving_25f.py').read_text().replace('25f','26b').replace('village_paving_study_24m','village_paving_study_26b').replace('round-24m-village-paving-native-check','round-26b-village-paving-native-check')
p=p.replace('courtyard/paving/contour stairs','courtyard/continuous inclined paving')
(R/'tools/render_village_paving_26b.py').write_text(p,encoding='utf-8')
s=(R/'captures/village_paving_runtime_25f.gd').read_text().replace('25f','26b')
s=s.replace('var at:=Vector3((a.x+b.x+c.x)/3.,solid.top_y,(a.y+b.y+c.y)/3.)','var expected_y:float=(float(solid.top_heights[ids[0]])+float(solid.top_heights[ids[1]])+float(solid.top_heights[ids[2]]))/3.\n\t\t\t\tvar at:=Vector3((a.x+b.x+c.x)/3.,expected_y,(a.y+b.y+c.y)/3.)')
s=s.replace('hit.position.y-float(solid.top_y)','hit.position.y-expected_y').replace('"expected_y":solid.top_y','"expected_y":expected_y')
(R/'captures/village_paving_runtime_26b.gd').write_text(s,encoding='utf-8')
