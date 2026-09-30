from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'tools/render_lantern_island_30c.py').read_text().replace('30c','30d')
s=s.replace('C/D30d welded actual terrain/main-bedrock exterior removes perimeter collar; 30a terrain top/path/pads and authored D placement,30b17rocks retained. Buildings/trees re-grounded with new collision meshes.', 'C/D30d authored native cutbacks of the welded main exterior to expose West/Southwest/North shoulders. Complete paths,17rocks and D placement retained. Buildings/trees re-grounded with actual cutback collision meshes.')
p=R/'tools/render_lantern_island_30d.py';assert not p.exists();p.write_text(s)
print('30d fixed five-view GPU driver prepared')
