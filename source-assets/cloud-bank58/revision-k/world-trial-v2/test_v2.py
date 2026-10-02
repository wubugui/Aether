"""Pure/synthetic migration tests. Never touch the actual bound work copy."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
sys.dont_write_bytecode=True
import binding58k as b
import relocate58k as r
import run_renderer58k as renderer


class V2Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='cloud58k-v2-synthetic-test-')
        self.root=Path(self.temp.name);self.src=self.root/'source';self.dst=self.root/'destination'
        self.src.mkdir();self.dst.mkdir();self.a=self.src/'tiny.txt';self.z=self.dst/'tiny.txt'
        self.a.write_bytes(b'synthetic relocation fixture\x00\xff')
        self.digest=b.sha(self.a);self.journal=self.root/'journal.jsonl'
    def tearDown(self):self.temp.cleanup()

    def test_single_synthetic_file_move(self):
        r.move_member(self.a,self.z,self.digest,self.journal,'tiny.txt')
        self.assertFalse(self.a.exists());self.assertEqual(b.sha(self.z),self.digest)
        events=[json.loads(x) for x in self.journal.read_text().splitlines()]
        self.assertEqual([x['state'] for x in events],['copy_started','destination_verified_and_synced','moved_source_removed'])
        self.assertIn('destination_signature',events[1])
        self.assertEqual(r.partition(self.src,self.dst,{'tiny.txt':self.digest})['tiny.txt']['state'],'moved')

    def test_stream_hash_mismatch_preserves_source(self):
        with self.assertRaises(ValueError):r.move_member(self.a,self.z,'0'*64,self.journal,'tiny.txt')
        self.assertEqual(b.sha(self.a),self.digest)
        self.assertTrue(r.partition(self.src,self.dst,{'tiny.txt':self.digest})['tiny.txt']['original_recoverable'])

    def test_existing_destination_never_overwritten(self):
        self.z.write_bytes(b'existing')
        with self.assertRaises(ValueError):r.move_member(self.a,self.z,self.digest,self.journal,'tiny.txt')
        self.assertEqual(self.z.read_bytes(),b'existing');self.assertTrue(self.a.exists())

    def test_verification_journal_failure_retains_both(self):
        original=r.append_event
        def write(path,event):
            if event['state']=='destination_verified_and_synced':raise OSError('synthetic journal failure')
            original(path,event)
        with mock.patch.object(r,'append_event',side_effect=write):
            with self.assertRaises(OSError):r.move_member(self.a,self.z,self.digest,self.journal,'tiny.txt')
        self.assertEqual(b.sha(self.a),self.digest);self.assertEqual(b.sha(self.z),self.digest)

    def test_unlink_failure_retains_verified_both(self):
        original=Path.unlink
        def unlink(path,*args,**kwargs):
            if path==self.a:raise PermissionError('synthetic unlink failure')
            return original(path,*args,**kwargs)
        with mock.patch.object(Path,'unlink',unlink):
            with self.assertRaises(PermissionError):r.move_member(self.a,self.z,self.digest,self.journal,'tiny.txt')
        self.assertEqual(r.partition(self.src,self.dst,{'tiny.txt':self.digest})['tiny.txt']['state'],'both_verified')

    def test_post_unlink_journal_failure_has_verified_destination(self):
        original=r.append_event
        def write(path,event):
            if event['state']=='moved_source_removed':raise OSError('synthetic final journal failure')
            original(path,event)
        with mock.patch.object(r,'append_event',side_effect=write):
            with self.assertRaises(OSError):r.move_member(self.a,self.z,self.digest,self.journal,'tiny.txt')
        result=r.partition(self.src,self.dst,{'tiny.txt':self.digest})['tiny.txt']
        self.assertTrue(result['original_recoverable']);self.assertEqual(result['state'],'moved')

    def test_symlink_and_relative_path_escape_reject(self):
        link=self.src/'link';link.symlink_to(self.a)
        with self.assertRaises(ValueError):b.inspect_tree(self.src)
        with self.assertRaises(ValueError):b.relative_manifest({'/outside/a':'0'*64},self.src)
        with self.assertRaises(ValueError):b.relative_manifest({str(self.src/'..'/'a'):'0'*64},self.src)

    def test_empty_directories_and_membership_recorded(self):
        (self.src/'empty').mkdir();tree=b.inspect_tree(self.src)
        self.assertEqual(tree['directories'],['empty'])
        self.assertEqual(tree['files'],{'tiny.txt':self.digest})
        other=dict(tree);other['directories']=[]
        self.assertNotEqual(b.canonical_sha(tree),b.canonical_sha(other))

    def test_partition_read_error_does_not_discard_other_members(self):
        other=self.src/'other.txt';other.write_bytes(b'other');digest=b.sha(other)
        real=b.sha
        def reading(path):
            if path==self.a:raise PermissionError('synthetic read failure')
            return real(path)
        with mock.patch.object(b,'sha',side_effect=reading):
            rows=r.partition(self.src,self.dst,{'tiny.txt':self.digest,'other.txt':digest})
        self.assertEqual(len(rows),2)
        self.assertEqual(rows['tiny.txt']['read_errors'][0]['side'],'source')
        self.assertTrue(rows['other.txt']['original_recoverable'])

    def test_directory_identities_and_durable_first_journal(self):
        (self.src/'empty').mkdir()
        identities=r.directory_identities(self.src,['empty'])
        self.assertEqual(set(identities),{'.','empty'})
        self.assertEqual(identities['.'][0],self.src.stat().st_dev)
        self.assertEqual(identities['empty'][1],(self.src/'empty').stat().st_ino)
        with mock.patch.object(r,'fsync_dir',wraps=r.fsync_dir) as sync:
            r.append_event(self.journal,{'state':'synthetic_first_record'})
            sync.assert_called_once_with(self.root)

    def test_partition_cancellation_propagates(self):
        with mock.patch.object(b,'sha',side_effect=InterruptedError('synthetic alarm')):
            with self.assertRaises(InterruptedError):r.partition(self.src,self.dst,{'tiny.txt':self.digest})

    def test_separate_move_phase_and_outer_deadline(self):
        text=(b.HERE/'relocate58k.py').read_text()
        self.assertIn('signal.setitimer(signal.ITIMER_REAL,180)',text)
        self.assertIn('300-(time.monotonic()-started)',text)
        self.assertIn("stage='partition'",text)
        self.assertIn("stage='main_project_after'",text)
        self.assertIn("stage='protected_inputs'",text)
        self.assertEqual(text.count('b.require(time.monotonic()-started<300'),3)

    def test_original_parse_binding_read_only(self):
        expected=b.parse_authority()
        self.assertEqual(len(expected),4889)
        self.assertEqual(b.sha(b.V1/'preparation-freeze.json'),b.V1_FREEZE_SHA)
        self.assertEqual(b.DESTINATION,b.ROOT.parent/'Aether-working/cloud58k-world-trial-v2')

    def test_original_all_image_gates_ast_exact(self):
        tree=ast.parse((b.V1/'run_world58k.py').read_text())
        old=None
        for node in ast.walk(tree):
            if isinstance(node,ast.If) and node.body and isinstance(node.body[0],ast.Assign) and isinstance(node.body[0].targets[0],ast.Name) and node.body[0].targets[0].id=='native':old=node.body[:-1]
        self.assertIsNotNone(old)
        new_tree=ast.parse((b.HERE/'run_renderer58k.py').read_text())
        fn=next(n for n in new_tree.body if isinstance(n,ast.FunctionDef) and n.name=='validate_images')
        start=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='native')
        self.assertEqual([ast.dump(n) for n in old],[ast.dump(n) for n in fn.body[start:]])

    def test_original_native_sources_and_budget_reused(self):
        self.assertEqual(b.old.LIMITS['renderer_child_seconds'],240)
        self.assertEqual(b.old.LIMITS['wrapper_seconds'],300)
        self.assertEqual(b.support.MAX_RSS_KIB,3145728)
        self.assertFalse(list(b.HERE.glob('*.gd')))
        text=(b.HERE/'run_renderer58k.py').read_text()
        self.assertIn("'res://cloud_k_trial/observe58k.gd'",text)
        self.assertNotIn('copytree(b.old.p.PROJECT',text)
        self.assertNotIn('copytree(b.DESTINATION',text)
        self.assertNotIn('--parse-only',text)
        self.assertNotIn('DISPLAY=',text)
        for path in b.HERE.glob('*.py'):ast.parse(path.read_text())

    def test_defaults_start_nothing(self):
        before=b.inspect_tree(b.HERE)
        for name in ['relocate58k.py','run_renderer58k.py']:
            env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
            result=subprocess.run([sys.executable,str(b.HERE/name)],env=env,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(before,b.inspect_tree(b.HERE))


if __name__=='__main__':unittest.main(verbosity=2)
