"""Blend intersecting road profiles continuously instead of a nearest-route switch."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lantern_islands_20l.py';assert not target.exists()
text=(root/'blender/model_lantern_islands_20k.py').read_text()
text=text.replace('lantern_islands_study_20k','lantern_islands_study_20l').replace("'label':'20k'","'label':'20l'")
old='        distance,grade=min((closest_profile(point,p) for p in profiles),key=lambda pair:pair[0])'
new='''        nearby=[closest_profile(point,p) for p in profiles]
        distance=min(d for d,z in nearby)
        # A hard nearest-route boundary created a 17 cm discontinuity beside
        # the A junction. A compact, smooth crossfall blend makes the shared
        # road bed continuous, while distant branches have exactly no effect.
        weighted=[]
        for d,z in nearby:
            influence=max(0.,1.-(d/5.)**2)**3
            if influence>0.:weighted.append((influence,z))
        grade=sum(w*z for w,z in weighted)/sum(w for w,z in weighted) if weighted else 0.'''
assert text.count(old)==1;text=text.replace(old,new)
target.write_text(text);print(target)
