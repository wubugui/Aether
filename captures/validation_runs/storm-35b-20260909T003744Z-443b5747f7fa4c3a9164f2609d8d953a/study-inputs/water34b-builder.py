from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];O=R/'captures/water_study_34b';assert not O.exists();O.mkdir()
source=R/'captures/water_study_34a/open_water.gdshader';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=source.read_text(encoding='utf-8')
for a,b in [('vec2(6.5,4.5)','vec2(5.5,2.8)'),('.95*(sea_noise(q*vec2(.028,.055)','2.4*(sea_noise(q*vec2(.045,.085)'),('.48*(sea_noise(q*vec2(.065,.12)','1.35*(sea_noise(q*vec2(.09,.20)'),('.09*(sea_noise(q*vec2(.14,.24)','.15*(sea_noise(q*vec2(.17,.45)')]:
 assert a in s,a;s=s.replace(a,b)
start=s.index('    // Finite pixel footprint');end=s.index('    float broken_wave=',start)
s=s[:start]+'''    // Reflect the actual finite330m lunar sphere at9000m, not a broad
    // soft point-light lobe. The pixel angular footprint anti-aliases its rim.
    vec3 reflected_ray=reflect(-view_direction,wave_normal);
    float separation=acos(clamp(dot(reflected_ray,normalize(moon_direction)),-1.,1.));
    float moon_radius=atan(330./9000.);
    float pixel_angle=max(.00015,.65*(length(dFdx(view_direction))+length(dFdy(view_direction))));
    float reflected=1.-smoothstep(moon_radius-pixel_angle,moon_radius+pixel_angle,separation);
'''+s[end:]
s=s.replace('float broken_wave=.38+.62*sea_noise','float broken_wave=.70+.30*sea_noise')
(O/'open_water.gdshader').write_text(s,encoding='utf-8');shutil.copy2(__file__,O/'builder.py')
(O/'design-plan.json').write_text(json.dumps(dict(label='34b',source=str(source.relative_to(R)),source_sha256=sha(source),shader_sha256=sha(O/'open_water.gdshader'),scope='34a rework:5.5x2.8m shared irregular facets with broader slope distribution and finite lunar disk reflection, smooth view-ray pixel footprint at disk edge. Actual sea geometry remains flat; no local lamp or cloud/scene reflection. Coast33f retained; actualGPU required.',production_modified=False,full_reference_accepted=False),indent=2),encoding='utf-8')
driver=(R/'tools/render_water_34a.py').read_text(encoding='utf-8').replace('34a','34b')
driver=driver.replace("prior=root/'captures/validation_runs/rightcoast-33f-20260908T233517Z-9aac3867c5f340208c238c9e2b83fc1e'", "prior=root/'captures/validation_runs/water-34a-20260908T233808Z-05bd651c68574ef79ba9b59ab98506bb'")
driver=driver.replace("shutil.copy2(prior/'actual-coast-rebuild.json',frozen/'inherited-33f-coast-runtime.json')", "require((frozen/'inherited-33f-coast-runtime.json').exists(),'Inherited33f runtime report missing')")
# This already-prepared preview has the same water views and inherited report;
# replacing its bounded view block is idempotent, no grading gate is rewritten.
driver=driver.replace('s=s.replace(\'\\t\\treport["lantern_lighting"]=lantern_report\'', 's=s.replace(\'\\t\\treport["lantern_lighting"]=lantern_report\'',1)
# Avoid duplicate identity assignment inherited from34a.
line='   s=s.replace(\'\\t\\treport["lantern_lighting"]=lantern_report\''
driver='\n'.join(l for l in driver.split('\n') if not l.startswith(line))
p=R/'tools/render_water_34b.py';assert not p.exists();p.write_text(driver,encoding='utf-8');print('34b shader and renderer prepared')
