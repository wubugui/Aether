"""Fetch only the Windows runtime from the official template ZIP using ranges."""
from pathlib import Path
import requests,struct,zlib
ROOT=Path(__file__).resolve().parents[1]
URL='https://github.com/godotengine/godot-builds/releases/download/4.5.1-stable/Godot_v4.5.1-stable_export_templates.tpz'
SIZE=1355592535
def fetch(a,b):
    with requests.get(URL,headers={'Range':f'bytes={a}-{b}'},stream=True,timeout=90) as response:
        if response.status_code!=206:
            raise RuntimeError(f'Server did not honor a range request: {response.status_code}')
        result=response.content
        if len(result)!=b-a+1:raise RuntimeError('Unexpected range length')
        return result
tail=fetch(SIZE-131072,SIZE-1)
cursor=0;found=None
while True:
    offset=tail.find(b'PK\x01\x02',cursor)
    if offset<0:break
    fields=struct.unpack_from('<4s6H3I5H2I',tail,offset)
    name=tail[offset+46:offset+46+fields[10]].decode('utf-8')
    cursor=offset+46+fields[10]+fields[11]+fields[12]
    if name=='templates/windows_release_x86_64.exe':found=fields;break
if found is None:raise RuntimeError('Windows release runtime missing')
local=fetch(found[16],found[16]+29)
name_len,extra_len=struct.unpack_from('<HH',local,26)
start=found[16]+30+name_len+extra_len
compressed=fetch(start,start+found[8]-1)
data=zlib.decompress(compressed,-15) if found[4]==8 else compressed
if len(data)!=found[9] or zlib.crc32(data)!=found[7]:raise RuntimeError('Runtime CRC mismatch')
target=ROOT/'.tools/godot/windows_release_x86_64.exe';target.write_bytes(data)
print('Verified official Godot 4.5.1 Windows release runtime:',len(data),'bytes; downloaded',len(compressed),'bytes')
