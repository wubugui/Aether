#!/usr/bin/env python3
"""Run the exact pinned built_in_strtod template in a standalone C++ harness.
This is a source reproduction, not a Godot run and not recovered old native bits.
"""
from pathlib import Path
import gzip,hashlib,json,struct,subprocess,tempfile
HERE=Path(__file__).resolve().parent
V1=HERE.parent/'scatter-readonly-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def require(ok,why):
    if not ok:raise RuntimeError(why)
def main():
    raw=gzip.decompress((V1/'prepared-inputs.json.gz').read_bytes());inputs=json.loads(raw)
    source=(HERE/'upstream/core__string__ustring.cpp').read_text()
    start=source.index('template <typename C>\nstatic double built_in_strtod(');end=source.index('\n#define READING_SIGN',start)
    extracted=source[start:end]
    prefix='''#include <iostream>
#include <iomanip>
#include <cstring>
#include <string>
#include <cstdint>
template<class C> static bool is_digit(C c){return c>='0' && c<='9';}
#define WARN_PRINT(x) do { throw "unexpected exponent overflow"; } while(0)
'''
    suffix='''
int main(){
static_assert(sizeof(float)==4 && sizeof(double)==8,"IEEE storage width required");
std::string s;
while(std::getline(std::cin,s)){
std::u32string u(s.begin(),s.end());char32_t *end=nullptr;
double d=built_in_strtod<char32_t>(u.c_str(),&end);float f=static_cast<float>(d);
if(end!=u.c_str()+u.size())return 2;
const auto print=[](const void *p,size_t n){auto b=static_cast<const unsigned char *>(p);for(size_t i=0;i<n;i++)std::cout<<std::hex<<std::setfill('0')<<std::setw(2)<<unsigned(b[i]);};
print(&d,8);std::cout<<" ";print(&f,4);std::cout<<"\\n";
}}
'''
    harness=prefix+extracted+suffix
    tokens=[(group['path'],i,json.dumps(v),v)for group in inputs['groups']for i,v in enumerate(group['world_transform_columns'])]
    with tempfile.TemporaryDirectory(prefix='scatter-json-source-')as t:
        p=Path(t);(p/'source.cpp').write_text(harness)
        command=['g++','-std=c++17','-O0','-ffp-contract=off',str(p/'source.cpp'),'-o',str(p/'reproduce')]
        compiled=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
        require(compiled.returncode==0,'standalone compile failed '+compiled.stderr)
        executed=subprocess.run([str(p/'reproduce')],input='\n'.join(x[2]for x in tokens)+'\n',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
        require(executed.returncode==0 and not executed.stderr,'source reproduction failed')
    lines=executed.stdout.splitlines();require(len(lines)==len(tokens),'source result count differs')
    changed=[]
    for (path,index,token,oracle),line in zip(tokens,lines):
        raw64,raw32=line.split();want32=struct.pack('<f',oracle).hex();want64=struct.pack('<d',oracle).hex()
        require(raw32==want32,'JSON cannot recover exact float32 source '+path)
        if raw64!=want64:
            changed.append({'path':path,'component_index':index,'input_token':token,'source_reproduced_json_float64_hex_le':raw64,'independent_float32_lifted_to_float64_hex_le':want64,'same_float32_hex_le':want32,'delta':struct.unpack('<d',bytes.fromhex(raw64))[0]-oracle})
    target=[x for x in changed if x['path']=='World/Vegetation/Authored_WestRoadCopse']
    require(len(target)==1 and target[0]['component_index']==10 and target[0]['source_reproduced_json_float64_hex_le']=='010000004c2b2c40','known JSON defect not reproduced')
    return {'status':'passed_exact_pinned_source_reproduction','godot_invoked':False,'old_native_raw_bits_recovered':False,'fresh_native_fixture_still_required':True,'official_commit':'f62fdbde15035c5576dad93e586201f4d41ef0cb','prepared_inputs_sha256':sha(raw),'extracted_function_sha256':sha(extracted.encode()),'harness_sha256':sha(harness.encode()),'compiler_flags':['-std=c++17','-O0','-ffp-contract=off'],'compile_returncode':compiled.returncode,'execute_returncode':executed.returncode,'component_count':len(tokens),'canonical_float32_identity_matches':len(tokens),'binary64_transport_differences':changed,'known_failure_component':target[0]}
if __name__=='__main__':print(json.dumps(main(),indent=2))
