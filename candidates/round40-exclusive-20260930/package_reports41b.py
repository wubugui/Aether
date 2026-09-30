from pathlib import Path
import json,zipfile,hashlib
base=Path(__file__).resolve().parent/'evidence'
run=base/'gpu-f-cloud41b-1712'
report=json.loads((run/'report.json').read_text(encoding='utf8'))
files=[run/'report.json',base/'gpu-f-cloud41b-1712-summary.json',base/'gpu-f-cloud41b-1712-comparison.png']
for row in report['captures']:
    path=Path(row['image'])
    assert path.parent==run and path.suffix=='.png'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
    files.append(path)
manifest={'scope':'Only real GPU screenshots and acceptance reports authorized for Slack; no project source, scripts, raw logs or credentials.','scene_sha256':report['source_sha256'],'files':[{'path':str(p.relative_to(base)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
target=base/'gpu-f-cloud41b-reports-and-screenshots.zip'
assert not target.exists()
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in files: archive.write(path,str(path.relative_to(base)))
    archive.writestr('contents-manifest.json',json.dumps(manifest,indent=2))
print(json.dumps({'archive':str(target),'bytes':target.stat().st_size,'contents':[p.name for p in files]}))
