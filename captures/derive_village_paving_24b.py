from pathlib import Path
root=Path(__file__).resolve().parents[1]
prefix=(root/'blender/model_harbor_paths_22f.py').read_text(encoding='utf-8').split('# Appended to the standalone')[0].replace("'captures/harbor_paths_study_22f'","'captures/village_paving_study_24b'")
body='''
source=ROOT/'captures/village_paving_design_24b/paving.json'
design=json.loads(source.read_text(encoding='utf-8'));shutil.copy2(source,OUT/'paving-design.json')
shutil.copy2(ROOT/'tools/prepare_village_paving_24b.py',OUT/'prepare-design.py')
materials=[mat('Village buried rubble masonry',(.095,.087,.066))]
for i,color in enumerate([(.150,.139,.112),(.162,.149,.121),(.141,.133,.110),(.173,.158,.129)]):materials.append(mat('Village worn limestone '+str(i),color))
for group in design['groups']:
    reset();origin=group['origin']
    for item in group['solids']:
        points=item['vertices_xz'];n=len(points)
        vertices=[(x-origin[0],-(z-origin[2]),y) for y in [item['bottom_y'],item['top_y']] for x,z in points]
        faces=[tuple(reversed(t)) for t in item['cap_triangles']]+[tuple(i+n for i in t) for t in item['cap_triangles']]
        faces.extend((a,b,b+n,a+n) for a,b in item['boundary_edges'])
        obj=mesh(item['name'],vertices,faces,materials[item['material']]);obj['world_top_y']=item['top_y'];obj['paving_role']=item['kind'];obj['world_origin']=origin
    freeze('village_'+group['name'],'Connected real stone courtyard and contour stairs for village '+group['name']+'. Actual headland-derived shared level field, separate thick limestone pavers and buried closed bedding. All door interfaces, ground envelope, widths and fidelity remain to verify in native World.')
(OUT/'model-report.json').write_text(json.dumps({'label':'24b','assets':reports,'source_headland_sha256':design['headland_glb_sha256'],'source_grid_run':design['source_grid_run'],'production_modified':False},indent=2),encoding='utf-8')
print('VILLAGE PAVING BUILT '+str(sum(a['parts'] for a in reports))+' EDITABLE SOLIDS',flush=True)
'''
target=root/'blender/model_village_paving_24b.py';assert not target.exists();target.write_text(prefix+body,encoding='utf-8')
checker=(root/'captures/check_harbor_paths_22.py').read_text(encoding='utf-8').replace("'harbor_paths_study_'","'village_paving_study_'").replace("'-harbor-paths-native-check.json'","'-village-paving-native-check.json'")
(root/'captures/check_village_paving_24.py').write_text(checker,encoding='utf-8')
