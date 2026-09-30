from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'tools/prepare_village_paving_24e.py').read_text(encoding='utf-8').replace('24e','24f')
code=code.replace("poly=shapely.set_precision(poly.simplify(.0005,preserve_topology=True),1e-5)","poly=shapely.set_precision(poly.simplify(.0005,preserve_topology=True),.001)")
code=code.replace('a[2]>=level-1e-9 if above else a[2]<=level+1e-9','a[2]>=level if above else a[2]<=level')
code=code.replace('b[2]>=level-1e-9 if above else b[2]<=level+1e-9','b[2]>=level if above else b[2]<=level')
start=code.index('    bands=defaultdict(list)')
end=code.index('    # Extensiveness',start)
code=code[:start]+'''    bands=defaultdict(list)
    for triangle in region_triangles:
        triangle=[[x,z,round(h,6)] for x,z,h in triangle]
        polygon=Polygon([(p[0],p[1]) for p in triangle])
        low=min(v[2] for v in triangle);high=max(v[2] for v in triangle)
        if high-low<1e-6:
            top=next((p['height'] for p in patches if abs(p['height']-high)<1e-6),min(v for v in levels if v>=high-1e-7))
            bands[round(top,7)].append(polygon);continue
        # Partition by successive upper half-planes. Every triangle remainder
        # belongs to its highest band; no uncovered region gets a minimum floor.
        remaining=polygon
        relevant=[v for v in levels if v>=low-1e-7 and v<=high+.1500001]
        for level in relevant:
            if remaining.is_empty:break
            clipped=clip(triangle,level,False)
            region=Polygon([(p[0],p[1]) for p in clipped]) if len(clipped)>=3 else Polygon()
            region=shapely.make_valid(region).intersection(remaining)
            for piece in pieces(region):
                if piece.area>1e-12:bands[level].append(piece)
            remaining=remaining.difference(region)
        assert remaining.area<1e-8,(name,'unassigned triangle floor',remaining.area)
''' +code[end:]
code=code.replace('    filtered={};previous=footprint;ordered=sorted(raw_bands)', '''    raw_coverage=shapely.union_all(list(raw_bands.values()))
    missing=footprint.difference(raw_coverage)
    assert missing.area<.001,(name,'raw bands left a physical hole',missing.area)
    filtered={};previous=footprint;ordered=sorted(raw_bands)''')
code=code.replace("region=(footprint if i==0 else superlevels[level]).difference(higher).difference(patch_union)","region=superlevels[level].difference(higher).difference(patch_union)")
(root/'tools/prepare_village_paving_24f.py').write_text(code,encoding='utf-8')
code=(root/'blender/model_village_paving_24e.py').read_text(encoding='utf-8').replace('24e','24f')
(root/'blender/model_village_paving_24f.py').write_text(code,encoding='utf-8')
