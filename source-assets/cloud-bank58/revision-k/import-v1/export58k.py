"""One explicitly scheduled export from the unchanged accepted source; never saves Blender."""
import argparse
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import contract58k as c

def main():
    import bpy
    import numpy as np
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);out=args.out.resolve()
    c.require(out.is_dir() and not any(out.iterdir()),'Fresh export output required')
    verified=c.source_preconditions()
    c.require(bpy.app.version==(4,5,14),'Pinned Blender 4.5.14')
    bpy.context.preferences.filepaths.use_scripts_auto_execute=False
    bpy.ops.wm.open_mainfile(filepath=str(c.SOURCE))
    core=c.load(c.K/'recovery-01/source_contact58k.py').recovery_core()
    bank=bpy.data.objects[c.BANK]
    identity=core.native_identity(bank)
    c.require(identity==verified['native_identity'] and identity['passed'],'Fresh full native identity equals accepted source')
    c.require(core.dependency_state()['strict_saved_source_dependencies_passed'],'No source image/library dependency')
    _,settings,_,reference=core.inputs();core.light_material_identity(bpy.context.scene,bank,settings)
    c.require(core.cameras(bpy.context.scene,bank,*core.inputs()[:2],reference)==verified['cameras'],'Original cameras/settings remain unchanged')
    vertices,faces=core.rebuild.geometry_arrays(bank)
    c.require(len(vertices)==194 and len(faces)==384 and c.geometry_fingerprint(vertices,faces)==identity['mesh'],'Actual source arrays')
    material=bank.data.materials[0];bsdf=material.node_tree.nodes['Principled BSDF']
    source=dict(passed=True,pid=os.getpid(),blender_version=list(bpy.app.version),source_sha256=c.SOURCE_SHA,
        source_saved=False,authored_vertex_count=194,triangles=faces.tolist(),positions=vertices.tolist(),
        polygon_normals=[list(p.normal) for p in bank.data.polygons],source_bounds=c.bounds(vertices),
        godot_relative_bounds=c.bounds(c.mapped(vertices)),matrix_world=[list(row) for row in bank.matrix_world],
        source_frame=c.strict_json_text(identity['source_frame']),
        material=dict(name=material.name,base_color_linear_rgba=list(bsdf.inputs['Base Color'].default_value),
                      roughness=float(bsdf.inputs['Roughness'].default_value),metallic=float(bsdf.inputs['Metallic'].default_value),
                      double_sided=not material.use_backface_culling),
        world_loaded=False,world_anchor_applied=False,visual_acceptance=False)
    # Selection is transient in this process only. Six semantic handles, cameras,
    # lights and embedded authoring text stay exclusively in the unchanged .blend.
    bpy.ops.object.select_all(action='DESELECT');bank.select_set(True);bpy.context.view_layer.objects.active=bank
    c.require([o.name for o in bpy.context.selected_objects]==[c.BANK],'Exactly one selected mesh')
    options=dict(filepath=str(out/'cloud58k.glb'),export_format='GLB',use_selection=True,
        export_yup=True,export_apply=False,export_normals=True,export_tangents=False,
        export_texcoords=False,export_vertex_color='NONE',export_all_vertex_colors=False,
        export_attributes=False,export_materials='EXPORT',export_animations=False,
        export_skins=False,export_morph=False,export_cameras=False,export_lights=False,
        export_extras=False,export_gpu_instances=False,export_unused_images=False,export_unused_textures=False)
    c.require(bpy.ops.export_scene.gltf(**options)=={'FINISHED'},'One selected-mesh GLB export')
    c.require(c.sha(c.SOURCE)==c.SOURCE_SHA and core.native_identity(bank)==identity,'Source and in-memory authored identity unchanged by exporter')
    document,raw,material=c.parse_glb(out/'cloud58k.glb')
    source['glb_geometry']=c.validate_geometry(raw,source)
    source['glb_material']=c.validate_material(material,source)
    source['glb_sha256']=c.sha(out/'cloud58k.glb');source['glb_bytes']=(out/'cloud58k.glb').stat().st_size
    source['export_options']=options
    c.write(out/'source-readback.json',source)

if __name__=='__main__':main()
