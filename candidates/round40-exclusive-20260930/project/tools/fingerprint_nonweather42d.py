"""Exact structural/content fingerprint ignoring only the Weather42b subtree.
No Godot rendering or scene mutation. Resource IDs resolved recursively to content.
"""
import hashlib, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = pathlib.Path(sys.argv[1])
IGNORE_PARAMS = "--ignore-shader-params" in sys.argv
HEADER = re.compile(r'^\[(?:gd_scene|ext_resource|sub_resource|node|connection|editable)\b[^\n]*\]', re.M)
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def parse(path):
    text=path.read_text()
    matches=list(HEADER.finditer(text))
    sections=[text[m.start():(matches[i+1].start() if i+1<len(matches) else len(text))].strip() for i,m in enumerate(matches)]
    ext={}; sub={}; nodes={}; cache={}
    for s in sections:
        h=s.split('\n',1)[0]
        if h.startswith('[ext_resource '):
            ident=re.search(r' id="([^"]+)"',h)[1]
            ext[ident]=re.sub(r' id="[^"]+"','',h)
        if h.startswith('[sub_resource '):
            ident=re.search(r' id="([^"]+)"',h)[1]
            sub[ident]=re.sub(r' id="[^"]+"','',s,count=1)
    def canonical(s):
        if IGNORE_PARAMS: s=re.sub(r"^shader_parameter/[^\n]*\n?", "", s, flags=re.M)
        s=re.sub(r'ExtResource\("([^"]+)"\)',lambda m: 'ExtContent('+ext[m[1]]+')',s)
        return re.sub(r'SubResource\("([^"]+)"\)',lambda m: 'SubContent('+resource(m[1])+')',s)
    def resource(ident):
        if ident not in cache: cache[ident]=sha(canonical(sub[ident]))
        return cache[ident]
    for s in sections:
        h=s.split('\n',1)[0]
        if not h.startswith('[node '): continue
        name=re.search(r' name="([^"]+)"',h)[1]
        match=re.search(r' parent="([^"]+)"',h)
        parent=match[1] if match else ''
        path=name if parent in ('','.') else parent+'/'+name
        if path=='Weather42b' or path.startswith('Weather42b/'): continue
        nodes[path]=sha(canonical(s))
    return nodes
before=parse(ROOT/'scenes/candidate42c/Game42c.tscn')
after=parse(ROOT/'scenes/candidate42d/Game42d.tscn')
changed=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
report={'passed':not changed,'method':'Exact normalized node content plus recursively resolved referenced resource content; all Weather42b nodes excluded, nothing else', 'shader_parameters_excluded_for_diagnostic':IGNORE_PARAMS,'before_node_count':len(before),'after_node_count':len(after),'changed_nodes':changed,'before_sha256':sha(json.dumps(before,sort_keys=True)),'after_sha256':sha(json.dumps(after,sort_keys=True))}
OUTPUT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='changed_nodes'},indent=2));print('changed_node_count',len(changed));sys.exit(0 if report['passed'] else 1)
