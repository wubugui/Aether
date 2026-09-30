from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/check_island_30a.py').read_text().replace('30a','30b')
s=s.replace("assert len(native)==20", "assert len(native)==20\nassert e['old']['island_c grass and exposed rock terrain']==e['new']['island_c grass and exposed rock terrain']\nassert e['old']['island_c terrain fitted keeper paths']==e['new']['island_c terrain fitted keeper paths']")
p=R/'captures/check_island_30b.py';assert not p.exists();p.write_text(s)
s=(R/'tools/render_lantern_island_30a.py').read_text().replace('30a','30b')
s=s.replace('C/D30b native land proportion and full-size occupied-site rebuild. Buildings/trees re-grounded; D position/orientation intentionally changed.', 'C/D30b local fractured coast and short embedded rock roots; 30a terrain/path/pads and authored D placement retained. Buildings/trees re-grounded with new collision meshes.')
p=R/'tools/render_lantern_island_30b.py';assert not p.exists();p.write_text(s)
print('30b native reopener and same-world GPU driver prepared')
