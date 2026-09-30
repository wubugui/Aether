import pathlib,re,json,math,sys
p=pathlib.Path(__file__).resolve().parents[1]
head=re.compile(r'^\[(?:gd_scene|ext_resource|sub_resource|node)\b[^\n]*\]',re.M)
def load(n):
 s=(p/f'scenes/candidate{n}/Game{n}.tscn').read_text();mm=list(head.finditer(s));secs=[s[m.start():(mm[i+1].start() if i+1<len(mm) else len(s))].strip() for i,m in enumerate(mm)];sub={};ext={}
 for x in secs:
  h=x.split('\n',1)[0];mid=re.search(r' id="([^"]+)"',h)
  if h.startswith('[sub_resource'): sub[mid[1]]=x
  if h.startswith('[ext_resource'): ext[mid[1]]=re.search(r' path="([^"]+)"',h)[1]
 return sub,ext
old,oe=load('42c');new,ne=load('42d');changes=[];bad=[]
def params(s):return dict(re.findall(r'^shader_parameter/(\w+) = ([^\n]*)',s,re.M))
def val(s):
 s=s.strip()
 if s in ('true','false'):return s
 m=re.match(r'(?:vec|Vector)([234])\(([^)]+)\)',s)
 if m:
  a=[float(i) for i in m[2].split(',')];return a*int(m[1]) if len(a)==1 else a
 try:return [float(s)]
 except:return s
for ident,a in old.items():
 if ident not in new:continue
 b=new[ident];pa=params(a);pb=params(b)
 if pa==pb:continue
 ref=re.search(r'^shader = (SubResource|ExtResource)\("([^"]+)"\)',b,re.M)
 if not ref: bad.append({'resource':ident,'reason':'no shader'});continue
 shader=new[ref[2]] if ref[1]=='SubResource' else (p/ne[ref[2]].removeprefix('res://')).read_text()
 defaults=dict(re.findall(r'uniform\s+(?:bool|int|float|vec[234])\s+(\w+)(?:\s*:[^=;]+)?\s*=\s*([^;]+);',shader))
 for name in set(pa)|set(pb):
  if pa.get(name)==pb.get(name):continue
  expected=defaults.get(name,'MISSING')
  v1=val(pb.get(name,''));v2=val(expected)
  match=v1==v2 or (isinstance(v1,list) and isinstance(v2,list) and len(v1)==len(v2) and all(math.isclose(x,y,rel_tol=1e-6,abs_tol=1e-6) for x,y in zip(v1,v2)))
  row={'resource':ident,'parameter':name,'before':pa.get(name),'after':pb.get(name),'shader_default':expected,'is_null_to_shader_default':pa.get(name)=='null' and match}
  changes.append(row)
  if not row['is_null_to_shader_default']:bad.append(row)
report={'changed_shader_parameters':len(changes),'all_changes_are_null_to_declared_shader_defaults':not bad,'unexpected_changes':bad,'changes':changes}
out=pathlib.Path(sys.argv[1]);out.write_text(json.dumps(report,indent=2))
print(len(changes),'changes',len(bad),'unexpected');print(json.dumps(bad[:20],indent=2))
