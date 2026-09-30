from pathlib import Path
R=Path(__file__).resolve().parents[1]
for path in ['tools/render_village_paving_25c.py','captures/village_paving_runtime_25c.gd']:
    source=R/path;dest=R/path.replace('25c','25f');assert not dest.exists()
    dest.write_text(source.read_text(encoding='utf-8').replace('25c','25f'),encoding='utf-8')
