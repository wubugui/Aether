import collections,hashlib,json,mmap,re,struct,time
from pathlib import Path
P=Path('/workspace/scratch/a29d03198654/Aether/candidates/round40-exclusive-20260930/project')
A=P.parents[2]
entry='res://scenes/candidate61-coast/Game61Coast.tscn'
seen={};edges=[];queue=[entry];gaps=[];scripts={};attachments=[];uid_headers=[]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def edge(src,dst,kind,extra=None):
 edges.append({'from':src,'to':dst,'kind':kind,**(extra or {})})
 if dst.startswith('res://') and dst not in seen and dst not in queue:queue.append(dst)
 elif not dst.startswith('res://'):gaps.append({'file':src,'kind':'external_path','target':dst})
def attrs(header):return {k:v for k,v in re.findall(r'(\w+)="((?:[^"\\]|\\.)*)"',header)}
def binary_header(p):
 with p.open('rb') as f:
  magic=f.read(4)
  if magic!=b'RSRC':raise ValueError('unsupported magic '+repr(magic))
  size=p.stat().st_size
  def read(fmt):
   n=struct.calcsize(fmt);b=f.read(n)
   if len(b)!=n:raise ValueError('truncated header')
   r=struct.unpack(fmt,b);return r[0] if len(r)==1 else r
  def string():
   n=read('<I')
   if not 0<=n<=size-f.tell():raise ValueError('invalid string length')
   return f.read(n).rstrip(b'\0').decode('utf-8')
  be,real64,major,minor,ver=read('<5I')
  if be or real64 or major!=4 or ver>6:raise ValueError('unreviewed binary format '+repr((be,real64,major,minor,ver)))
  cls=string();metadata=read('<Q');flags=read('<I');uid=read('<Q');reserved=read('<11I')
  if flags&~3 or any(reserved):raise ValueError('unknown flags/reserved '+repr(flags))
  names=[string() for _ in range(read('<I'))]
  ext=[]
  for _ in range(read('<I')):
   typ,path=string(),string();eu=read('<Q') if flags&2 else None;ext.append({'type':typ,'path':path,'uid':eu})
  internal=[(string(),read('<Q')) for _ in range(read('<I'))]
  types=[]
  for name,offset in internal:
   if not 0<=offset<size:raise ValueError('invalid internal offset')
   f.seek(offset);types.append({'path':name,'type':string()})
  return {'class':cls,'engine':[major,minor],'format':ver,'flags':flags,'external':ext,'internal_types':types,'property_name_script_present':'script' in names,'string_table_count':len(names)}
while queue:
 uri=queue.pop(0)
 if uri in seen:continue
 p=P/uri[6:]
 if not p.is_file():seen[uri]={'missing':True};gaps.append({'file':uri,'kind':'missing_file'});continue
 item={'sha256':sha(p),'bytes':p.stat().st_size,'kind':p.suffix};seen[uri]=item
 if p.suffix in ('.tscn','.tres'):
  with p.open('rb') as f, mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as b:
   headers=[]
   for match in re.finditer(rb'(?m)^\[(?:ext_resource|sub_resource|resource|node)[^\r\n]*\]',b):
    h=match.group().decode();a=attrs(h);headers.append((match.start(),h,a))
    if h.startswith('[ext_resource'):
     edge(uri,a.get('path',''),'text_ext_resource',{'type':a.get('type'),'id':a.get('id'),'uid':a.get('uid')})
     if a.get('uid'):uid_headers.append({'source':uri,**a})
    elif a.get('type') in ['GDScript','CSharpScript','Script']:
     gaps.append({'file':uri,'kind':'embedded_script_resource','header':h})
   for match in re.finditer(rb'(?m)^script\s*=\s*([^\r\n]*)',b):
    i=max((i for i,x in enumerate(headers) if x[0]<match.start()),default=-1)
    owner=headers[i][1] if i>=0 else 'unknown'
    attachments.append({'file':uri,'owner':owner,'assignment':match.group().decode(),'owner_is_node':owner.startswith('[node')})
   item['external_resources']=sum(h.startswith('[ext_resource') for _,h,_ in headers)
   item['embedded_resource_types']=dict(collections.Counter(a.get('type','<root>') for _,h,a in headers if h.startswith('[sub_resource')))
 elif p.suffix=='.gd':
  text=p.read_text();decls=[]
  for no,line in enumerate(text.splitlines(),1):
   s=line.strip()
   if re.match(r'(extends\b|class_name\b|@tool\b|(?:static\s+)?(?:var|const|func)\b)',s) and (line==line.lstrip() or re.search(r'\b_static_init\b',line)):decls.append({'line':no,'text':line})
   for m in re.finditer(r'preload\s*\(\s*([\'"])(.*?)\1\s*\)',line):edge(uri,m[2],'gd_preload',{'line':no})
   m=re.match(r'\s*extends\s+([\'"])(.*?)\1',line)
   if m:edge(uri,m[2],'gd_extends',{'line':no})
  scripts[uri]={'sha256':item['sha256'],'declarations':decls,'static_vars':[(i,l.strip()) for i,l in enumerate(text.splitlines(),1) if re.match(r'\s*static\s+var\b',l)],'static_init':[(i,l.strip()) for i,l in enumerate(text.splitlines(),1) if re.match(r'\s*(?:static\s+)?func\s+_static_init\b',l)],'constructors':[(i,l.strip()) for i,l in enumerate(text.splitlines(),1) if re.match(r'\s*func\s+_init\b',l)],'extends':next((l.strip() for l in text.splitlines() if re.match(r'\s*extends\b',l)),None),'tool_annotation':bool(re.search(r'^\s*@tool\b',text,re.M))}
 elif p.suffix in ('.res','.mesh','.scn'):
  try:
   info=binary_header(p);item['binary_header']=info
   for dep in info['external']:
    edge(uri,dep['path'],'binary_external_table',{'type':dep['type'],'uid':dep['uid']})
    if dep['uid'] not in (None,0,2**64-1):uid_headers.append({'source':uri,**dep})
   if info['property_name_script_present']:gaps.append({'file':uri,'kind':'binary_script_property_needs_value_review'})
   for inner in info['internal_types']:
    if 'Script' in inner['type']:gaps.append({'file':uri,'kind':'binary_embedded_script_type','internal':inner})
  except Exception as exc:gaps.append({'file':uri,'kind':'binary_dependency_metadata_unparsed','error':str(exc)})
 elif p.suffix=='.gdshader':
  for m in re.finditer(r'^\s*#include\s+"([^"]+)"',p.read_text(),re.M):edge(uri,m[1],'shader_include')
 elif p.suffix in ('.png','.jpg','.jpeg','.exr','.glb','.gltf','.svg'):
  imp=Path(str(p)+'.import')
  if imp.is_file():
   seen[uri+'.import']={'sha256':sha(imp),'bytes':imp.stat().st_size,'kind':'.import'}
   t=imp.read_text();m=re.search(r'^path="([^"]+)"',t,re.M)
   if m:edge(uri,m[1],'import_remap')
   else:gaps.append({'file':uri,'kind':'import_remap_missing'})
  else:gaps.append({'file':uri,'kind':'asset_import_metadata_absent'})
 elif p.suffix=='.ctex':
  item['dependency_terminal']='native compressed texture, no user-script attachment inspected; format-specific confirmation still required'
 else:gaps.append({'file':uri,'kind':'unknown_dependency_file_type'})
report={'at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'entry':entry,'files':seen,'edges':edges,'scripts':scripts,'script_attachments':attachments,'uid_declarations':uid_headers,'gaps':gaps,'engines_started':False}
Path('/tmp/north62-dependency-graph.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'file_count':len(seen),'edges':len(edges),'scripts':len(scripts),'script_attachments':len(attachments),'uid_declarations':len(uid_headers),'gaps':gaps,'script_summary':{k:{s:v[s] for s in ['extends','static_vars','static_init','constructors','tool_annotation']} for k,v in scripts.items()}},indent=2))
