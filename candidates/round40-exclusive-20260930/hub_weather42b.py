from pathlib import Path
import sys,json,zipfile,uuid,hashlib
base=Path(__file__).resolve().parent
sys.path.insert(0,str(base/'evidence'))
from hub_client import HubClient
c=HubClient('http://denghong01:8765',app_id='feiting',project_id='feiting-round40-exclusive-clouds')
record_path=base/'evidence/hub-weather42b-task.json'
if sys.argv[1]=='submit':
    assert not record_path.exists()
    for endpoint,filename in [('/health','hub-cloud-health.json'),('/capabilities.json','hub-cloud-capabilities.json'),('/v1/blender/versions','hub-cloud-versions.json')]:
        (base/'evidence'/filename).write_text(json.dumps(c.call('GET',endpoint)),encoding='utf8')
    guide=c.http.get('/guide.md');guide.raise_for_status();(base/'evidence/hub-cloud-guide.md').write_text(guide.text,encoding='utf8')
    z=base/'evidence/weather42b-input.zip'
    with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as archive:archive.write(base/'model_weather42b.py','main.py')
    upload=c.upload(z);key='feiting-weather42b-'+uuid.uuid4().hex
    body={'backend':'blender','name':'FeiTing42b native spatial weather primitives','priority':50,'params':{'version':'4.5.13','project_file':upload['id'],'script':'main.py','device':'cpu','threads':4,'ram_mb':4096,'timeout_seconds':600}}
    record={'base_url':'http://denghong01:8765','idempotency_key':key,'body':body,'upload':upload}
    record_path.write_text(json.dumps(record,indent=2),encoding='utf8')
    record['submit_response']=c.call('POST','/v1/tasks',json=body,headers={'Idempotency-Key':key})
    record_path.write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record['submit_response']))
else:
    record=json.loads(record_path.read_text(encoding='utf8'));task=record['submit_response']['task_id']
    job=c.call('GET','/v1/tasks/'+task)
    (base/'evidence/hub-weather42b-result.json').write_text(json.dumps(job,indent=2),encoding='utf8')
    print('state',job['state'])
    if job['state']=='succeeded':
        for item in job['result']['files']:
            rel=Path(item['relative_path']);assert not rel.is_absolute() and '..' not in rel.parts
            target=base/'source-assets/hub-weather42b'/rel;target.parent.mkdir(parents=True,exist_ok=True);c.download(item['id'],target)
            assert hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']
            if target.suffix=='.glb':
                asset=base/'project/assets/weather42b'/target.name;asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(target.read_bytes())
            print('SHA verified',rel,item['size'])
    elif job['state']=='failed':
        print(job.get('error'))
        for channel in ['stdout','stderr']:
            data,_,_=c.task_log(task,channel);(base/f'evidence/hub-weather42b-{channel}.log').write_bytes(data);print(data.decode('utf8',errors='replace')[-3000:])
