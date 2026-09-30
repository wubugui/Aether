from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageDraw
import json, re, zipfile

root = Path(__file__).resolve().parents[1]
base = root/'captures/acceptance39/frozen-audit-f'
run = base/'gpu-h'
manifest = json.loads((base/'snapshot-manifest.json').read_text(encoding='utf8'))
report = json.loads((run/'report.json').read_text(encoding='utf8'))
for image in report['captures']:
    assert sha256(Path(image['image']).read_bytes()).hexdigest() == image['sha256']
assert sha256((base/'project/scenes/candidate39/Game39.tscn').read_bytes()).hexdigest() == report['source_sha256']
critical = [r for r in manifest['source_files'] if r['path'].endswith(('.gd','.gdshader','.tscn','.tres','.json','.godot'))]
changed = [r['path'] for r in critical if sha256((root/r['path']).read_bytes()).hexdigest()!=r['sha256']]
issues = [line for line in (base/'gpu-h.stderr.log').read_text(encoding='utf8',errors='replace').splitlines() if re.search(r'ERROR:|WARNING:',line)]
summary = {'functional_checks_passed':report['passed'], 'checks':len(report['checks']),
 'raw_screenshots':len(report['captures']), 'scene_sha256':report['source_sha256'],
 'single_world':len({c['world_instance'] for c in report['captures']})==1,
 'full_log_clean':not issues, 'log_issues':issues, 'shared_critical_sources_changed':changed,
 'visual_acceptance':'not_passed', 'goal_complete':False,
 'writer_identity':'unresolved; no evidence proving another user session',
 'limits':['Only five reference views plus limited side/back and 240-frame flight tested.',
 'Mesh/collision equality is not physical impact or accessibility validation.',
 'No complete inter-region flight route or all weather/reference acceptance.',
 'gpu-g is invalid due to incomplete snapshot; it is retained only as failed validation-process evidence.']}
(base/'summary-h.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
sheet=Image.new('RGB',(1280,1969),'#141b26')
draw=ImageDraw.Draw(sheet)
draw.text((12,9),'Original reference | Actual frozen native Game39 GPU-h | VISUAL ACCEPTANCE PENDING',fill='white')
for i,(reference,actual) in enumerate([('1343','boot-day'),('1342','reference-1342'),('1274','reference-1274'),('1278','reference-1278'),('1216','reference-1216')]):
    y=34+i*387
    draw.text((12,y+5),f'{reference} | native snapshot 9a52fce6...8d151',fill='white')
    for col,path in enumerate([root/'ref'/f'{reference}.png',run/f'{actual}.png']):
        im=Image.open(path).convert('RGB'); im.thumbnail((640,360)); sheet.paste(im,(col*640,y+27))
sheet.save(base/'comparison-h.png')
with zipfile.ZipFile(base/'slack-readonly39-h-evidence.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for path in base.iterdir():
        if path.is_file() and path.suffix!='.zip': archive.write(path,path.name)
    for directory in ['gpu-g','gpu-h']:
        for path in (base/directory).iterdir():
            if path.is_file(): archive.write(path,f'{directory}/{path.name}')
print(json.dumps(summary,ensure_ascii=False))
print('comparison bytes', (base/'comparison-h.png').stat().st_size)
print('zip bytes', (base/'slack-readonly39-h-evidence.zip').stat().st_size)
