"""Correct27e's visibly oversized triangular wave facets using the fixed camera."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];out=R/'captures/coast_environment_study_27f'
assert not out.exists();shutil.copytree(R/'captures/coast_environment_study_27e',out)
p=(out/'open_water.gdshader').read_text(encoding='utf-8')
assert p.count('vec2(4.8,2.6)')==2
p=p.replace('vec2(4.8,2.6)','vec2(3.2,1.1)').replace('),140.);','),220.);')
p=p.replace('vec3(.88,1.12,1.65)*reflected','vec3(.98,1.28,2.05)*reflected')
p=p.replace('float broken_wave=.45+.55*sea_noise','float broken_wave=.72+.28*sea_noise')
(out/'open_water.gdshader').write_text(p,encoding='utf-8')
for source,target in [('captures/coast_environment_27e.gd','captures/coast_environment_27f.gd'),('tools/render_coast_environment_27e.py','tools/render_coast_environment_27f.py')]:
    p=(R/source).read_text(encoding='utf-8').replace('27e','27f')
    (R/target).write_text(p,encoding='utf-8')
shutil.copy2(__file__,out/'prepare-27f.py')
(out/'change-report-27f.json').write_text(json.dumps({'scope':'27e actual GPU showed oversized triangular plates.27f keeps the shared wave-height topology but decreases cells from4.8x2.6m to3.2x1.1m, narrows the moon lobe and lowers the additional random amplitude modulation. Same native27d clouds and world layout. Material wave-normal approximation only; no physical sea displacement or art acceptance claimed.','water_sha256':hashlib.sha256((out/'open_water.gdshader').read_bytes()).hexdigest(),'production_modified':False},indent=2),encoding='utf-8')
print('27f wave scale revision prepared')
