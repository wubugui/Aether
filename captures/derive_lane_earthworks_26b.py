from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'tools/prepare_village_grading_25d.py').read_text().replace("label='25d'","label='26b'").replace('village_paving_design_24m','village_paving_design_26b')
p=p.replace('import shapely','import shapely\nimport numpy as np\nfrom shapely.ops import nearest_points',1)
p=p.replace("    original_collar=local(shapely.from_geojson(g['grading_footprint_geojson']))\n",'')
p=p.replace("    bands=[(row['height'],local(shapely.from_geojson(row['geojson']))) for row in g['grading_bands']]",'''    bands=[]
    for row in g['grading_surface_triangles']:
        pts=np.array(row['vertices_xz'])-np.array([origin[0],origin[2]])
        plane=np.linalg.solve(np.column_stack([pts,np.ones(3)]),row['heights'])
        bands.append((plane,Polygon(pts)))
    surface_tree=shapely.STRtree([poly for plane,poly in bands])''')
p=p.replace('groups.append((foot,collar,bands))','groups.append((foot,collar,bands,surface_tree))').replace('for foot,collar,bands in groups:','for foot,collar,bands,surface_tree in groups:')
p=p.replace('            ceiling=min(h-.06+.5*poly.distance(point) for h,poly in bands)-.5*distance', '''            nearest=int(surface_tree.nearest(point));plane,poly=bands[nearest]
            at=nearest_points(point,poly)[1]
            ceiling=float(np.array([at.x,at.y,1.])@plane)-.06''')
p=p.replace("'paving_candidate':'24m'","'paving_candidate':'26b'").replace("'prior_graded_headland':'24l'","'prior_graded_headland':'25f'")
(R/'tools/prepare_village_grading_26b.py').write_text(p,encoding='utf-8')
s=(R/'tools/solve_village_earthworks_25f.py').read_text().replace("label='25f'","label='26b'").replace('village_paving_design_24m','village_paving_design_26b')
s=s.replace("    for row in g['grading_bands']:\n        poly=shapely.transform(shapely.from_geojson(row['geojson']),lambda a:a-O[[0,2]])\n        bands.append((row['height'],poly))",'''    for row in g['grading_surface_triangles']:
        pts=np.array(row['vertices_xz'])-O[[0,2]]
        plane=np.linalg.solve(np.column_stack([pts,np.ones(3)]),row['heights'])
        bands.append((plane,Polygon(pts)))''')
s=s.replace("        y,b=bands[bi];inter=poly.intersection(b)","        cap_plane,b=bands[bi];inter=poly.intersection(b)")
s=s.replace("        for point in vertices(inter):\n            uv=", "        for point in vertices(inter):\n            y=float(np.array([point[0],point[1],1.])@cap_plane)\n            uv=")
(R/'tools/solve_village_earthworks_26b.py').write_text(s,encoding='utf-8')
(R/'blender/grade_village_earthworks_26b.py').write_text((R/'blender/grade_village_earthworks_25f.py').read_text(),encoding='utf-8')
