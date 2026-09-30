from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'tools/prepare_village_paving_24c.py').read_text(encoding='utf-8').replace('24c','24d')
start=code.index('    def field(x,z):')
end=code.index('    minx,minz,maxx,maxz=',start)
code=code[:start]+'''    # Euclidean Lipschitz roadbed bounds honor every entry and courtyard, while
    # allowing deliberate localized terrain cuts where the existing slope is too high.
    grade_limit=.30
    for a in patches:
        for b in patches:
            assert abs(a['height']-b['height'])<=grade_limit*a['polygon'].distance(b['polygon'])+.001,('Incompatible fixed road levels',name,a['house'],b['house'])
    def limits(x,z):
        p=Point(x,z);distances=[patch['polygon'].distance(p) for patch in patches]
        return max(patch['height']-grade_limit*d for patch,d in zip(patches,distances)),min(patch['height']+grade_limit*d for patch,d in zip(patches,distances))
'''+code[end:]
old='    seed=np.unique(np.round(seed,7),axis=0);dt=Delaunay(seed)'
new='''    seed=np.unique(np.round(seed,7),axis=0)
    seed_levels=[]
    for x,z in seed:
        lower,upper=limits(x,z);seed_levels.append(max(lower,min(upper,ground(x,z)+.08)))
    seed_levels=np.array(seed_levels)
    def field(x,z):
        lower,upper=limits(x,z)
        cone=float(np.max(seed_levels-grade_limit*np.linalg.norm(seed-np.array([x,z]),axis=1)))
        return max(lower,min(upper,cone))
    dt=Delaunay(seed)'''
assert old in code;code=code.replace(old,new)
code=code.replace("levels=sorted(set([round(v,7) for v in np.arange(0,50,.15)]+[round(p['height'],7) for p in patches]))","levels=[round(v,7) for v in np.arange(0,50,.15)]")
old="top=min(v for v in levels if v>=high-1e-6);bands[top].append(Polygon([(p[0],p[1]) for p in triangle]));continue"
new="top=next((p['height'] for p in patches if abs(p['height']-high)<1e-6),min(v for v in levels if v>=high-1e-6));bands[round(top,7)].append(Polygon([(p[0],p[1]) for p in triangle]));continue"
assert old in code;code=code.replace(old,new)
anchor='    solids=[];band_rows=[]'
insertion='''    # Morphological filtering of nested superlevel regions removes isolated thin
    # humps and slots. Exact 1.15m entrance aprons and the courtyard remain protected.
    raw_bands={level:shapely.union_all(polygons,grid_size=1e-5) for level,polygons in bands.items()}
    filtered={};previous=footprint;ordered=sorted(raw_bands)
    superlevels={}
    for level in ordered:
        region=shapely.union_all([poly for h,poly in raw_bands.items() if h>=level-1e-7])
        region=region.buffer(-.20,join_style=1,quad_segs=4).buffer(.20,join_style=1,quad_segs=4)
        region=region.buffer(.20,join_style=1,quad_segs=4).buffer(-.20,join_style=1,quad_segs=4)
        region=region.intersection(footprint).intersection(previous);superlevels[level]=region;previous=region
    # Any sub-millimetre edge strips trimmed by morphology inherit the lowest floor.
    for i,level in enumerate(ordered):
        higher=superlevels[ordered[i+1]] if i+1<len(ordered) else Polygon()
        region=(footprint if i==0 else superlevels[level]).difference(higher).difference(patch_union)
        filtered[level]=region
    for patch in patches:
        height=round(patch['height'],7);filtered[height]=shapely.union_all([filtered.get(height,Polygon()),patch['polygon'].intersection(footprint)])
    bands={h:pieces(poly) for h,poly in filtered.items() if not poly.is_empty and poly.area>.0001}
    grading_bands=[{'height':h,'geojson':shapely.to_geojson(shapely.union_all(polygons,grid_size=1e-5))} for h,polygons in bands.items()]
    grading_footprint=footprint.buffer(.65,join_style=1,quad_segs=4).difference(shapely.union_all(obstacles))
'''
assert anchor in code;code=code.replace(anchor,insertion+anchor)
code=code.replace("'solids':solids}","'solids':solids,'grading_bands':grading_bands,'grading_footprint_geojson':shapely.to_geojson(grading_footprint),'grade_limit':grade_limit}")
code=code.replace("'headland_glb_sha256':plan['headland_glb_sha256']","'headland_glb_sha256':plan['headland_glb_sha256']")
(root/'tools/prepare_village_paving_24d.py').write_text(code,encoding='utf-8')
code=(root/'blender/model_village_paving_24c.py').read_text(encoding='utf-8').replace('24c','24d')
(root/'blender/model_village_paving_24d.py').write_text(code,encoding='utf-8')
