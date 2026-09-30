"""Read native geometry and verify the keeper glazing follows its wall plane."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];label=sys.argv[sys.argv.index('--')+1]
folder=root/'captures'/('lantern_islands_study_'+label)
output=root/'reviews'/('round-'+label+'-coast-native-check.json');assert not output.exists()
rows=[]
for source in sorted(folder.glob('*.blend')):
    bpy.ops.wm.open_mainfile(filepath=str(source));issues=[];glazing=[];objects=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world);bm.normal_update()
        if any(not e.is_manifold for e in bm.edges):issues.append([obj.name,'nonmanifold edge'])
        if any(f.calc_area()<1e-9 for f in bm.faces):issues.append([obj.name,'zero area'])
        volume=bm.calc_volume(signed=True)
        if volume<=0:issues.append([obj.name,'nonpositive signed volume'])
        if 'window glazing' in obj.name:
            bounds=[min(v.co[i] for v in bm.verts) for i in range(3)],[max(v.co[i] for v in bm.verts) for i in range(3)]
            dims=[bounds[1][i]-bounds[0][i] for i in range(3)]
            thickness_axis=0 if (' east ' in obj.name or ' west ' in obj.name) else 1
            okay=dims[thickness_axis]<.06 and dims[1-thickness_axis]>1.0
            glazing.append({'name':obj.name,'dimensions_blender':dims,'wall_thickness_axis':thickness_axis,'passed':okay})
            if not okay:issues.append([obj.name,'glazing not in its wall plane'])
        objects.append({'name':obj.name,'vertices':len(bm.verts),'faces':len(bm.faces),'volume_m3':volume});bm.free()
    if source.stem=='keeper_house':assert len(glazing)==8
    rows.append({'asset':source.stem,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'passed':not issues,'parts':len(objects),'issues':issues,'glazing':glazing,'objects':objects})
result={'scope':'Independent read of saved Blender parts: closed positive-volume geometry, zero-area faces and keeper window pane orientation. Not visual or whole scene acceptance.','label':label,'passed':all(r['passed'] for r in rows),'assets':rows}
output.write_text(json.dumps(result,indent=2));print(json.dumps({'passed':result['passed'],'issues':{r['asset']:r['issues'] for r in rows}}),flush=True)
