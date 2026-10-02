#!/usr/bin/env python3
"""Pure compatibility/source negative controls plus the unchanged 60 v3 tests."""
from __future__ import annotations
import inspect,sys,unittest
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run_shadow62_v4 as r
import test_shadow62 as prior_tests

class ScriptPathTests(unittest.TestCase):
    def test_complete_source_guards(self):
        r.source_guards()

    def test_exact_one_block_delta(self):
        actual=r.SCRIPT.read_text();baseline=r.v3.SCRIPT.read_text()
        self.assertEqual(actual.count(r.NEW_BLOCK),1)
        self.assertEqual(actual.replace(r.NEW_BLOCK,r.OLD_BLOCK),baseline)
        self.assertNotIn('ShadowAudit.resource_path',actual)

    def test_script_instance_and_type_guard_order(self):
        required=['var auditor: Variant = ShadowAudit.new()',
                  'var audit_script_value: Variant = auditor.get_script()',
                  'if not check(audit_script_value is Script,"existing shadow audit is not a Script"): return empty',
                  'var audit_script: Script = audit_script_value as Script',
                  'FileAccess.get_sha256(audit_script.resource_path) == AUDIT_SHA']
        positions=[r.NEW_BLOCK.index(token)for token in required]
        self.assertEqual(positions,sorted(positions))

    def test_old_static_property_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'outside typed Script'):
            r.exact_collector(r.v3.SCRIPT.read_text())

    def test_missing_or_relaxed_type_gate_rejected(self):
        text=r.SCRIPT.read_text()
        for replacement in ['true','audit_script_value != null','audit_script_value is Resource']:
            with self.subTest(replacement=replacement),self.assertRaises(RuntimeError):
                r.exact_collector(text.replace('audit_script_value is Script',replacement))

    def test_sha_gate_removal_or_change_rejected(self):
        text=r.SCRIPT.read_text()
        for a,b in [('FileAccess.get_sha256(audit_script.resource_path) == AUDIT_SHA','true'),
                    (r.AUDIT_SHA,'0'*64),('audit_script.resource_path','"other.gd"')]:
            with self.subTest(change=a),self.assertRaises(RuntimeError):r.exact_collector(text.replace(a,b))

    def test_unrelated_geometry_and_gate_changes_rejected(self):
        text=r.SCRIPT.read_text()
        for a,b in [('actual_sha == predicted_sha','true'),
                    ('auditor.audit_array_mesh(mesh)','{}'),
                    ('combined(item.combined_clearance_bounds,item.get_faces_bounds)','item.combined_clearance_bounds'),
                    ('JSON.stringify(result,"\\t",true,true)','JSON.stringify(result,"\\t")'),
                    ('../version-guard-v2/read_proxy_meshes62_v2.gd','../read_proxy_meshes62.gd')]:
            self.assertIn(a,text)
            with self.subTest(change=a),self.assertRaises(RuntimeError):r.exact_collector(text.replace(a,b))

    def test_launcher_only_two_label_substitutions(self):
        r.exact_main(inspect.getsource(r.main))

    def test_launcher_protection_changes_rejected(self):
        text=inspect.getsource(r.main)
        for a,b in [('legacy.launch(command,out,env)','legacy.launch(command,out,{})'),
                    ('old.validate_dependencies()','{}'),
                    ("native_parse_passed':False","native_parse_passed':True"),
                    ('old.process_ok(process,errors)','True'),
                    ('validate_native(native,request)','None'),
                    ('replay.analyze(native)','None')]:
            self.assertIn(a,text)
            with self.subTest(change=a),self.assertRaises(RuntimeError):r.exact_main(text.replace(a,b))

    def test_all_v3_frozen_files_and_original_failure_bound(self):
        pins=r.provenance_check()
        for rel,sha in r.v3.freeze_check().items():self.assertEqual(pins[str(r.V3/rel)],sha)
        self.assertIn(str(r.V3/'FINAL_SHA256.json'),pins)
        self.assertTrue(any('092937Z-rurh4rw7/wrapper-report.json'in p for p in pins))

    def test_original_protocol_and_schema_identity(self):
        self.assertEqual((r.HERE/'native-request-v3.json').read_bytes(),(r.V3/'native-request-v3.json').read_bytes())
        self.assertIs(r.validate_native,r.v3.validate_native)
        self.assertIs(r.replay,r.v3.replay)
        self.assertEqual(r.old.digest(r.HERE/'visible_geometry61.gd'),r.AUDIT_SHA)

    def test_copied_inheritance_paths_preserved(self):
        out=Path('/tmp/example-output')
        first_line=r.SCRIPT.read_text().splitlines()[0]
        path=first_line.split('"')[1]
        self.assertEqual((out/r.HERE.name/path).resolve(),out/r.V2.name/r.previous.SCRIPT.name)
        self.assertEqual(r.SCRIPT.parent,r.HERE)
        self.assertIn('preload("visible_geometry61.gd")',r.SCRIPT.read_text())

if __name__=='__main__':
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(prior_tests),unittest.defaultTestLoader.loadTestsFromTestCase(ScriptPathTests)])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful()else 1)
