from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];OUT=R/'captures/storm_study_35b';OLD=R/'captures/storm_study_35a'
assert not OUT.exists();OUT.mkdir()
for p in OLD.iterdir():
    if p.is_file() and p.name not in ['design-plan.json','builder.py','storm_front_35a.gd']:shutil.copy2(p,OUT/p.name)
shutil.copytree(R/'captures/storm_cloud_assets_35b',OUT/'cloud-assets')
shutil.copy2(__file__,OUT/'builder.py')
s=(OLD/'storm_front_35a.gd').read_text()
s=s.replace('35a','35b').replace('Vector3(.32,.14,-.94)','Vector3(.97,.11,-.20)')
s=s.replace('920.+35.*sin(row*1.5)','1160.+35.*sin(row*1.5)').replace('1040.,z-180.','1300.,z-180.').replace('685.,z-90.','930.,z-90.')
s=s.replace('"native_materials_adapted":converted.size()','"material_cache_entries":converted.size(),"legacy_cloud_meshes_adapted":legacy_cloud_count')
anchor='\tfor row in range(4):'
s=s.replace(anchor,'''\tvar legacy_cloud_count:int=0
\tvar legacy_clouds:Node3D=game.get_node("World/Clouds")
\tvar legacy_vapor:=ShaderMaterial.new();legacy_vapor.shader=shader_named("storm_cloud");register(legacy_vapor)
\tfor mesh in legacy_clouds.find_children("*","MeshInstance3D",true,false):
\t\tmesh.material_override=legacy_vapor;legacy_cloud_count+=1
'''+anchor)
(OUT/'storm_front_35b.gd').write_text(s,encoding='utf-8')
for p in OUT.glob('*.gdshader'):
    s=p.read_text().replace('vec3(.32,.14,-.94)','vec3(.97,.11,-.20)')
    if p.name=='storm_cloud.gdshader':
        s=s.replace('vec3(.021,.032,.047),vec3(.11,.14,.18)','vec3(.075,.10,.14),vec3(.24,.29,.36)')
        s=s.replace('vec3(.20,.16,.125),vec3(.76,.53,.28)','vec3(.25,.23,.205),vec3(.77,.61,.39)')
        s=s.replace('edge_light*.86','edge_light*.72')
    elif p.name=='open_water.gdshader':
        s=s.replace('float whitecaps=smoothstep(.032,.105,crest_level)*storm;', 'float whitecaps=smoothstep(.10,.23,crest_level)*storm*smoothstep(.48,.69,sea_noise(world_point.xz*.017+vec2(world_time*.08,3.)));')
    elif p.name=='storm_rain.gdshader':
        s=s.replace('VERTEX.y+=new_y-p.y;','VERTEX.y+=new_y-p.y;\n    VERTEX.x+=(top-new_y)*.16;')
        s=s.replace('vec3(.35,.43,.54)','vec3(.55,.62,.72)').replace('ALPHA=.30','ALPHA=.16')
    elif p.name=='storm_sky.gdshader':
        s=s.replace('vec3(.94,.59,.24),vec3(.23,.38,.54)','vec3(.86,.69,.43),vec3(.26,.39,.53)')
        s=s.replace('vec3(.52,.28,.05)*glow','vec3(.42,.26,.07)*glow')
        start=s.index('    float distance_to_layer=');end=s.index('    vec3 overcast=',start)
        s=s[:start]+'''    // Optical coverage integrates the finite world weather along the ray;
    // a clear far endpoint no longer leaks a uniform warm stripe underneath it.
    float optical=0.;
    for(int i=0;i<8;i++){
        float distance_along=(float(i)+.5)*900.;
        optical+=storm35_mask(storm_camera+ray*distance_along);
    }
    float cloud_coverage=1.-exp(-optical*.48);
'''+s[end:]
    p.write_text(s,encoding='utf-8')
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()}
(OUT/'design-plan.json').write_text(json.dumps(dict(label='35b',source_run='storm-35a-20260909T003123Z-b7154d45310e4e2482e9aff200346918',files_sha256=hashes,scope='New connected Blender canopy surfaces replace35a capsules. Cloud banks raised above observation routes, legacy world clouds weather-shaded, sky weather coverage integrated along world rays, native sun shifted to warm side, lower whitecap density and angled rain. Same land remains incomplete; no visual acceptance yet.',production_modified=False,full_reference_accepted=False),indent=2)+'\n',encoding='utf-8')
# Separate driver, preserving the complete failed35a source and real captures.
s=(R/'tools/render_storm_35a.py').read_text().replace('35a','35b')
s=s.replace("names=['storm-high','storm-coast-low','storm-inside','storm-edge','storm-clear','storm-flash','storm-cloud-back']", "names=['storm-high','storm-coast-low','storm-inside','storm-edge','storm-clear','storm-flash','storm-inside-flash','storm-cloud-back']")
s=s.replace('["storm-cloud-back",Vector3(-4600,1400,-2900),Vector3(-2750,950,-3600),70.,0.]', '["storm-inside-flash",Vector3(-3700,330,-2500),Vector3(-3300,160,-5100),70.,2.04],\n\\t\\t["storm-cloud-back",Vector3(-6900,2000,-3300),Vector3(-2750,1100,-3600),70.,0.]')
s=s.replace("(1 if name=='storm-flash' else 0)","(1 if name in ['storm-flash','storm-inside-flash'] else 0)")
s=s.replace("require(len(d['storm_setup']['assets'])==12", "require(d['storm_setup']['legacy_cloud_meshes_adapted']>0,'Legacy cloud binding missing')\n                require(len(d['storm_setup']['assets'])==12")
driver=R/'tools/render_storm_35b.py';assert not driver.exists();driver.write_text(s,encoding='utf-8')
print('35b storm native/shader preparation ready')
