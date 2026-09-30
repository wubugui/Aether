from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'tools/prepare_village_paving_24g.py').read_text(encoding='utf-8').replace('24g','24h')
old="""    seed_levels=[]
    for x,z in seed:
        lower,upper=limits(x,z);seed_levels.append(max(lower,min(upper,ground(x,z)+.08)))
    seed_levels=np.array(seed_levels)"""
new="""    # Author a connected entry-to-courtyard stair grade rather than following
    # every dip in the old hill. The underlying editable ground is graded later.
    route_heights=[next(p['height'] for p in entries if p['house']==r['house']) for r in group['routes']]
    seed_levels=[]
    for x,z in seed:
        point=Point(x,z);lower,upper=limits(x,z);candidates=[]
        for line,entry_height in zip(lines,route_heights):
            along=line.project(point)
            t=max(0,min(1,(along-1.15)/max(.01,line.length-1.15)))
            height=entry_height+(court_y-entry_height)*t
            candidates.append(height-grade_limit*line.distance(point))
        preferred=max(min(p['height'] for p in patches),max(candidates))
        seed_levels.append(max(lower,min(upper,preferred)))
    seed_levels=np.array(seed_levels)"""
assert old in code;code=code.replace(old,new)
code=code.replace('return max(lower,min(upper,cone))',"return max(min(p['height'] for p in patches),lower,min(upper,cone))")
(root/'tools/prepare_village_paving_24h.py').write_text(code,encoding='utf-8')
code=(root/'blender/model_village_paving_24g.py').read_text(encoding='utf-8').replace('24g','24h')
(root/'blender/model_village_paving_24h.py').write_text(code,encoding='utf-8')
