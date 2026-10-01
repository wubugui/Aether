import bpy,json,numpy as np
from pathlib import Path
from mathutils import Matrix
D=Path(__file__).resolve().parent
geom=json.loads((D/'diagnostics-foot57b/prop-foot-geometry.json').read_text())
placements=json.loads((D/'scatter-replacements-seated.json').read_text())
S=np.array([[1,0,0],[0,0,-1],[0,1,0]],np.float32)
origin=np.array([-3840,0,-3840],np.float32)
meshes={}
for g in geom['groups']:
    assert len(g['surfaces'])==1
    s=g['surfaces'][0];v=np.array(s['vertices'],np.float32);idx=np.array(s['indices'],np.int32).reshape(-1,3)
    key=g['mesh']
    if key not in meshes:
        name=g['node'].split('/')[-1]+'_native_mesh'
        mesh=bpy.data.meshes.new(name);mesh.from_pydata((v@S.T).tolist(),[],idx[:,[0,2,1]].tolist());mesh.update()
        colors=np.array(s['colors'],np.float32)
        assert colors.shape==(len(v),4)
        col=mesh.color_attributes.new(name='NativeColor',type='FLOAT_COLOR',domain='POINT');col.data.foreach_set('color',colors.ravel())
        normals=np.array(s['normals'],np.float32)
        att=mesh.attributes.new('native_normal','FLOAT_VECTOR','POINT');att.data.foreach_set('vector',normals.ravel())
        mesh.normals_split_custom_set((normals@S.T)[idx[:,[0,2,1]].ravel()].tolist())
        mat=bpy.data.materials.new(s['material_name']+' [unaltered native prop colors]');mat.use_nodes=True
        color=mat.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name='NativeColor';bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.9;mat.node_tree.links.new(color.outputs['Color'],bs.inputs['Base Color']);mesh.materials.append(mat)
        mesh['native_mesh_resource']=key;meshes[key]=mesh
    meshes[g['node']]=meshes[key]
for phase,field in [('Original','before_buffer'),('Candidate','candidate_buffer')]:
    collection=bpy.data.collections.new('Coast57B_'+phase+'Props');bpy.context.scene.collection.children.link(collection)
    collection.hide_render=phase=='Original';collection.hide_viewport=phase=='Original'
    for r in placements:
        obj=bpy.data.objects.new(phase+'_'+r['node'].split('/')[-1]+'_'+str(r['index']),meshes[r['node']]);collection.objects.link(obj)
        buf=np.array(r[field],np.float32).reshape(3,4);m=np.eye(4,dtype=np.float32);m[:3,:3]=S@buf[:,:3]@S.T
        delta_origin=np.array(r['source_group_origin'],float)-origin.astype(float)
        local=(buf[:,3].astype(float)+delta_origin).astype(np.float32);m[:3,3]=S@local
        obj.matrix_world=Matrix(m.tolist())
        obj['source_node']=r['node'];obj['source_instance_index']=r['index'];obj['native_buffer']=r[field];obj['source_group_origin']=r['source_group_origin'];obj['phase']=phase
        obj['placement_evidence']='Exact continuous native foot-polygon/terrain-triangle overlay; candidate includes recorded seating and seven individually recorded bounded horizontal relocations'
print('EDITABLE57B_PROPS_CREATED',len(placements),'original + candidate; native mesh/colors retained')
