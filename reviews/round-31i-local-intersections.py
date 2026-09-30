from pathlib import Path
src=(Path(__file__).parent/'round-31f-local-intersections.py').read_text(encoding='utf-8').replace('lantern_island_study_31f','lantern_island_study_31i').replace('lantern_island_study_31e','lantern_island_study_31h').replace('differs from31e','differs from31h').replace('round-31f-','round-31i-').replace(" and r['changed_triangles_normal_reversal_count']==0", " and not r.get('actual_tree_upper_envelope_pending',True) and not r.get('shoulder_shared_edge_check_pending',True)")
exec(compile(src,'31i_actual_finite_triangle_sweep','exec'))
