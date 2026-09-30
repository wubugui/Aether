from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'tools/render_lantern_island_29b.py';assert not p.exists()
s=(R/'tools/render_lantern_island_29a.py').read_text().replace('29a','29b')
s=s.replace('C/D geological remodeling over actual20l path/terrain','C/D peripheral terrain and low/wide rock remodeling with protected20l path/pad/tree support')
s=s.replace("'model-report.json','geometry-evidence.json','builder.py'","'model-report.json','geometry-evidence.json','builder.py','terrain-plan.json'")
s=s.replace('Native29b preserves terrain/path','Native29b preserves paths and protected support triangles while remodeling peripheral terrain')
p.write_text(s,encoding='utf-8')
print(p)
