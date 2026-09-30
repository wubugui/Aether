from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/audit_island_31a_runtime.py').read_text().replace('31a','31d')
exec(compile(s,str(__file__),'exec'))
