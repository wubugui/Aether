from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'tools/render_rightcoast_33c.py').read_text(encoding='utf-8').replace('33c','33d');p=R/'tools/render_rightcoast_33d.py';assert not p.exists();p.write_text(s,encoding='utf-8')
print('33d renderer retains26b to33b to33d native provenance and actual paving validation')
