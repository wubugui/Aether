#!/usr/bin/env python3
"""Read-only AST/source-order checks. Never starts Godot or claims native tests."""
import ast
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE=Path(__file__).resolve().parent
ORBIT=HERE.parent

def require(ok, name):
    if not ok:
        raise RuntimeError(name)
    return {'name':name,'passed':True}

def section(text, name):
    return text.split('func '+name+'(',1)[1].split('\nfunc ',1)[0]

def main():
    checks=[]
    for path in ORBIT.rglob('*.py'):
        ast.parse(path.read_text())
    checks.append(require(True,'All orbit Python files AST parse'))
    spec=importlib.util.spec_from_file_location('orbit61_runner',ORBIT/'run_orbit61.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original=module.static_checks()
    main_source=(ORBIT/'verify_orbit61.gd').read_text()
    visual=(ORBIT/'visible_geometry61.gd').read_text()
    sample=section(main_source,'sample_process')
    checks.append(require(sample.index('classify_new_geometry()')<sample.index('visual.unchanged(true,"late_process",frame)')<sample.index('sequence.sample(frame)')<sample.index('pending.append('),'New geometry and full MM witness precede queued segment'))
    capture=section(main_source,'capture')
    checks.append(require('await witness.physics_checked' in capture and 'await witness.processed' not in capture,'Capture resumes on audited physics boundary'))
    audit=section(main_source,'audit_pending')
    checks.append(require(audit.index('classify_new_geometry()')<audit.index('visual.unchanged(true,"physics_before_segments",last_frame)')<audit.index('while not pending.is_empty()'),'Physics new geometry and identity gates precede queries'))
    checks.append(require(audit.index('if not native_before.is_empty()')<audit.index('sequence.audit('),'Sequence marks audit only after all actual clearance gates'))
    geometry=section(main_source,'classify_new_geometry')
    checks.append(require('if not is_instance_valid(node): abort(' in geometry,'Removed new geometry fails closed'))
    mm=section(visual,'multimesh_identity')
    binding=section(visual,'multimesh_binding_identity')
    checks.append(require(binding.index('if mm==null: return')<binding.index('mm.mesh') and mm.index('multimesh_binding_identity(node)')<mm.index('mm.instance_count') and 'buffer.to_byte_array()' in mm and 'HashingContext.HASH_SHA256' in mm,'Explicit null/binding guard precedes full native buffer hashing'))
    checks.append(require('RenderingServer.multimesh_get_mesh(mm.get_rid())' in binding and '"ok":cpu_mesh_rid==server_mesh_rid' in binding and '"server_mesh_rid":server_mesh_rid.get_id()' in binding and 'get_surface_count' not in binding and 'get_aabb' not in binding,'CPU/server stored mesh RID agreement fails before unsafe mesh queries'))
    checks.append(require(mm.index('buffer.size()!=count*stride')<mm.index('hashing.start(')<mm.index('if not bytes.is_empty() and hashing.update(bytes)!=OK')<mm.index('hashing.finish()'),'True empty buffer uses start/finish while nonzero layout mismatch still rejects'))
    checks.append(require('mesh.get_surface_count() if drawable else null' in mm and 'mesh.get_aabb()).hex_encode() if drawable else null' in mm and 'mm.get_aabb()).hex_encode() if drawable else null' in mm,'Empty bindings skip computed mesh and MultiMesh coverage queries'))
    bounds=section(visual,'geometry_bounds')
    checks.append(require(bounds.index('multimesh_binding_identity(node)')<bounds.index('multimesh_non_rendered_reason(node)')<bounds.index('node.get_aabb()') and 'return null' in bounds,'Geometry bounds guard consistent empty resources without fabricated AABB'))
    prepare=section(visual,'prepare')
    checks.append(require(prepare.index('bind_multimesh_identity(watch)')<prepare.index('if not visible: continue'),'Hidden MultiMeshes acquire baseline before visibility skip'))
    runtime=section(visual,'unchanged')
    checks.append(require('if check_buffers and node is MultiMeshInstance3D:' in runtime and 'if item.query_candidate or (current_bounds is AABB and current_bounds.intersects(domain)):' in runtime and 'validate_multimesh_identity(item)' in runtime,'MM validation is separate from domain-specific transform rejection'))
    checks.append(require(runtime.index('validate_multimesh_identity(item)')<runtime.index('queued_ancestors(node)')<runtime.index('geometry_bounds(node,'),'MM resource identity validation precedes evidence and transform bounds'))
    new_geometry=section(visual,'accept_distant_new_node')
    checks.append(require(new_geometry.index('multimesh_binding_identity(node)')<new_geometry.index('mesh.get_surface_count()'),'New MM CPU/server binding checked before material surface reads'))
    run=section(main_source,'run')
    loop=run.split('while game.orbit.x<goal-.000001',1)[1]
    checks.append(require('if not await wait_event_audited(): return' in loop and 'wait_settled()' not in loop.split('if not check(mouse_button(false)',1)[0],'Intermediate event loop uses exact-process/audit wait, not intermediate settle'))
    checks.append(require(main_source.count('if not await wait_settled(): return')==2 and 'if stable>=2:' in main_source and 'const SETTLE_METERS := .02' in main_source,'Startup and target settling keep two samples and .02m'))
    fixture_source=(HERE/'fixture.gd').read_text()
    checks.append(require('identity.mesh_instance_id>0' not in fixture_source and 'identity.multimesh_instance_id>0' not in fixture_source and 'is_instance_id_valid(identity.mesh_instance_id)' in fixture_source and 'instance_from_id(identity.multimesh_instance_id)==stable.node.multimesh' in fixture_source,'Native ObjectIDs checked by nonzero/live resolution, never positive sign'))
    checks.append(require('"held_multimesh":mm,"held_mesh":mesh' in fixture_source and 'dispose_fixture(f)' in section(fixture_source,'check_guard') and section(fixture_source,'dispose_fixture').index('f.held_multimesh.mesh=f.held_mesh')<section(fixture_source,'dispose_fixture').index('f.node.free()'),'Negative fixture resources retained and binding restored before disposal'))
    old_fixture=(module.AETHER/'cloud-evidence/nearbay61-continuous-v6-20261002T054712Z-k649_9in/source-snapshot/continuous-v6/fixture.gd').read_text()
    import re
    check_pattern=r'(?:record|check_guard)\("([^"\n]+)"'
    old_names=set(re.findall(check_pattern,old_fixture))
    current_names=re.findall(check_pattern,fixture_source)
    checks.append(require(len(old_names)==48 and old_names.issubset(current_names) and len(current_names)==61 and len(set(current_names))==61,'All prior 48 native checks retained plus 13 explicit empty/binding cases'))
    fixture_wrapper=(HERE/'run_fixture.py').read_text()
    wrapper_tree=ast.parse(fixture_wrapper)
    command=next(node.value for node in ast.walk(wrapper_tree) if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='command' for t in node.targets))
    literals=[node.value for node in ast.walk(command) if isinstance(node,ast.Constant) and isinstance(node.value,str)]
    checks.append(require('--headless' not in literals and '--display-driver' in literals and 'x11' in literals and '--rendering-method' in literals and 'gl_compatibility' in literals and '320x180' in literals,'Native mutation fixture uses actual small X11 GL window, not dummy headless'))
    checks.append(require('set_instance_transform' in fixture_source and 'set_instance_color' in fixture_source and 'set_instance_custom_data' in fixture_source and 'get_instance_transform' in fixture_source and 'get_instance_color' in fixture_source and 'get_instance_custom_data' in fixture_source and 'get_current_rendering_driver_name' in fixture_source,'Fixture retains real native setters/readbacks and reports actual backend'))
    checks.append(require('LIVE_RESOURCE_IDENTITY_SCOPE' in main_source and '"live_resource_identity_scope":LIVE_RESOURCE_IDENTITY_SCOPE' in main_source and '"universal_live_resource_freeze_proved":false' in main_source and 'material_shader_limit' in main_source and 'ship_limit' in main_source,'Full engine reports retain explicit live Mesh/material/shader/ship identity limits'))
    reviewed,evidence=module.dependency_validation()
    checks.append(require(evidence['reviewed_closure_files']==1483 and evidence['exact_prior_manifest_delta_files']==51 and evidence['packaged_auditors_match_frozen_embedded_sources'] is True,'Exact immutable saved loading closure and packaged auditor identities verified'))
    inputs=module.source_manifest()
    checks.append(require(all(str(module.DEPENDENCY_HOME/name) in inputs for name in module.DEPENDENCY_FILES) and set(reviewed).issubset(inputs),'Reviewed closure/guard/gzip/auditor files included in input manifest'))
    runner=(ORBIT/'run_orbit61.py').read_text()
    checks.append(require("result['dependency_guard_before'] = dependency_validation()" in runner and "result['dependency_guard_after'] = dependency_validation()" in runner and "target = out / 'dependency-review62' / relative" in runner,'Wrapper checks full dependency guard before children and finally, and snapshots auditors/review'))
    tests=module.SUPPORT.strict_json(HERE/'WRAPPER_TESTS.json')
    checks.append(require(tests.get('passed') is True and tests.get('tests_run')==29 and tests.get('godot_invoked') is False and all(hashlib.sha256((ORBIT/name).read_bytes()).hexdigest()==sha for name,sha in tests['tested_source_sha256'].items()),'29 Python-only wrapper tests match final source hashes'))
    deadline=module.SUPPORT.strict_json(HERE/'deadline-v1/TESTS.json')
    checks.append(require(deadline.get('passed') is True and deadline.get('tests_run')==10 and deadline.get('godot_invoked') is False and deadline.get('native_clock_tested') is False and all(hashlib.sha256((ORBIT/name).read_bytes()).hexdigest()==sha for name,sha in deadline['tested_source_sha256'].items()),'10 deadline source-order and isolated Python tests match current sources; no native clock proof'))
    files=[ORBIT/name for name in ['verify_orbit61.gd','visible_geometry61.gd','run_orbit61.py','native_sequence61.gd','orbit_telemetry61.gd']]+[HERE/name for name in ['README.md','fixture.gd','run_fixture.py','wrapper_support.py','test_wrappers.py','check_static.py','WRAPPER_TESTS.json','EMPTY_RESOURCE_SOURCES.json']]
    return {'version':'orbit61-continuous-v6-preparation','passed':True,'checks':checks,'original_static_checks':original,'source_sha256':{str(p.relative_to(ORBIT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'wrapper_python_tests':tests,'dependency_guard':evidence,'godot_invoked':False,'gdscript_parse_passed':False,'native_fixture_passed':False,'world_run_passed':False,'scope':'Python AST/source assertions, 29 isolated wrapper tests, unchanged inherited1477 inputs and exact1483 saved loading closure/absence guards. Graphical native mutation fixture and GDScript parsing remain unrun; no universal live-resource identity or world acceptance.'}

if __name__=='__main__':
    print(json.dumps(main(),indent=2))
