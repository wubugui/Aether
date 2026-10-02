"""Engine-free checks. Tiny synthetic four-file fixtures are NOT native restores."""
import ast, copy, hashlib, json, os, sys, tempfile, types, unittest
from pathlib import Path
from unittest import mock
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import restore_contract62 as r
import run_restore_read62 as wrapper
import probe_restored62 as probe


class RestoreReadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='.pure-fixture-', dir=r.HERE)
        self.base = Path(self.temp.name)
        self.root = self.base / 'restored'; self.root.mkdir()
        self.canonical = self.base / 'original'; self.canonical.mkdir()
        self.expected = {}
        for index, name in enumerate(r.EXPECTED):
            data = ('synthetic fixture %d only\n' % index).encode()
            path = self.root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
            self.expected[name] = (len(data), hashlib.sha256(data).hexdigest())
        self.source = self.root / r.SOURCE_REL

    def tearDown(self):
        self.temp.cleanup()

    def check(self, root=None, source=None):
        return r.validate_layout(root or self.root, source or self.source, self.expected, self.canonical, r.SOURCE_REL)

    def test_exact_synthetic_four_file_layout(self):
        self.assertEqual(len(self.check()['files']), 4)

    def test_explicit_path_rejects_original_outside_and_wrong_name(self):
        original = self.canonical / r.SOURCE_REL
        original.parent.mkdir(parents=True); original.write_bytes(b'fixture')
        for root, source in [(self.canonical, original), (self.root, original), (self.base, self.source)]:
            with self.subTest(root=root, source=source), self.assertRaises(ValueError): self.check(root, source)
        alternate = self.root / 'alternate.blend'; alternate.write_bytes(b'fixture')
        with self.assertRaises(ValueError): self.check(source=alternate)

    def test_symlink_root_ancestor_and_file_rejected(self):
        alias = self.base / 'alias'; alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError): self.check(alias, alias / r.SOURCE_REL)
        self.source.unlink(); self.source.symlink_to(self.root / r.RAW_REL)
        with self.assertRaises(ValueError): self.check()

    def test_intermediate_symlink_rejected(self):
        directory = self.root / 'source-assets'
        moved = self.base / 'moved'; directory.rename(moved); directory.symlink_to(moved, target_is_directory=True)
        with self.assertRaises(ValueError): self.check()

    def test_relative_traversal_missing_rejected(self):
        for path in [Path('.'), self.root / '..' / 'restored', self.base / 'missing']:
            with self.subTest(path=path), self.assertRaises((ValueError, FileNotFoundError)): r.no_symlinks(path)

    def test_extra_file_rejected(self):
        (self.root / 'unexpected').write_text('fixture')
        with self.assertRaises(ValueError): self.check()

    def test_extra_empty_directory_rejected(self):
        (self.root / 'unexpected-empty').mkdir()
        with self.assertRaises(ValueError): self.check()

    def test_missing_file_rejected(self):
        (self.root / r.RAW_REL).unlink()
        with self.assertRaises(ValueError): self.check()

    def test_changed_content_same_length_rejected(self):
        data = self.source.read_bytes(); self.source.write_bytes(b'X' + data[1:])
        with self.assertRaises(ValueError): self.check()

    def test_hardlink_rejected(self):
        os.link(self.source, self.base / 'hardlink')
        with self.assertRaises(ValueError): self.check()

    def test_tree_identity_detects_membership_and_bytes(self):
        before = r.tree_identity(self.root)
        (self.root / 'empty').mkdir()
        self.assertNotEqual(before, r.tree_identity(self.root))
        (self.root / 'empty').rmdir(); self.source.write_bytes(b'changed')
        self.assertNotEqual(before, r.tree_identity(self.root))

    def test_raw_only_pid_affinity_may_differ(self):
        raw = dict(pid=101, cpu_affinity=[0, 1], version='fixture', geometry=[1.0, 2.0], nested={'all': True})
        other = copy.deepcopy(raw); other.update(pid=202, cpu_affinity=[2, 3])
        self.assertTrue(r.same_raw(other, raw))
        self.assertTrue(r.same_raw(dict(other, pid=101), raw))  # historical PID reuse is valid
        for changed in [dict(other, geometry=[1.0, 2.000000000000001]), dict(other, extra=True),
                        dict(other, nested={'all': False}), dict(other, nested={'all': 1}),
                        dict(other, geometry=[1, 2.0]), dict(other, pid='101')]:
            with self.subTest(changed=changed), self.assertRaises(ValueError): r.same_raw(changed, raw)

    def test_default_never_launches(self):
        with mock.patch.object(r, 'preparation_inputs', return_value={}), mock.patch.object(r.c, 'read', return_value={}), \
             mock.patch.object(r.c, 'check_binding'), mock.patch.object(r.support, 'run_child', side_effect=AssertionError('No child permitted')):
            self.assertEqual(wrapper.main([]), 0)

    def test_default_real_path_gate_is_engine_free(self):
        with mock.patch.object(r, 'preparation_inputs', return_value={}), mock.patch.object(r.c, 'read', return_value={}), \
             mock.patch.object(r.c, 'check_binding'), mock.patch.object(r, 'restore_identity', return_value=self.check()) as gate, \
             mock.patch.object(r.support, 'run_child', side_effect=AssertionError('No child permitted')):
            self.assertEqual(wrapper.main(['--restore-root', str(self.root), '--restored-source', str(self.source)]), 0)
            gate.assert_called_once_with(self.root, self.source)

    def test_missing_explicit_path_native_rejected_before_launch(self):
        with mock.patch.object(r.support, 'run_child', side_effect=AssertionError('No child permitted')):
            with self.assertRaises(ValueError): wrapper.main(['--run-approved'])
            with self.assertRaises(ValueError): wrapper.main(['--restore-root', str(self.root)])

    def test_command_has_only_restored_open_entry(self):
        command = wrapper.native_command(self.root, self.source, self.base)
        self.assertIn('--disable-autoexec', command)
        self.assertIn(str(self.source), command)
        self.assertNotIn(str(r.c.SOURCE), command)
        self.assertEqual(command.count('--python'), 1)
        self.assertEqual(wrapper.TOTAL_SECONDS, 60); self.assertEqual(wrapper.NATIVE_SECONDS, 30)
        self.assertEqual(r.support.MAX_RSS_KIB, 1572864)

    def test_static_probe_reuses_capture_and_validator_no_mutators(self):
        code = (r.HERE / 'probe_restored62.py').read_text(); tree = ast.parse(code)
        calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]
        self.assertIn('native62.capture', calls); self.assertIn('c.validate_raw', calls)
        self.assertEqual(calls.count('bpy.ops.wm.open_mainfile'), 1)
        for name in calls:
            self.assertFalse(any(token in name for token in ('save_as_mainfile', 'save_mainfile', 'rebuild(', 'create_source', 'render.render')))
        self.assertLess(code.index('c.write(rawpath, raw)'), code.index("report['validation'] = c.validate_raw"))
        self.assertIn('Path(bpy.data.filepath) == args.restored_source', code)
        self.assertNotIn('c.SOURCE =', code)

    def test_original_protection_has_no_v2_mutable_exclusions(self):
        with mock.patch.object(r, 'tree_identity', side_effect=lambda p: {'root': str(p), 'canonical': str(r.c.SOURCE)}), \
             mock.patch.object(r, 'no_symlinks', side_effect=lambda p: p), mock.patch.object(r.c, 'sha', return_value='fixture'):
            protection = r.protected_identity()
        self.assertIn(str(r.c.ROOT / 'source-assets'), protection['trees'])
        self.assertIn(str(r.inherited.PROJECT), protection['trees'])
        code = (r.HERE / 'restore_contract62.py').read_text()
        body = code[code.index('def protected_identity():'):code.index('def same_raw(')]
        self.assertNotIn('pop(', body); self.assertNotIn('original.protected_manifest', body)


    def test_same_pid_still_requires_this_launch_pid_binding_and_filepath(self):
        source = (r.HERE / 'run_restore_read62.py').read_text()
        self.assertIn("terminal['pid'] == raw['pid'] == row['pid']", source)
        self.assertIn('support.process_passed(row)', source)
        self.assertIn("terminal['actual_opened_filepath'] == str(args.restored_source)", source)
        self.assertEqual(source.count('row = support.run_child('), 1)
        self.assertNotIn("row['pid'] not in", source)
        # The imported implementation is the unchanged frozen helper, whose
        # new Popen/wait4 binding is checked rather than historical inequality.
        import inspect
        helper = inspect.getsource(r.support.run_child)
        self.assertIn('subprocess.Popen(', helper); self.assertIn('os.wait4(child.pid, flags)', helper)

    def run_fake_probe(self, wrong_path=False):
        out = self.base / 'cloud-evidence' / 'new-read' / 'outputs'; out.mkdir(parents=True)
        raw = dict(pid=os.getpid(), cpu_affinity=[0, 1], fixture='synthetic capture only')
        fake_capture = mock.Mock(return_value=raw)
        fake_open = mock.Mock()
        fake_bpy = types.SimpleNamespace(data=types.SimpleNamespace(filepath=str(self.source) + ('-wrong' if wrong_path else '')),
                                        ops=types.SimpleNamespace(wm=types.SimpleNamespace(open_mainfile=fake_open)))
        original_sha = r.c.sha
        def hash_file(path):
            return r.EXPECTED[r.SOURCE_REL][1] if Path(path) == self.source else original_sha(path)
        def reject_after_raw(saved_raw, binding):
            self.assertEqual(json.loads((out / 'restore-read-raw.json').read_text()), raw)
            partial = json.loads((out / 'restore-read-result.json').read_text())
            self.assertEqual(partial['raw_sha256'], original_sha(out / 'restore-read-raw.json'))
            raise ValueError('Injected pure validation failure after actual raw persistence')
        with mock.patch.dict(sys.modules, bpy=fake_bpy, native62=types.SimpleNamespace(capture=fake_capture)), \
             mock.patch.object(sys, 'argv', ['probe', '--', '--restore-root', str(self.root), '--restored-source', str(self.source), '--out', str(out)]), \
             mock.patch.object(r.c, 'ROOT', self.base), mock.patch.object(r.c, 'SOURCE', self.source), \
             mock.patch.object(r, 'restore_identity', return_value={'fixture': 'unchanged'}), mock.patch.object(r, 'preparation_inputs'), \
             mock.patch.object(r.c, 'read', return_value={}), mock.patch.object(r.c, 'check_binding'), \
             mock.patch.object(r.c, 'sha', side_effect=hash_file), mock.patch.object(r.c, 'validate_raw', side_effect=reject_after_raw):
            with self.assertRaises(ValueError): probe.main()
        fake_open.assert_called_once_with(filepath=str(self.source), load_ui=False, use_scripts=False)
        return out, fake_capture

    def test_raw_preserved_before_failing_native_validation_using_fake_rna(self):
        out, capture = self.run_fake_probe()
        capture.assert_called_once()
        self.assertTrue((out / 'restore-read-raw.json').is_file())
        terminal = json.loads((out / 'restore-read-result.json').read_text())
        self.assertFalse(terminal['passed']); self.assertFalse(terminal['source_saved'])
        self.assertFalse(terminal['rebuild_performed']); self.assertEqual(terminal['images'], 0)

    def test_wrong_actual_opened_filepath_fails_before_capture_using_fake_rna(self):
        out, capture = self.run_fake_probe(wrong_path=True)
        capture.assert_not_called()
        self.assertFalse((out / 'restore-read-raw.json').exists())
        terminal = json.loads((out / 'restore-read-result.json').read_text())
        self.assertFalse(terminal['passed'])
        self.assertEqual(terminal['actual_opened_filepath'], str(self.source) + '-wrong')

    def test_real_raw_validator_and_negative_controls(self):
        # Read actual raw, never copy/restore/open the original .blend.
        raw = r.c.read(r.c.ROOT / r.RAW_REL); binding = r.c.read(r.c.BINDING_PATH)
        r.c.validate_raw(raw, binding)
        for label, mutate in [
            ('shape', lambda x: x['terrain'][0]['vertices'][0].__setitem__(2, x['terrain'][0]['vertices'][0][2] + 1)),
            ('camera', lambda x: x['cameras'][0].__setitem__('lens', x['cameras'][0]['lens'] + 1)),
            ('schema', lambda x: x['terrain'][0]['attribute_schemas'].__setitem__('src_rgba', {'data_type': 'FLOAT', 'domain': 'POINT'})),
            ('embedded text', lambda x: x['embedded_text_sha256'].__setitem__('CONTRACT62.py', '0' * 64)),
        ]:
            changed = copy.deepcopy(raw); mutate(changed)
            with self.subTest(label=label), self.assertRaises((ValueError, KeyError)): r.c.validate_raw(changed, binding)


if __name__ == '__main__':
    unittest.main(verbosity=2)
