"""Protect actual lighthouse foundation extent rather than the oversized old grading pad."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lantern_islands_20k.py';assert not target.exists()
text=(root/'blender/model_lantern_islands_20j.py').read_text()
text=text.replace('lantern_islands_study_20j','lantern_islands_study_20k').replace("'label':'20j'","'label':'20k'")
start=text.index('        # Protect each actual structure platform')
end=text.index('        return value',start)
block=text[start:end]
old='            d=max(abs(u)-wx,abs(v)-wy,0.)'
new='''            # 19h tower foundation bound is 4.015 m; the 6.3 m authoring
            # platform was unnecessarily flattening the approach outside it.
            gx,gy=(4.2,4.2) if wx>6. else (wx,wy)
            d=max(abs(u)-gx,abs(v)-gy,0.)'''
assert block.count(old)==1;block=block.replace(old,new)
text=text[:start]+block+text[end:]
target.write_text(text);print(target)
