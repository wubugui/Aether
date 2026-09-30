"""Record the identity of the user-provided, unmodified scene references."""
from pathlib import Path
import hashlib,json
from PIL import Image
root=Path(__file__).resolve().parents[1]
target=root/'reviews/reference-catalog-20260908.json'
assert not target.exists()
names=['1125','1126','1128','1129','1131','1135','1216','1217','1218','1220',
       '1274','1275','1276','1278','1332','1341','1342','1343','1344','1347']
actual=sorted(p.stem for p in (root/'ref').glob('*.png'))
assert actual==names,actual
records=[]
for path in [root/'ref'/(name+'.png') for name in names]+[root/'assets/reference.jpg']:
    with Image.open(path) as img:width,height=img.size
    records.append({'path':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':width,'height':height,
        'visually_inspected':True,'scene_acceptance':'not_complete'})
target.write_text(json.dumps({'scope':'Scene-only expanded goal from 2026-09-08 user instruction; 20 new references plus original. Original image files unmodified.',
    'goal_document':'GOAL.md','scene_index':'REFERENCE_SCENES.md','references':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('REFERENCE CATALOG',len(records),'images',str(target))
