import io,struct,hashlib,zstandard

def inspect(path):
 raw=path.read_bytes();compressed=False
 if raw[:4]==b'RSCC':
  mode,block,total=struct.unpack_from('<3I',raw,4)
  if mode!=2 or not block:raise ValueError('unsupported compressed mode/block')
  count=total//block+1;sizes=struct.unpack_from('<'+'I'*count,raw,16);pos=16+4*count;chunks=[]
  for i,size in enumerate(sizes):
   expected=min(block,total-i*block)
   chunk=zstandard.ZstdDecompressor().decompress(raw[pos:pos+size],max_output_size=max(1,expected));pos+=size
   if len(chunk)!=expected:raise ValueError('decompressed block length mismatch')
   chunks.append(chunk)
  if pos+4!=len(raw) or raw[pos:]!=b'RSCC':raise ValueError('compressed tail')
  data=b''.join(chunks);f=io.BytesIO(data);compressed=True
 elif raw[:4]==b'RSRC':data=raw;f=io.BytesIO(data);f.seek(4)
 else:raise ValueError('unsupported magic')
 def rd(fmt):
  n=struct.calcsize(fmt);b=f.read(n)
  if len(b)!=n:raise ValueError('truncated')
  r=struct.unpack(fmt,b);return r[0] if len(r)==1 else r
 def skip(n):
  if n<0 or f.tell()+n>len(data):raise ValueError('invalid skip')
  f.seek(n,1)
 def st():
  n=rd('<I')
  if n>len(data)-f.tell():raise ValueError('string overflow')
  return f.read(n).rstrip(b'\0').decode('utf8')
 be,r64,major,minor,ver=rd('<5I')
 if be or r64 or major!=4 or ver>6:raise ValueError('unreviewed format')
 cls=st();metadata=rd('<Q');flags=rd('<I');uid=rd('<Q');reserved=rd('<11I')
 if flags&~3 or any(reserved):raise ValueError('unknown header flags')
 names=[st() for _ in range(rd('<I'))]
 def named():
  n=rd('<I')
  if n&0x80000000:
   size=n&0x7fffffff
   if size>len(data)-f.tell():raise ValueError('named string overflow')
   return f.read(size).rstrip(b'\0').decode()
  if n>=len(names):raise ValueError('name index out of bounds')
  return names[n]
 ext=[]
 for _ in range(rd('<I')):
  t,p=st(),st();eu=rd('<Q') if flags&2 else None;ext.append({'type':t,'path':p,'uid':eu})
 intern=[(st(),rd('<Q')) for _ in range(rd('<I'))];objectrefs=[];kinds=set()
 def variant(depth=0):
  if depth>32:raise ValueError('deep variant')
  k=rd('<I');kinds.add(k)
  if k==1:return None
  if k in (2,3,23):return rd('<I')
  if k==4:skip(4);return '<float>'
  if k in (40,41):skip(8);return '<64bit>'
  if k in (5,44):return st()
  fixed={10:8,11:16,12:12,13:16,14:16,15:24,16:36,17:48,18:24,20:16,45:8,46:16,47:12,50:16,51:16,52:64}
  if k in fixed:skip(fixed[k]);return '<fixed>'
  if k==22:
   a,b=rd('<HH');b=(b&0x7fff)+(1 if ver<3 else 0)
   return {'node_path':[named() for _ in range(a+b)]}
  if k==24:
   tag=rd('<I')
   if tag==0:return None
   if tag in (2,3):
    index=rd('<I');ref={'tag':tag,'index':index}
    if tag==3:
     if index>=len(ext):raise ValueError('external ref index overflow')
     ref['external']=ext[index]
    elif flags&1 and index>=len(intern):raise ValueError('internal ref index overflow')
   elif tag==1:ref={'tag':tag,'type':st(),'path':st()}
   else:raise ValueError('unknown object tag')
   objectrefs.append(ref);return ref
  if k in (42,43):return '<empty callable/signal>'
  if k==26:
   n=rd('<I')&0x7fffffff;result=[]
   for _ in range(n):result.append([variant(depth+1),variant(depth+1)])
   return {'dictionary':result}
  if k==30:
   n=rd('<I')&0x7fffffff
   return [variant(depth+1) for _ in range(n)]
  if k==34:return [st() for _ in range(rd('<I'))]
  packed={31:1,32:4,33:4,35:12,36:16,37:8,48:8,49:8,53:16}
  if k in packed:
   n=rd('<I');skip(n*packed[k]);
   if k==31:skip((-n)%4)
   return {'packed_type':k,'length':n,'payload_not_decoded':True}
  raise ValueError('unknown variant '+str(k))
 resources=[];scripts=[];legacy=[]
 for i,(name,offset) in enumerate(intern):
  f.seek(offset);typ=st();n=rd('<I');props=[]
  for _ in range(n):
   prop=named();v=variant();props.append(prop)
   if prop=='script':scripts.append({'internal':name,'class':typ,'value':v})
  expected=intern[i+1][1] if i+1<len(intern) else len(data)-4
  if f.tell()!=expected:raise ValueError('resource record boundary mismatch '+str((name,f.tell(),expected)))
  resources.append({'path':name,'type':typ,'property_names':props})
 if data[-4:]!=b'RSRC':raise ValueError('resource trailing marker')
 for ref in objectrefs:
  if ref['tag']==1:legacy.append(ref)
 return {'compressed':compressed,'decoded_byte_count':len(data),'decoded_sha256':hashlib.sha256(data).hexdigest() if compressed else None,'class':cls,'format':ver,'engine':[major,minor],'flags':flags,'external':ext,'internal_resources':resources,'script_properties':scripts,'legacy_inline_external_refs':legacy,'variant_kinds':sorted(kinds),'full_property_stream_boundaries_validated':True}
