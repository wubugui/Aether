"""Broader irregular world-space water facets; no scene geometry or camera cards."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];O=R/'captures/water_study_34a';assert not O.exists();O.mkdir()
source=R/'captures/validation_runs/rightcoast-33d-20260908T232040Z-ea61879316ae487487e34e2f5d2c313b/study-inputs/new-environment27f/open_water.gdshader'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=source.read_text(encoding='utf-8')
assert sha(source)=='cb2528a352d1c17c966e9a5a48b8c96d54e2a87b73776277ed8f7add3987cdfa'
for a,b in [('vec2(3.2,1.1)','vec2(6.5,4.5)'),('offset*.32','offset*.45'),('.68*(sea_noise(q*vec2(.034,.11)','.95*(sea_noise(q*vec2(.028,.055)'),('.42*(sea_noise(q*vec2(.072,.32)','.48*(sea_noise(q*vec2(.065,.12)'),('.13*(sea_noise(q*vec2(.21,.86)','.09*(sea_noise(q*vec2(.14,.24)')]:
 assert a in s,a;s=s.replace(a,b)
s=s.replace('    float warp=sea_noise(q*vec2(.033,.08))*2.;\n','')
old='    float reflected=pow(max(dot(reflect(-view_direction,wave_normal),normalize(moon_direction)),0.),220.);'
new='''    // Finite pixel footprint broadens the specular lobe and conserves its
    // approximate integrated energy, avoiding subpixel distant bright combs.
    vec3 reflected_ray=reflect(-view_direction,wave_normal);
    vec3 ray_dx=dFdx(reflected_ray),ray_dy=dFdy(reflected_ray);
    float ray_variance=dot(ray_dx,ray_dx)+dot(ray_dy,ray_dy);
    float lobe_power=1./(1./180.+ray_variance*1.5);
    float reflected=pow(max(dot(reflected_ray,normalize(moon_direction)),0.),lobe_power)*(lobe_power/180.);'''
assert old in s;s=s.replace(old,new)
s=s.replace('float broken_wave=.72+.28*sea_noise(world_point.xz*vec2(.075,.18)+vec2(4.,world_time*.15));','float broken_wave=.38+.62*sea_noise(world_point.xz*vec2(.035,.055)+vec2(4.,world_time*.08));')
s=s.replace('vec3(.012,.035,.105),vec3(.027,.070,.19)','vec3(.016,.043,.125),vec3(.030,.080,.215)')
(O/'open_water.gdshader').write_text(s,encoding='utf-8');shutil.copy2(__file__,O/'builder.py')
(O/'design-plan.json').write_text(json.dumps(dict(label='34a',source=str(source.relative_to(R)),source_sha256=sha(source),shader_sha256=sha(O/'open_water.gdshader'),scope='Broader6.5x4.5m world-space irregular material facets and pixel-footprint specular filtering. Existing sea geometry remains flat. No local lamp/cloud geometry reflection yet. All coast/islands/clouds retained; reference fidelity awaits GPU.',production_modified=False,full_reference_accepted=False),indent=2),encoding='utf-8')
print('34a shader prepared')
