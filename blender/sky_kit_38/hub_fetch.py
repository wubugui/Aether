import sys, os, json, hashlib
sys.path.insert(0, r'C:/Users/weiruanrinima/.claude/skills/inference-hub-generation/scripts')
from hub_client import HubClient
here = os.path.dirname(os.path.abspath(__file__))
rec = json.load(open(os.path.join(here, sys.argv[1] if len(sys.argv) > 1 else 'hub_task.json')))
tid = rec['submit_response']['task_id']
c = HubClient(rec['base_url'], app_id='feiting', project_id='feiting-sky-kit-38')
job = c.wait(tid)
state = job.get('state')
print('state', state, 'exit', (job.get('result') or {}).get('exit_code'), 'error', job.get('error'))
out = os.path.join(here, sys.argv[2] if len(sys.argv) > 2 else 'hub_output'); os.makedirs(out, exist_ok=True)
if state == 'succeeded':
    for f in job['result']['files']:
        p = os.path.join(out, f['relative_path'])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        c.download(f['id'], p)
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        print('downloaded', f['relative_path'], f['size'], 'sha ok' if h == f['sha256'] else 'SHA MISMATCH')
    json.dump(job, open(os.path.join(out, 'hub_result.json'), 'w'), indent=1, default=str)
else:
    for ch in ('stdout', 'stderr'):
        try:
            r = c.call('GET', f'/v1/tasks/{tid}/logs/{ch}')
            print('----', ch); print(str(r)[-3000:])
        except Exception as e:
            print('log fetch failed', ch, e)
