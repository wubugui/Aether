"""Repair resource reference syntax in new native scene copies only."""
from pathlib import Path
import re,json,hashlib,shutil
R=Path(__file__).resolve().parents[1]
prior=R/'captures/validation_runs/highcoast-36b-20260909T015215Z-0c71bb650bcf43d890987772791f1dff'
source=prior/'images/native-scenes'
out=R/'captures/candidate_highcoast36c'
assert not out.exists();out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(__file__,out/'repair.py')
script=out/'candidate_game_36c.gd'
shutil.copy2(prior/'study-inputs/highcoast36b/candidate_game_36b.gd',script)

def local(path):
    normal=re.sub('/+','/',path.replace('\\','/'))
    prefix=R.as_posix()+'/'
    assert normal.lower().startswith(prefix.lower()),normal
    relative=normal[len(prefix):]
    if relative.endswith('/World36b.tscn'):relative='captures/candidate_highcoast36c/World36c.tscn'
    if relative.endswith('/candidate_game_36b.gd'):relative='captures/candidate_highcoast36c/candidate_game_36c.gd'
    assert (R/relative).exists(),relative
    return 'res://'+relative

records=[]
for name in ['World','Game']:
    src=source/(name+'36b.tscn');dest=out/(name+'36c.tscn')
    old=src.read_text(encoding='utf-8');changes=[]
    def reference(m):
        previous=m.group(1);new=local(previous)
        changes.append(dict(kind='ext_resource',before=previous,after=new))
        return m.group(0).replace(previous,new)
    new=re.sub(r'^\[ext_resource [^\n]*path="(E:[^"]+)"[^\n]*$',reference,old,flags=re.M)
    def folder(m):
        previous=json.loads(m.group(1));fixed=local(previous)
        changes.append(dict(kind='weather_folder',before=previous,after=fixed))
        return 'candidate_weather_folder = '+json.dumps(fixed)
    new=re.sub(r'^candidate_weather_folder = (".*")$',folder,new,flags=re.M)
    assert len(changes)==(14 if name=='World' else 3),changes
    dest.write_text(new,encoding='utf-8')
    records.append(dict(source=str(src.relative_to(R)),source_sha256=sha(src),output=str(dest.relative_to(R)),sha256=sha(dest),changes=changes))
(out/'repair-report.json').write_text(json.dumps(dict(records=records,source_run_status='failed',scope='Only external resource references and weather folder normalized; native geometry/material/transform payload unchanged. Fresh-process Godot verification still required.'),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(output=str(out),changes=[len(r['changes']) for r in records])))
