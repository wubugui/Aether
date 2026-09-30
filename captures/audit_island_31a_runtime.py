from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1]
s=(R/'captures/audit_island_30b_runtime.py').read_text()
s=s.replace("run=R/'captures/validation_runs/lantern-island-30b-20260908T181107Z-79169d5784aa499ea0429f797ff3fc6e'", "run=R/'captures/validation_runs'/sys.argv[1]")
s=s.replace('lantern-island-30a-20260908T180129Z-961944bd320b46a4bb5f15256ceb5c8f','lantern-island-30k-r1-20260908T193210Z-09e7ff871c9941519a561b4fede063ee').replace('30b','31a').replace('actual31a/30a','actual31a/30k')
exec(compile(s,str(__file__),'exec'))
