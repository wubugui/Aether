from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R/'reviews/round-30f-independent-geometry.py').read_text(encoding='utf-8').replace('30f','30h')
exec(compile(src,'30h_actual_geometry','exec'))
out=R/'reviews/round-30h-independent-geometry.json';report=json.loads(out.read_text());report['joint_builder_changes']['cutter_tessellation']='30h constraints independent of source interior triangle edges, sampled cutter boundaries plus inset and anchors; see round-30h-plan-independent.json';report['joint_builder_changes']['causality']='30e/30f/30g failed.30h changes cutter tessellation while retaining MANIFOLD solver and unclamped floor; successful output does not alone isolate all earlier failure causes.';report['limits'] += ['30f and30g also have no accepted native export; neither is an asset baseline.'];out.write_text(json.dumps(report,indent=2),encoding='utf-8')
