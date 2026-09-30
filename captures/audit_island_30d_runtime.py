from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/audit_island_30b_runtime.py').read_text().replace('lantern-island-30b-20260908T181107Z-79169d5784aa499ea0429f797ff3fc6e','lantern-island-30d-20260908T183203Z-dfad421d9cb14734824e8942e33ac04c').replace('30b','30d')
exec(compile(s,str(__file__),'exec'))
