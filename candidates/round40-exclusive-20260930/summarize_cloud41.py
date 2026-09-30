from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageDraw
import json,re,sys,zipfile,shutil

base=Path(__file__).resolve().parent; root=base.parents[1]; project=base/'project'
run_name=sys.argv[1]; run=base/'evidence'/run_name
report=json.loads((run/'report.json').read_text(encoding='utf8'))
for capture in report['captures']:assert sha256(Path(capture['image']).read_bytes()).hexdigest()==capture['sha256']
inputs=base/'evidence'/(run_name+'-inputs'); inputs.mkdir(exist_ok=True)
rows=[]
for rel in ['scripts/game40.gd','scripts/environment40.gd','scripts/airship_body.gd','assets/reference_views40.json','tools/build_round40.gd','tools/verify_cloud41.gd','tools/build_cloud41.gd','project.godot']:
    target=inputs/rel; target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists(): content=target.read_bytes()
    else:
        content=(project/rel).read_bytes();target.write_bytes(content)
    rows.append({'path':rel,'bytes':len(content),'sha256':sha256(content).hexdigest()})
asset_folder='hub-cabins40' if run_name=='gpu-a' else 'hub-cabins40-b'
for path in list((base/'source-assets'/asset_folder).iterdir())+list((base/'source-assets'/'hub-cloud41').iterdir()):
    if path.is_file(): rows.append({'path':str(path.relative_to(base)),'bytes':path.stat().st_size,'sha256':sha256(path.read_bytes()).hexdigest()})
issues=[line for line in (base/'evidence'/(run_name+'.stderr.log')).read_text(encoding='utf8',errors='replace').splitlines() if re.search('ERROR:|WARNING:',line)]
summary={'candidate_root':str(project),'baseline_sha256':'9a52fce69ad88c4545b0993a587a896b8ada1e8b7b5e2351273b76a028f8d151','scene_sha256':report['source_sha256'],
 'run':run_name,'checks_passed':sum(r['passed'] for r in report['checks']),'check_count':len(report['checks']),'failed_checks':[r for r in report['checks'] if not r['passed']],
 'raw_screenshots':len(report['captures']),'runtime_passed':report['passed'],'full_log_clean':not issues,'log_issues':issues,
 'visual_acceptance':'not_passed','goal_complete':False,'input_files':rows,
 'scope':'Same native world with 25 shared modeled cloud placements, actual side/back cloud views and retained cabin/player blocking checks. Limited shared true lighting, retained native cabin lining, four camera clearance checks, original player swept collision against two cabin solids (initial contact roof lining) and one floating island. Not complete accessibility/routes/weather/visual acceptance.'}
(base/'evidence'/(run_name+'-summary.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
sheet=Image.new('RGB',(1920,1969),'#141b26'); draw=ImageDraw.Draw(sheet)
draw.text((12,9),'REFERENCE | VERIFIED BASELINE 39-h | ROUND40 REAL GPU | VISUAL ACCEPTANCE PENDING',fill='white')
baseline=root/'captures/acceptance39/frozen-audit-f/gpu-h'
for i,(reference,actual) in enumerate([('1343','boot-day'),('1342','reference-1342'),('1274','reference-1274'),('1278','reference-1278'),('1216','reference-1216')]):
    y=34+i*387;draw.text((12,y+5),reference+' | '+run_name,fill='white')
    for col,path in enumerate([root/'ref'/f'{reference}.png',baseline/f'{actual}.png',run/f'{actual}.png']):
        im=Image.open(path).convert('RGB');im.thumbnail((640,360));sheet.paste(im,(col*640,y+27))
sheet.save(base/'evidence'/(run_name+'-comparison.png'))
with zipfile.ZipFile(base/'evidence'/(run_name+'-evidence.zip'),'w',zipfile.ZIP_DEFLATED) as archive:
    for path in run.rglob('*'):
        if path.is_file():archive.write(path,str(path.relative_to(base/'evidence')))
    for path in inputs.rglob('*'):
        if path.is_file():archive.write(path,str(path.relative_to(base/'evidence')))
    for name in [run_name+'-summary.json',run_name+'-comparison.png',run_name+'.stdout.log',run_name+'.stderr.log',run_name+'.log','hub-cabins40-b-task.json','hub-cabins40-b-result.json','hub-cloud41-task.json','hub-cloud41-result.json','independence-audit.json']:
        path=base/'evidence'/name
        if path.is_file():archive.write(path,name)
print(json.dumps({k:summary[k] for k in ['run','scene_sha256','checks_passed','check_count','runtime_passed','full_log_clean','failed_checks']}))
print('png bytes',(base/'evidence'/(run_name+'-comparison.png')).stat().st_size)
print('zip bytes',(base/'evidence'/(run_name+'-evidence.zip')).stat().st_size)
