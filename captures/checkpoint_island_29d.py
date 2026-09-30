from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/checkpoint_islands_29ab.py').read_text()
start=s.index('runs=');end=s.index('\nfor label',start)
s=s[:start]+"runs={'29d':'lantern-island-29d-20260908T172214Z-8332ad44c9854fcca4d10e061507dda4'}"+s[end:]
exec(compile(s,str(__file__),'exec'))
