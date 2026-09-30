from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/audit_island_30b_runtime.py').read_text().replace('lantern-island-30b-20260908T181107Z-79169d5784aa499ea0429f797ff3fc6e','lantern-island-30h-20260908T191003Z-b60fbd9ddc33459aa01a7396a355b6db').replace('30b','30h')
exec(compile(s,str(__file__),'exec'))
