from pathlib import Path
import json,hashlib,zipfile,shutil
from PIL import Image,ImageDraw
base=Path(__file__).resolve().parent;root=base.parents[1];evidence=base/'evidence';run=evidence/'gpu-g-weather42b-1733';project=base/'project'
report=json.loads((run/'report.json').read_text(encoding='utf8'))
inputs=evidence/'gpu-g-weather42b-1733-inputs';inputs.mkdir(exist_ok=True)
rows=[]
for rel in ['scripts/game42b.gd','scripts/environment42b.gd','scripts/weather42b.gd','scripts/airship_body.gd','assets/reference_views42.json','tools/build_weather42b.gd','tools/verify_weather42b.gd','project.godot']:
    target=inputs/rel;target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():shutil.copyfile(project/rel,target)
    rows.append({'path':rel,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
issues=[]
for suffix in ['.log','.stdout.log','.stderr.log']:
    issues += [line for line in (evidence/('gpu-g-weather42b-1733'+suffix)).read_text(encoding='utf8',errors='replace').splitlines() if 'ERROR:' in line or 'WARNING:' in line]
summary={'scene_sha256':report['source_sha256'],'checks_passed':sum(row['passed'] for row in report['checks']),'check_count':len(report['checks']),'raw_images':len(report['captures']),'all_20_reference_navigation':True,'full_log_clean':not issues,'log_issues':issues,'runtime_passed':report['passed'],'visual_acceptance':'not_passed','goal_complete':False,'inputs':rows,'failures':['Near rain appears as excessive coarse streaks; must fade near viewing eye and reduce native particle scale.','Snow1276 view occluded by real geometry; diagnose true ground and camera clearance.','Upper clouds retain heavy base and repeated arranged silhouettes.','Terrain, mountain silhouettes, islands, ports, fine interior props and reflection fidelity still require full reference work.']}
summary_path=evidence/'gpu-g-weather42b-summary.json';summary_path.write_text(json.dumps(summary,indent=2),encoding='utf8')
captures={row['name']:row for row in report['captures']}
ref_ids=[str(row['ref']) for row in json.loads((project/'assets/reference_views42.json').read_text(encoding='utf8'))]
sheet_paths=[]
for page in range(3):
    ids=ref_ids[page*7:(page+1)*7]
    if page==2:ids.append('original')
    sheet=Image.new('RGB',(1280,32+len(ids)*385),'#141b26');draw=ImageDraw.Draw(sheet)
    draw.text((8,8),'ORIGINAL REFERENCE | GAME42B REAL GPU | VISUAL ACCEPTANCE NOT PASSED',fill='white')
    for index,id in enumerate(ids):
        name='boot-controller-original' if id=='original' else 'reference-'+id
        y=32+index*385;draw.text((8,y+3),id+' | Game42b / 105 limited checks',fill='white')
        ref=root/'assets/reference.jpg' if id=='original' else root/'ref'/f'{id}.png'
        for column,path in enumerate([ref,Path(captures[name]['image'])]):
            image=Image.open(path).convert('RGB');image.thumbnail((640,360));sheet.paste(image,(column*640,y+24))
    path=evidence/f'gpu-g-weather42b-all-reference-page{page+1}.png';sheet.save(path);sheet_paths.append(path)
files=[run/'report.json',summary_path]+sheet_paths+[Path(row['image']) for row in report['captures']]
for row in report['captures']:assert hashlib.sha256(Path(row['image']).read_bytes()).hexdigest()==row['sha256']
archive_path=evidence/'gpu-g-weather42b-reports-and-screenshots.zip'
assert not archive_path.exists()
with zipfile.ZipFile(archive_path,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in files:archive.write(path,str(path.relative_to(evidence)))
    archive.writestr('contents-manifest.json',json.dumps({'scope':'Only PNG screenshots and acceptance JSON reports, no source/scripts/raw logs/credentials.','files':[{'path':str(p.relative_to(evidence)),'bytes':p.stat().st_size} for p in files]},indent=2))
print(json.dumps({'summary':summary,'deliverables':[{'path':str(p),'bytes':p.stat().st_size} for p in sheet_paths+[archive_path]]}))
