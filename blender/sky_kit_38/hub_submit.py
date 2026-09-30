import sys, os, json, zipfile, uuid, time
sys.path.insert(0, r'C:/Users/weiruanrinima/.claude/skills/inference-hub-generation/scripts')
from hub_client import HubClient
here = os.path.dirname(os.path.abspath(__file__))
rec_path = os.path.join(here, sys.argv[1] if len(sys.argv) > 1 else 'hub_task.json')
if os.path.exists(rec_path):
    print('record exists, not resubmitting:', open(rec_path).read()); sys.exit(0)
z = os.path.join(here, 'sky_kit_38_project.zip')
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(os.path.join(here, 'main.py'), 'main.py')
c = HubClient('http://denghong01:8765', app_id='feiting', project_id='feiting-sky-kit-38')
up = c.upload(z)
fid = up['id'] if isinstance(up, dict) else up
key = 'feiting-sky-kit-38-' + uuid.uuid4().hex
body = {'backend': 'blender', 'name': 'feiting sky kit 38 (cabins, floating islands, cloud sea)', 'priority': 50,
        'params': {'version': '4.5.13', 'project_file': fid, 'script': 'main.py', 'device': 'cpu', 'threads': 4, 'ram_mb': 4096, 'timeout_seconds': 1800}}
rec = {'base_url': 'http://denghong01:8765', 'idempotency_key': key, 'body': body, 'upload': up}
open(rec_path, 'w').write(json.dumps(rec, indent=1))
res = c.call('POST', '/v1/tasks', json=body, headers={'Idempotency-Key': key})
rec['submit_response'] = res
open(rec_path, 'w').write(json.dumps(rec, indent=1, default=str))
print(json.dumps(res, indent=1, default=str)[:800])
