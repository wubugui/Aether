import sys, os, json, zipfile, uuid, hashlib
sys.path.insert(0, r'C:/Users/weiruanrinima/.claude/skills/inference-hub-generation/scripts')
from hub_client import HubClient
here = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1]; refs = sys.argv[2:]
rec_path = os.path.join(here, f'hub_task_{tag}.json'); out = os.path.join(here, f'out_{tag}')
c = HubClient('http://denghong01:8765', app_id='feiting', project_id='feiting-lookdev-38')
if not os.path.exists(rec_path):
    z = os.path.join(here, f'project_{tag}.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(os.path.join(here, 'main.py'), 'main.py')
        for g in [x for x in os.listdir(here) if x.endswith('.glb')]: zf.write(os.path.join(here, g), g)
    up = c.upload(z); fid = up['id'] if isinstance(up, dict) else up
    key = f'feiting-lookdev-38-{tag}-' + uuid.uuid4().hex
    body = {'backend': 'blender', 'name': f'feiting lookdev 38 {tag}', 'priority': 50,
            'params': {'version': '4.5.13', 'project_file': fid, 'script': 'main.py', 'args': refs, 'device': 'gpu', 'gpu_policy': 'auto',
                       'threads': 4, 'ram_mb': 8192, 'vram_mb': 3000, 'timeout_seconds': 1800}}
    rec = {'base_url': 'http://denghong01:8765', 'idempotency_key': key, 'body': body}
    open(rec_path, 'w').write(json.dumps(rec, indent=1))
    rec['submit_response'] = c.call('POST', '/v1/tasks', json=body, headers={'Idempotency-Key': key})
    open(rec_path, 'w').write(json.dumps(rec, indent=1, default=str))
rec = json.load(open(rec_path)); tid = rec['submit_response']['task_id']
print('task', tid, flush=True)
job = c.wait(tid)
print('state', job.get('state'), 'exit', (job.get('result') or {}).get('exit_code'), 'error', job.get('error'), flush=True)
os.makedirs(out, exist_ok=True)
for f in (job.get('result') or {}).get('files', []):
    p = os.path.join(out, f['relative_path']); os.makedirs(os.path.dirname(p), exist_ok=True)
    c.download(f['id'], p)
    ok = hashlib.sha256(open(p, 'rb').read()).hexdigest() == f['sha256']
    print('downloaded', f['relative_path'], f['size'], 'sha ok' if ok else 'SHA MISMATCH', flush=True)
json.dump(job, open(os.path.join(out, 'hub_result.json'), 'w'), indent=1, default=str)
for ch in ('stdout', 'stderr'):
    try:
        r = c.call('GET', f'/v1/tasks/{tid}/logs/{ch}')
        txt = r if isinstance(r, str) else json.dumps(r, default=str)
        open(os.path.join(out, f'{ch}.log'), 'w', encoding='utf-8').write(txt)
    except Exception as e:
        print('log fetch failed', ch, e)
