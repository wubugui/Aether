from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'tools/prepare_village_paving_24h.py').read_text(encoding='utf-8').replace('24h','24i')
old='        closed=original.buffer(.20,join_style=1,quad_segs=4).buffer(-.20,join_style=1,quad_segs=4)'
new='''        # Continue each existing high region beyond the road boundary before
        # closing. Treating every outside point as the lowest floor otherwise
        # preserves thin low notches that open onto a road edge.
        extended=shapely.union_all([original,original.buffer(.7,quad_segs=4).difference(footprint)])
        closed=extended.buffer(.30,join_style=1,quad_segs=4).buffer(-.30,join_style=1,quad_segs=4)'''
assert old in code;code=code.replace(old,new)
(root/'tools/prepare_village_paving_24i.py').write_text(code,encoding='utf-8')
code=(root/'blender/model_village_paving_24h.py').read_text(encoding='utf-8').replace('24h','24i')
(root/'blender/model_village_paving_24i.py').write_text(code,encoding='utf-8')
