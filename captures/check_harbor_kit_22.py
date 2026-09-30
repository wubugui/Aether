"""Reopen all native harbor sources; verify solids and physically thin lantern panes."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];label=sys.argv[sys.argv.index('--')+1]
folder=root/'captures'/('harbor_kit_study_'+label);output=root/'reviews'/('round-'+label+'-harbor-native-check.json');assert not output.exists()
rows=[]
for asset in json.loads((folder/'model-report.json').read_text(encoding='utf-8'))['assets']:
    source=folder/(asset['name']+'.blend');assert hashlib.sha256(source.read_bytes()).hexdigest()==asset['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source));parts=[];issues=[];panes=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world);bm.normal_update()
        volume=bm.calc_volume(signed=True)
        if any(not e.is_manifold for e in bm.edges):issues.append([obj.name,'nonmanifold edge'])
        if any(f.calc_area()<1e-9 for f in bm.faces):issues.append([obj.name,'zero area'])
        if volume<=0:issues.append([obj.name,'nonpositive volume'])
        low=[min(v.co[i] for v in bm.verts) for i in range(3)];high=[max(v.co[i] for v in bm.verts) for i in range(3)]
        if obj.name.startswith(('Lantern front rear glass','Lantern side glass')):
            dims=[high[i]-low[i] for i in range(3)];axis=1 if obj.name.startswith('Lantern front') else 0
            okay=dims[axis]<.02 and dims[1-axis]>.30 and dims[2]>.55
            if not okay:issues.append([obj.name,'pane orientation'])
            panes.append({'name':obj.name,'dimensions':dims,'passed':okay})
        parts.append({'name':obj.name,'verts':len(bm.verts),'faces':len(bm.faces),'volume_m3':volume,'bounds_blender':[low,high]});bm.free()
    if asset['name']=='harbor_lantern':assert len(panes)==4
    assert len(parts)==asset['parts']
    rows.append({'asset':asset['name'],'source_sha256':asset['source_sha256'],'glb_sha256':hashlib.sha256((folder/(asset['name']+'.glb')).read_bytes()).hexdigest(),'passed':not issues,'issues':issues,'panes':panes,'parts':parts})
report={'passed':all(r['passed'] for r in rows),'scope':'Reopened saved Blender solids, dimensions and lantern glazing planes. Does not prove visual matching, all intersections, placement or seabed anchoring.','assets':rows}
output.write_text(json.dumps(report,indent=2),encoding='utf-8');print('HARBOR NATIVE GATE '+str(report['passed']),flush=True)
