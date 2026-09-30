"""Preserve 20f failure; split tile caps into planar facets in the new candidate."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lantern_islands_20g.py';assert not target.exists()
text=(root/'blender/model_lantern_islands_20f.py').read_text()
text=text.replace('lantern_islands_study_20f','lantern_islands_study_20g').replace("'label':'20f'","'label':'20g'")
old="            loft('Keeper staggered roof tile %d %d %d'%(side,row,col),[[(x,y,z-.095) for x,y,z in vertices],vertices],roof)"
new="""            lower=[(x,y,z-.095) for x,y,z in vertices]
            faces=[(0,5,2,1),(5,4,3,2),(6,7,8,11),(11,8,9,10)]
            faces.extend([(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)])
            mesh('Keeper staggered roof tile %d %d %d'%(side,row,col),lower+vertices,faces,roof)"""
assert text.count(old)==1;text=text.replace(old,new)
target.write_text(text);print(target)
