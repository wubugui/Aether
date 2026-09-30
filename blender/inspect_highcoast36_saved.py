"""Read saved native tiles before local sculpting; never call terrain generation."""
from pathlib import Path
import bpy,json,hashlib,numpy as np
R=Path(__file__).resolve().parents[1];OUT=R/'captures/highcoast36-saved-inputs';assert not OUT.exists();OUT.mkdir()
rows=[]
for cz in [-6,-5,-4,-3]:
    for cx in [-5,-4,-3,-2]:
        name=f'Ground_{cx}_{cz}';p=R/'blender/terrain_modules'/(name+'.blend')
        bpy.ops.wm.open_mainfile(filepath=str(p))
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objects)==1
        obj=objects[0];mesh=obj.data
        coords=np.array([obj.matrix_world@v.co for v in mesh.vertices],dtype=np.float64)
        godot=np.c_[coords[:,0]+cx*768,coords[:,2],-coords[:,1]+cz*768]
        mesh.calc_loop_triangles();faces=np.array([list(t.vertices) for t in mesh.loop_triangles],dtype=np.int32)
        np.savez_compressed(OUT/(name+'.npz'),vertices_world=godot,triangles=faces)
        # Shoreline vertices nearest Y=0 locate the actual saved water boundary.
        shore=godot[np.abs(godot[:,1])<.05]
        stats=dict(name=name,source=str(p.relative_to(R)),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                   object_name=obj.name,object_transform=[list(r) for r in obj.matrix_world],vertices=len(godot),triangles=len(faces),
                   world_bounds=[godot.min(axis=0).tolist(),godot.max(axis=0).tolist()],
                   near_sea_vertices=len(shore),near_sea_bounds=None if not len(shore) else [shore.min(axis=0).tolist(),shore.max(axis=0).tolist()],
                   color_attributes=[dict(name=a.name,domain=a.domain,data_type=a.data_type) for a in mesh.color_attributes],
                   local_origin=[cx*768,0,cz*768])
        rows.append(stats)
        print(name,'verts',len(godot),'shore',len(shore),flush=True)
layout=json.loads((R/'assets/world_layout.json').read_text())
report=dict(scope='Saved16 Blender tiles read only. Four western neighbor tiles included to locate actual coastline beyond the preliminary12-tile box. No generated heights or mesh edits.',tiles=rows,layout_coast=layout.get('coast'),production_modified=False)
(R/'reviews/36-terrain-savedmesh-intake.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('36 SAVED INPUTS READY',len(rows),flush=True)
