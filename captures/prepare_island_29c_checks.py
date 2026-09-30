from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/check_island_29b.py').read_text().replace('29b','29c').replace('lantern_island_study_29a','lantern_island_study_29b')
s=s.replace("assert old[terrain]['polygons']==new[terrain]['polygons']","assert old[terrain]==new[terrain]")
s=s.replace("assert changed==plan['changed_top_vertices']","assert changed==0")
s=s.replace('assert len(new)==20','assert len(new)==24')
s=s.replace("'protected_terrain_vertices_unchanged':True","'terrain_unchanged_from_29b':True,'protected_terrain_vertices_unchanged':True")
p=R/'captures/check_island_29c.py';assert not p.exists();p.write_text(s)
s=(R/'tools/render_lantern_island_29b.py').read_text().replace('29b','29c')
s=s.replace("'builder.py','terrain-plan.json'","'builder.py','terrain-plan.json','shoulder-plan.json'")
s=s.replace('C/D peripheral terrain and low/wide rock remodeling with protected20l path/pad/tree support','C/D29b terrain plus29c diagonal summit-to-tidal buttresses with protected20l path/pad/tree support')
p=R/'tools/render_lantern_island_29c.py';assert not p.exists();p.write_text(s)
