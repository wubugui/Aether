from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'tools/prepare_village_grading_25b.py').read_text().replace("label='25b'","label='25d'")
p=p.replace("network=shapely.union_all(lines,grid_size=1e-5)","""# One-metre cells bound the extent of new facets without touching the coast.
for foot,collar,bands in groups:
    x0,z0,x1,z1=collar.bounds
    for x in range(math.floor(x0),math.ceil(x1)+1):
        line=LineString([(x,z0-1),(x,z1+1)]).intersection(collar)
        if not line.is_empty:lines.append(line)
    for z in range(math.floor(z0),math.ceil(z1)+1):
        line=LineString([(x0-1,z),(x1+1,z)]).intersection(collar)
        if not line.is_empty:lines.append(line)
network=shapely.union_all(lines,grid_size=1e-5)""")
(R/'tools/prepare_village_grading_25d.py').write_text(p,encoding='utf-8')
b=(R/'blender/grade_village_earthworks_25c.py').read_text()
b=b.replace("for (x,z),constraints in zip(design['vertices_xz_local'],design['grading_constraints']):","for vertex_index,((x,z),constraints) in enumerate(zip(design['vertices_xz_local'],design['grading_constraints'])):")
b=b.replace("    assert height>bottom_height+.5","    if 'resolved_heights' in design:\n        assert abs(old_height-design['original_actual_heights'][vertex_index])<.002,('Original GLB/native mismatch',vertex_index,old_height,design['original_actual_heights'][vertex_index])\n        height=design['resolved_heights'][vertex_index]\n    assert height>bottom_height+.5")
(R/'blender/grade_village_earthworks_25d.py').write_text(b,encoding='utf-8')
