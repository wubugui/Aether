"""Connected sculpted canopy fields replace the rejected 35a capsule chain."""
import bpy,bmesh,math,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'captures/storm_cloud_assets_35b'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
records=[]
def reset():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def canopy(name,center,width,length,roof,belly,phase,nx,nz):
    verts=[]
    # Shared upper/lower grids make a single continuous bank. Broad designed
    # billows modulate the roof and underside, and change the eastern edge.
    for layer in [0,1]:
        for j in range(nz):
            v=-1+2*j/(nz-1)
            edge_wave=65*math.sin(v*6.1+phase)+30*math.sin(v*12.7+phase*.7)
            envelope=.22+.78*math.sin(math.pi*j/(nz-1))**.45
            for i in range(nx):
                u=-1+2*i/(nx-1)
                x=center[0]+u*width*.5+edge_wave*(.40+.60*(u+1)*.5)
                z=center[2]+v*length*.5+20*math.sin(u*5.2+phase)*math.sin(math.pi*j/(nz-1))
                section=max(0.,math.sin(math.pi*i/(nx-1)))**.55
                roof_shape=.80+.13*math.sin(v*5.4+phase)+.13*math.cos(u*4.2-v*3.5)
                bottom_shape=.74+.18*math.sin(v*7.6+phase)+.13*math.cos(u*5.5+v*4.1)
                middle=center[1]+35*math.sin(v*4.5+phase)+22*math.sin(u*3.1-v*5.7)
                y=middle+(18+roof*section*envelope*roof_shape if layer==0 else -18-belly*section*envelope*bottom_shape)
                verts.append((x,-z,y))
    n=nx*nz;faces=[]
    for layer in [0,1]:
        for j in range(nz-1):
            for i in range(nx-1):
                a=layer*n+j*nx+i;b=a+1;c=a+nx+1;d=a+nx
                pair=[(a,b,c),(a,c,d)] if (i+j)%2 else [(a,b,d),(b,c,d)]
                faces.extend(pair if layer==0 else [tuple(reversed(t)) for t in pair])
    boundary=list(range(nx))+[j*nx+nx-1 for j in range(1,nz)]+[(nz-1)*nx+i for i in range(nx-2,-1,-1)]+[j*nx for j in range(nz-2,0,-1)]
    for k,a in enumerate(boundary):
        b=boundary[(k+1)%len(boundary)];faces.extend([(a,a+n,b+n),(a,b+n,b)])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    mat=bpy.data.materials.new('Layered storm vapor');mat.diffuse_color=(.28,.33,.40,1);mesh.materials.append(mat)
    obj['construction']='Connected shared-grid upper roof, billowing underside, closed perimeter; coherent shaped edge'
def save(name):
    rows=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        assert all(e.is_manifold for e in bm.edges)
        assert min(f.calc_area() for f in bm.faces)>1e-4
        assert bm.calc_volume(signed=True)>0
        bm.to_mesh(o.data);rows.append(dict(name=o.name,vertices=len(bm.verts),faces=len(bm.faces),volume_m3=bm.calc_volume(signed=True)));bm.free()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',export_yup=True,export_animations=False)
    records.append(dict(asset=name,parts=rows,blend_sha256=hashlib.sha256((OUT/(name+'.blend')).read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((OUT/(name+'.glb')).read_bytes()).hexdigest()))
reset()
canopy('Connected broad front shelf',(-260,60,0),880,2460,245,105,.4,13,31)
canopy('Lower corrugated eastern cloud lip',(75,-80,90),310,2190,75,100,1.6,9,29)
save('storm_front_shelf')
reset()
canopy('Rear elevated anvil sheet',(-1000,180,0),2350,2690,470,180,.3,23,33)
canopy('Upper interlocking cloud ridge',(-1600,410,320),1450,2490,310,130,2.4,17,29)
save('storm_rear_anvil')
reset()
canopy('Hanging fragmented rain underside',(-130,-20,0),450,2150,95,160,2.6,11,29)
canopy('Outer rain fold',(30,-70,210),250,1250,75,125,4.1,9,23)
save('storm_rain_scud')
(OUT/'model-report.json').write_text(json.dumps(dict(scope='35b replaces35a rounded detached capsules with six editable continuous canopy fields across three assets. New model geometry, not a material-only fix; opaque cloud-interior transport still not modeled. Visual acceptance pending.',assets=records,production_modified=False,visual_accepted=False),indent=2)+'\n',encoding='utf-8')
print('35b CONNECTED CLOUD ASSETS READY',len(records),flush=True)
