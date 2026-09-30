from pathlib import Path
src=(Path(__file__).parent/'round-31f-local-intersections.py').read_text(encoding='utf-8').replace('lantern_island_study_31f','lantern_island_study_31g').replace('lantern_island_study_31e','lantern_island_study_31f').replace('differs from31e','differs from31f').replace('round-31f-','round-31g-').replace(" and r['changed_triangles_normal_reversal_count']==0", " and not r.get('actual_tree_upper_envelope_pending',True)")
exec(compile(src,'31g_actual_finite_triangle_sweep','exec'))
