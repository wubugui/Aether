from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'tools/render_lantern_island_30b.py').read_text().replace('30b','30c')
s=s.replace('C/D30c local fractured coast and short embedded rock roots; 30a terrain/path/pads and authored D placement retained. Buildings/trees re-grounded with new collision meshes.', 'C/D30c welded actual terrain/main-bedrock exterior removes perimeter collar; 30a terrain top/path/pads and authored D placement,30b17rocks retained. Buildings/trees re-grounded with new collision meshes.')
p=R/'tools/render_lantern_island_30c.py';assert not p.exists();p.write_text(s)
print('30c same-world five-view driver prepared')
