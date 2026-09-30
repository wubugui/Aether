"""Expose lower entry treads above the measured harbor slope without moving the doorway."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lighthouse_19h.py';assert not target.exists()
text=(root/'blender/model_lighthouse_19g.py').read_text()
for old,new in [("OUT=ROOT/'captures/lighthouse_study_19g'","OUT=ROOT/'captures/lighthouse_study_19h'"),
                ('[(4.50,.24),(4.03,.48),(3.56,.72)]','[(4.50,.44),(4.03,.58),(3.56,.72)]')]:
    assert text.count(old)==1,old;text=text.replace(old,new)
target.write_text(text);print(target)
