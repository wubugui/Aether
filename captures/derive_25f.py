from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1];out=R/'captures/village_grading_design_25f';assert not out.exists();out.mkdir()
shutil.copy2(R/'captures/village_grading_design_25e/grading.json',out/'grading.json')
shutil.copy2(R/'tools/prepare_village_grading_25d.py',out/'prepare-design.py')
p=(R/'tools/solve_village_earthworks_25e.py').read_text().replace("label='25e'","label='25f'")
p=p.replace("limit=max(.75,abs(float(prior[axis]))+.001)","limit=max(.80,abs(float(prior[axis]))+.05)")
p=p.replace("max(0.75, abs(original component)+0.001)","max(0.80, abs(original component)+0.05)")
p=p.replace("# Native float coordinates make microscopic planar discrepancies. Retain a\n# 0.1% allowance for pre-existing slopes, rather than demanding they be flattened.","# Feasibility diagnostic requires 0.044802 extra gradient for constrained old\n# interfaces. Use 0.05 explicitly, still bounding every newly graded face.")
(R/'tools/solve_village_earthworks_25f.py').write_text(p,encoding='utf-8')
shutil.copy2(R/'blender/grade_village_earthworks_25e.py',R/'blender/grade_village_earthworks_25f.py')
