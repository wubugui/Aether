from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/audit_island_30b_runtime.py').read_text().replace('lantern-island-30b-20260908T181107Z-79169d5784aa499ea0429f797ff3fc6e','lantern-island-30c-20260908T181715Z-31c81298860748f3ac9257c092e5f4b5').replace('30b','30c')
exec(compile(s,str(__file__),'exec'))
