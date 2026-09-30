from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];OLD=R/'captures/storm_study_35b';OUT=R/'captures/storm_study_35c'
assert not OUT.exists();shutil.copytree(OLD,OUT)
shutil.copy2(__file__,OUT/'builder.py')
# Keep the six-part35b native geometry unchanged; this revision fixes runtime
# rain wrapping and retains replaced resources across queued rendering updates.
s=(OLD/'storm_front_35b.gd').read_text().replace('35b','35c')
s=s.replace('var converted:Dictionary={}','var converted:Dictionary={}\nvar retained_original_materials:Array[Material]=[]')
s=s.replace('\tif m==null:return null','\tif m==null:return null\n\tif not retained_original_materials.has(m):retained_original_materials.append(m)')
s=s.replace('\t\tmesh.material_override=legacy_vapor;legacy_cloud_count+=1','\t\tif mesh.material_override!=null and not retained_original_materials.has(mesh.material_override):retained_original_materials.append(mesh.material_override)\n\t\tfor surface in range(mesh.mesh.get_surface_count()):\n\t\t\tvar original:Material=mesh.get_active_material(surface)\n\t\t\tif original!=null and not retained_original_materials.has(original):retained_original_materials.append(original)\n\t\tmesh.material_override=legacy_vapor;legacy_cloud_count+=1')
s=s.replace('\tcreate_lightning()','\tcreate_lightning()\n\tgame.set_meta("storm35_retained_materials",retained_original_materials)\n\tgame.set_meta("storm35_live_materials",materials)\n\tgame.set_meta("storm35_shader_cache",shader_cache)')
s=s.replace('"material_cache_entries":converted.size(),','"material_cache_entries":converted.size(),"retained_original_materials":retained_original_materials.size(),')
(OUT/'storm_front_35c.gd').write_text(s,encoding='utf-8')
for p in list(OUT.glob('*.gdshader'))+list(OUT.glob('*.gdshaderinc')):
    s=p.read_text().replace('vec3(-3450.-float(i)*440.,420.,','vec3(-3450.-float(i)*440.,230.,')
    if p.name=='storm_rain.gdshader':
        s=s.replace('vec3 p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;', '// One shared translation per actual MultiMesh instance keeps all eight\n    // vertices together across the900m reset boundary.\n    vec3 p=MODEL_MATRIX[3].xyz;')
    p.write_text(s,encoding='utf-8')
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='design-plan.json'}
(OUT/'design-plan.json').write_text(json.dumps(dict(label='35c',source_run='storm-35b-20260909T003744Z-443b5747f7fa4c3a9164f2609d8d953a',files_sha256=hashes,scope='Same35b six-part Blender clouds. Rain reset is per-instance, preserving ribbon dimensions; flash falloff centers now share nativeOmni Y230. Retain original and live material references on scene across renderer updates; previous GLES null-material root cause not yet isolated. All35b failed images/logs preserved. Full reference remains unaccepted.',production_modified=False,full_reference_accepted=False),indent=2)+'\n',encoding='utf-8')
s=(R/'tools/render_storm_35b.py').read_text().replace('35b','35c')
driver=R/'tools/render_storm_35c.py';assert not driver.exists();driver.write_text(s,encoding='utf-8')
print('35c runtime repair prepared;35b native clouds retained')
