"""Python client: uploads are streamed in 4 MB chunks, outputs are streamed to disk."""
import argparse
import hashlib
import json
import os
import socket
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import httpx


def _responsive_ipv4(url):
    """Resolve a LAN hostname afresh; skip unreachable IPv6/virtual adapters."""
    parsed=urlsplit(url)
    if parsed.scheme != 'http' or not parsed.hostname or parsed.hostname == 'localhost':
        return url,None
    try:
        socket.inet_pton(socket.AF_INET,parsed.hostname)
        return url,None
    except OSError:
        pass
    try:
        addresses=list(dict.fromkeys(item[4][0] for item in socket.getaddrinfo(
            parsed.hostname,parsed.port or 80,family=socket.AF_INET,type=socket.SOCK_STREAM)))
    except OSError:
        return url,None
    if not addresses:
        return url,None
    port=parsed.port or 80
    def probe(ip):
        target=urlunsplit((parsed.scheme,f'{ip}:{port}',parsed.path,parsed.query,parsed.fragment))
        try:
            with httpx.Client(base_url=target,headers={'Host':parsed.netloc},
                              timeout=1,trust_env=False) as probe_client:
                response=probe_client.get('/health/live')
                body=response.json() if response.status_code == 200 else None
                if isinstance(body,dict) and body.get('service') == 'inference-hub':
                    return target
        except (httpx.HTTPError, ValueError):
            pass
        return None
    with ThreadPoolExecutor(max_workers=min(len(addresses),8)) as pool:
        for future in as_completed([pool.submit(probe,ip) for ip in addresses]):
            target=future.result()
            if target:
                return target,parsed.netloc
    return url,None


class HubClient:
    def __init__(self, url, key=None, *, app_id=None, project_id=None, actor_id=None):
        headers={"Authorization":"Bearer "+key} if key else {}
        for name,value in [('App',app_id),('Project',project_id),('Actor',actor_id)]:
            if value:headers['X-Hub-'+name+'-ID']=value
        self.original_url=url
        self.base_headers=headers
        self._connect()

    def _connect(self):
        resolved,host=_responsive_ipv4(self.original_url)
        headers=self.base_headers | ({'Host':host} if host else {})
        previous=getattr(self,'http',None)
        self.http=httpx.Client(base_url=resolved,headers=headers,timeout=120,trust_env=False)
        if previous:previous.close()

    def call(self, method, path, **kwargs):
        safe = method in ("GET", "HEAD") or "Idempotency-Key" in kwargs.get("headers", {})
        for attempt in range(3):
            try:
                r=self.http.request(method,path,**kwargs)
                r.raise_for_status()
                return r.json()
            except httpx.TransportError:
                if not safe or attempt == 2:
                    raise
                self._connect()
                time.sleep(attempt+1)

    def pause_batch(self, batch_id, reason, ttl_seconds=86400, on_expiry="notify"):
        return self.call("POST", "/v1/batches/"+batch_id+"/pause",
                         json={"reason":reason,"ttl_seconds":ttl_seconds,"on_expiry":on_expiry})

    def renew_batch_pause(self, batch_id, reason, expected_version, ttl_seconds=86400, on_expiry="notify"):
        return self.call("POST", "/v1/batches/"+batch_id+"/pause/renew",json={
            "reason":reason,"ttl_seconds":ttl_seconds,"on_expiry":on_expiry,"expected_version":expected_version})

    def resume_batch(self, batch_id):
        return self.call("POST", "/v1/batches/"+batch_id+"/resume")

    def cancel_paused(self, batch_id):
        return self.call("POST", "/v1/batches/"+batch_id+"/pause/cancel")

    def upload(self, path, resume_id=None):
        path=Path(path)
        if resume_id:
            status=self.call("GET","/v1/uploads/"+resume_id)
            if status.get("completed"):
                return status["file"]
            fid,offset=resume_id,status["offset"]
        else:
            sha=hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda:stream.read(4*2**20),b''):
                    sha.update(chunk)
            r=self.call("POST","/v1/uploads",json={"filename":path.name,"size":path.stat().st_size,"sha256":sha.hexdigest()})
            fid,offset=r["upload_id"],0
        print("upload_id:",fid,"(save this ID to resume)",flush=True)
        with path.open('rb') as stream:
            stream.seek(offset)
            for chunk in iter(lambda:stream.read(4*2**20),b''):
                response=self.call("PUT","/v1/uploads/"+fid,content=chunk,headers={"Upload-Offset":str(offset),"Content-Type":"application/octet-stream"})
                offset=response["offset"]
        return self.call("POST","/v1/uploads/"+fid+"/complete")

    def submit(self, jobs, name="", idempotency_key=None, scheduling="normal"):
        return self.call("POST","/v1/batches",json={"name":name,"jobs":jobs,"scheduling":scheduling},headers={"Idempotency-Key":idempotency_key or str(uuid.uuid4())})

    def wait(self, task_id):
        while True:
            job=self.call("GET","/v1/tasks/"+task_id+"/wait?timeout=25")
            if job["state"] in ("succeeded","failed","cancelled"):
                return job
            if job["state"] == "needs_review":
                time.sleep(1)

    def status(self, task_id):
        """Small task and scheduling snapshot; omits large params and result files."""
        return self.call("GET", "/v1/tasks/"+task_id+"/status")

    def queue(self, limit=50, offset=0):
        return self.call("GET", "/v1/queue", params={"limit":limit,"offset":offset})

    def watch(self, task_id, interval=5):
        """Yield a fresh status periodically, then the final complete task."""
        if interval <= 0:
            raise ValueError('interval must be positive')
        while True:
            status=self.status(task_id)
            yield status
            if status['state'] in ('succeeded','failed','cancelled'):
                return
            time.sleep(interval)

    def task_log(self,task_id,channel='stdout',offset=0,limit=65536):
        """Return raw bytes, next offset, EOF; keep independent offsets per channel."""
        if channel not in ('stdout','stderr'):raise ValueError('invalid channel')
        response=self.http.get('/v1/tasks/'+task_id+'/logs/'+channel,params={'offset':offset,'limit':limit})
        response.raise_for_status()
        return response.content,int(response.headers['X-Next-Offset']),response.headers['X-Log-EOF']=='true'

    def download(self, file_id, path):
        path=Path(path)
        partial=path.with_suffix(path.suffix+'.part')
        info=self.call("GET","/v1/files/"+file_id)
        offset=partial.stat().st_size if partial.exists() else 0
        if offset > info["size"]:
            raise ValueError("partial file is larger than the expected result")
        if offset < info["size"]:
            with self.http.stream("GET",info["url"],headers={"Range":f"bytes={offset}-"} if offset else {}) as r:
                r.raise_for_status()
                mode='ab' if r.status_code==206 and offset else 'wb'
                with partial.open(mode) as stream:
                    for chunk in r.iter_bytes(1024*1024):stream.write(chunk)
        sha=hashlib.sha256()
        with partial.open('rb') as stream:
            for chunk in iter(lambda:stream.read(4*2**20),b''):sha.update(chunk)
        if sha.hexdigest()!=info['sha256']:
            raise ValueError("download checksum mismatch")
        partial.replace(path)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--url',default=os.environ.get('HUB_URL') or 'http://127.0.0.1:8765',
                   help='Hub base URL; overrides HUB_URL. Remote clients must use the address in /guide.md.')
    p.add_argument('--key-file',help='Optional Bearer key file; omit for local/LAN password-free access')
    p.add_argument('--upload')
    p.add_argument('--resume-id')
    p.add_argument('--batch',help='JSON file containing name, jobs, and optional scheduling (normal/idle)')
    p.add_argument('--status',metavar='TASK_ID',help='Show a compact task and scheduling snapshot')
    p.add_argument('--queue',action='store_true',help='Show current dispatch and queue snapshot')
    p.add_argument('--watch',metavar='TASK_ID',help='Print task and queue progress every five seconds until terminal')
    p.add_argument('--idempotency-key',help='Reuse this value when retrying the same submission')
    p.add_argument('--app-id',help='Stable ASCII application identifier for usage attribution')
    p.add_argument('--project-id',help='Stable ASCII project identifier')
    p.add_argument('--actor-id',help='Optional ASCII caller identifier (self-reported, not authentication)')
    a=p.parse_args();client=HubClient(a.url,Path(a.key_file).read_text().strip() if a.key_file else None,
                                    app_id=a.app_id,project_id=a.project_id,actor_id=a.actor_id)
    if a.upload:print(json.dumps(client.upload(a.upload,a.resume_id),ensure_ascii=False,indent=2))
    if a.batch:
        batch=json.loads(Path(a.batch).read_text(encoding='utf-8'))
        print(json.dumps(client.submit(batch['jobs'],batch.get('name',''),a.idempotency_key,batch.get('scheduling','normal')),ensure_ascii=False,indent=2))
    if a.status:
        print(json.dumps(client.status(a.status),ensure_ascii=False,indent=2))
    if a.queue:
        print(json.dumps(client.queue(),ensure_ascii=False,indent=2))
    if a.watch:
        try:
            for status in client.watch(a.watch):
                queue=status['queue']
                print(json.dumps({'at':time.strftime('%Y-%m-%d %H:%M:%S'),
                    'task_id':status['task_id'],'state':status['state'],'phase':status['phase'],
                    'lane':queue['lane'],'lane_state':queue['lane_state'],
                    'queued_total':queue['queued_total'],'active_task_ids':[j['id'] for j in queue['active']],
                    'candidate_now':queue['candidate_now'],'reason':queue['reason'],
                    'last_progress':status['last_progress'],'runner_heartbeat':status['runner_heartbeat'],
                    'error':status['error']},ensure_ascii=False),flush=True)
            print(json.dumps(client.call('GET','/v1/tasks/'+a.watch),ensure_ascii=False,indent=2))
        except KeyboardInterrupt:
            print('Stopped watching; Hub task remains unchanged: '+a.watch,flush=True)
