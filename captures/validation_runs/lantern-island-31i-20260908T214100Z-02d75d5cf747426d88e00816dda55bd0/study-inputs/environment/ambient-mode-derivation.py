"""Select actual color ambient source explicitly and report effective lighting state."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
folder=root/'captures/coast_environment_study_21c';assert not folder.exists()
shutil.copytree(root/'captures/coast_environment_study_21b',folder);shutil.copy2(__file__,folder/'ambient-mode-derivation.py')
p=root/'captures/coast_environment_21c.gd';assert not p.exists();s=(root/'captures/coast_environment_21b.gd').read_text()
s=s.replace('var bindings:Array=[]','var bindings:Array=[]\nvar unmapped_shaders:Array=[]\nvar light_records:Array=[]')
anchor='\telif source is StandardMaterial3D and night:'
s=s.replace(anchor,'''\t\telif not shader_cache.values().has(source.shader) and not unmapped_shaders.has(source.shader.resource_path):
\t\t\tunmapped_shaders.append(source.shader.resource_path)
'''+anchor)
s=s.replace('\t\tenvironment.ambient_light_color=Color(.36,.46,.70);','\t\tenvironment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR\n\t\tenvironment.ambient_light_color=Color(.36,.46,.70);')
s=s.replace('\t\t\ttower.add_child(lamp)','\t\t\ttower.add_child(lamp)\n\t\t\tlight_records.append({"node":str(lamp.get_path()),"position":[lamp.global_position.x,lamp.global_position.y,lamp.global_position.z],"energy":lamp.light_energy,"range_m":lamp.omni_range})')
s=s.replace('"native_sky_assets":asset_records,','"unmapped_shader_paths":unmapped_shaders,"local_light_records":light_records,"ambient_source":environment.ambient_light_source,"ambient_color":[environment.ambient_light_color.r,environment.ambient_light_color.g,environment.ambient_light_color.b],"native_sky_assets":asset_records,')
p.write_text(s)
p=root/'tools/render_coast_environment_21c.py';assert not p.exists();s=(root/'tools/render_coast_environment_21b.py').read_text().replace('21b','21c')
s=s.replace('coastal_sky_assets_21c','coastal_sky_assets_21b').replace('round-21c-sky-native-check','round-21b-sky-native-check')
s=s.replace("[('day-reference','reference-coast-near','day'),('night-reference'","[('night-reference'")
s=s.replace("root/'captures/coast_environment_21c.gd',","root/'captures/coast_environment_21c.gd',root/'captures/environment-sources-runtime.log',root/'captures/inspect_environment_sources.gd',")
s=s.replace("preview=preview.replace(anchor,insertion+anchor).replace(","preview=preview.replace('Actual temporary 3D geometry in existing world daytime; not night/fog/whole reference acceptance.','Actual temporary 3D geometry in existing world; lighting mode recorded in environment_study, no full reference acceptance.')\n            preview=preview.replace(anchor,insertion+anchor).replace(")
s=s.replace("require(len(env['native_sky_assets'])==(8 if mode=='night' else 7),'Native sky geometry missing')","require(len(env['native_sky_assets'])==(8 if mode=='night' else 7),'Native sky geometry missing')\n                require(env['ambient_source']==2 and len(env['local_light_records'])==4,'Color ambient or lamp records missing')")
s=s.replace('Native Blender lunar sphere/cloud banks, brighter actual night fill and crossed wave reflection. Day reference, night reference and reverse night views.','Explicit runtime AMBIENT_SOURCE_COLOR correction, effective ambient source/color and local lamp records. Retains all21b shaders, clouds and moon geometry. Two affected night reference/reverse GPU views.')
p.write_text(s);print(folder,p)
