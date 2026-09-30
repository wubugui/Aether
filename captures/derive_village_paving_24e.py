from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'tools/prepare_village_paving_24d.py').read_text(encoding='utf-8').replace('24d','24e')
start=code.index('    # Morphological filtering')
end=code.index('    for i,level in enumerate(ordered):',start)
code=code[:start]+'''    # Extensiveness is essential: never erode a high road edge down to the
    # group's lowest floor. Closing fills narrow depressions; union with the
    # original superlevel explicitly preserves every pre-existing high point.
    raw_bands={level:shapely.union_all(polygons,grid_size=1e-5) for level,polygons in bands.items()}
    filtered={};previous=footprint;ordered=sorted(raw_bands)
    superlevels={}
    for level in ordered:
        original=shapely.union_all([poly for h,poly in raw_bands.items() if h>=level-1e-7])
        closed=original.buffer(.20,join_style=1,quad_segs=4).buffer(-.20,join_style=1,quad_segs=4)
        region=shapely.union_all([original,closed]).intersection(footprint).intersection(previous)
        assert original.difference(region).area<.001,(name,level,'closing eroded original floor')
        superlevels[level]=region;previous=region
''' +code[end:]
(root/'tools/prepare_village_paving_24e.py').write_text(code,encoding='utf-8')
code=(root/'blender/model_village_paving_24d.py').read_text(encoding='utf-8').replace('24d','24e')
(root/'blender/model_village_paving_24e.py').write_text(code,encoding='utf-8')
