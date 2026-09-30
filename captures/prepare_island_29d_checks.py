from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/check_island_29b.py').read_text().replace('29b','29d').replace('lantern_island_study_29a','lantern_island_study_29b')
s=s.replace("new[core]['vertices'][72:]","new[core]['vertices'][54:]")
s=s.replace("assert new[core]['polygons']==old[core]['polygons']","assert len(new[core]['vertices'])==54+n")
p=R/'captures/check_island_29d.py';assert not p.exists();p.write_text(s)
s=(R/'tools/render_lantern_island_29b.py').read_text().replace('29b','29d')
s=s.replace('C/D peripheral terrain and low/wide rock remodeling with protected20l path/pad/tree support','C/D29d connected terrain and original bedrock topology remodeling, retaining actual protected20l path/pad/tree support')
p=R/'tools/render_lantern_island_29d.py';assert not p.exists();p.write_text(s)
