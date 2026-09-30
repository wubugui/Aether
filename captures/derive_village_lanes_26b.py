from pathlib import Path
import shutil,json
R=Path(__file__).resolve().parents[1];src=R/'tools/prepare_village_paving_26a.py'
shutil.copy2(src,R/'captures/village_paving_design_26a/prepare-design.py')
(R/'captures/village_paving_design_26a/rejection.json').write_text(json.dumps({'phase':'preparation','failure':'Pinched lane boundary','solid':'foreground inclined limestone (-3191, -2832, 0)','native_or_gpu_started':False},indent=2))
p=src.read_text().replace('26a','26b')
p=p.replace("        poly=shapely.set_precision(poly,.001)","        poly=shapely.set_precision(poly,.00001)")
start=p.index('        for j in field_tree.query(poly):');end=p.index('        counts=defaultdict(int)',start)
p=p[:start]+'''        # Node the complete cap network once. Separate clipped triangle soups
        # can leave T-junctions after tiny intersections round differently.
        cap_lines=[poly.boundary]
        for j in field_tree.query(poly):
            line=field_polys[j].boundary.intersection(poly)
            if not line.is_empty:cap_lines.append(line)
        for cell in polygonize(shapely.union_all(cap_lines,grid_size=.00001)):
            if not poly.buffer(.00002).covers(cell.representative_point()):continue
            for tri in shapely.constrained_delaunay_triangles(cell).geoms:
                if tri.area<1e-12:continue
                ids=[vertex(p) for p in list(tri.exterior.coords)[:-1]]
                if len(set(ids))==3:faces.append(ids)
'''+p[end:]
(R/'tools/prepare_village_paving_26b.py').write_text(p,encoding='utf-8')
