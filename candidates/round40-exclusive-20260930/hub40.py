from pathlib import Path
import sys, json, zipfile, uuid, hashlib

base=Path(__file__).resolve().parent
sys.path.insert(0,str(base/'evidence'))
from hub_client import HubClient
c=HubClient('http://denghong01:8765',app_id='feiting',project_id='feiting-round40-exclusive')
suffix=('-'+sys.argv[2]) if len(sys.argv)>2 else ''
record_path=base/('evidence/hub-cabins40'+suffix+'-task.json')
mode=sys.argv[1]
if mode=='submit':
    assert not record_path.exists(), 'Use saved task ID, never duplicate submission'
    health=c.call('GET','/health'); versions=c.call('GET','/v1/blender/versions')
    guide=c.http.get('/guide.md');guide.raise_for_status()
    (base/('evidence/hub-guide'+suffix+'.md')).write_text(guide.text,encoding='utf8')
    capabilities=c.call('GET','/capabilities.json')
    (base/('evidence/hub-capabilities'+suffix+'.json')).write_text(json.dumps(capabilities),encoding='utf8')
    (base/'evidence/hub-health.json').write_text(json.dumps(health,indent=2),encoding='utf8')
    (base/'evidence/hub-versions.json').write_text(json.dumps(versions,indent=2),encoding='utf8')
    script=(base/'repair_cabins40.py').read_text(encoding='utf8')
    script=script.replace('import bpy, math, json','import bpy, math, json, os')
    script=script.replace("out=base/'project/assets/cabins40';out.mkdir(parents=True,exist_ok=True)","out=Path(os.environ['HUB_OUTPUT_DIR']);out.mkdir(parents=True,exist_ok=True)")
    script=script.replace("base/'source-assets/cabins40.blend'","out/'cabins40.blend'")
    script=script.replace("base/'evidence/blender-cabin-repair.json'","out/'blender-cabin-repair.json'")
    z=base/('evidence/cabins40-input'+suffix+'.zip')
    with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('main.py',script)
        archive.write(base/'source-assets/sky_kit_baseline.blend','source-assets/sky_kit_baseline.blend')
    upload=c.upload(z)
    key='feiting-round40-cabins-'+uuid.uuid4().hex
    body={'backend':'blender','name':'FeiTing40 retained cabins real wall/floor/window lining repair','priority':50,
          'params':{'version':'4.5.13','project_file':upload['id'],'script':'main.py','device':'cpu','threads':4,'ram_mb':4096,'timeout_seconds':600}}
    record={'base_url':'http://denghong01:8765','idempotency_key':key,'body':body,'upload':upload}
    record_path.write_text(json.dumps(record,indent=2),encoding='utf8')
    result=c.call('POST','/v1/tasks',json=body,headers={'Idempotency-Key':key})
    record['submit_response']=result
    record_path.write_text(json.dumps(record,indent=2),encoding='utf8')
    print(json.dumps(result))
else:
    record=json.loads(record_path.read_text(encoding='utf8'))
    task=record['submit_response']['task_id']
    if mode=='status':print(json.dumps(c.status(task)))
    elif mode=='fetch':
        result=c.call('GET','/v1/tasks/'+task)
        (base/('evidence/hub-cabins40'+suffix+'-result.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
        print('state',result['state'])
        if result['state']=='succeeded':
            for file in result['result']['files']:
                relative=Path(file['relative_path'])
                assert not relative.is_absolute() and '..' not in relative.parts
                output=base/('source-assets/hub-cabins40'+suffix)/relative
                output.parent.mkdir(parents=True,exist_ok=True)
                c.download(file['id'],output)
                assert hashlib.sha256(output.read_bytes()).hexdigest()==file['sha256']
                if output.suffix=='.glb':
                    target=base/'project/assets/cabins40'/output.name
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(output.read_bytes())
                print('SHA verified',relative,file['size'])
        elif result['state'] in ['failed','cancelled']:
            print(result.get('error'))
            for channel in ['stdout','stderr']:
                data,offset,eof=c.task_log(task,channel)
                (base/f'evidence/hub-cabins40-{channel}.log').write_bytes(data)
                print(channel,data.decode('utf8',errors='replace')[-4000:])
