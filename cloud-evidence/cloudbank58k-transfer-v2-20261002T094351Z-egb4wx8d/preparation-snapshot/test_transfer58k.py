"""Pure bytes-only tests. No GLB is written and no native executable is launched."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch
import numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_transfer58k as r
t = r.t; c = t.c


def altered_document(blob, mutate):
    size = struct.unpack_from('<I', blob, 12)[0]
    doc = json.loads(blob[20:20+size]); mutate(doc)
    chunk = json.dumps(doc, separators=(',', ':')).encode(); chunk += b' ' * ((-len(chunk)) % 4)
    tail = blob[20+size:]
    return struct.pack('<4sII', b'glTF', 2, 20+len(chunk)+len(tail)) + struct.pack('<I4s', len(chunk), b'JSON') + chunk + tail


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = t.evidence_source(); cls.blob = t.g.FAILED_GLB.read_bytes()
        cls.result, cls.report = t.restore_bytes(cls.blob, cls.source)
        cls.doc, cls.raw, _ = c.parse_glb_bytes(cls.blob)

    def reject(self, fn, *args):
        with self.assertRaises((ValueError, KeyError, IndexError, TypeError, struct.error)):
            fn(*args)

    def test_actual_evidence_and_original_failure_preserved(self):
        self.assertFalse(self.source['original_native_validation_passed'])
        self.assertEqual(self.source['actual_native_normal_sha256'], t.RAW_SHA)
        self.assertEqual(c.sha(t.g.FAILED_GLB), t.g.FAILED_GLB_SHA)
        self.assertEqual(c.sha(c.SOURCE), c.SOURCE_SHA)

    def test_actual_corner_exact_and_original_contract(self):
        self.assertTrue(self.report['passed']); self.assertFalse(self.report['unmodified_official_export'])
        self.assertTrue(self.report['native_corner_values_preserved_exactly'])
        self.assertEqual(self.report['original_geometry_contract']['maximum_position_error_m'], 0)
        self.assertLess(self.report['original_geometry_contract']['maximum_normal_component_error'], 3e-5)
        self.assertEqual(c.NORMAL_EPS, 3e-5); self.assertEqual(c.POSITION_EPS, 1e-5)

    def test_non_normal_bytes_exact(self):
        slots, allowed = t.normal_byte_slots(self.blob, self.doc)
        self.assertEqual(len(slots), 1152); self.assertEqual(len(allowed), 13824)
        self.assertTrue(all(self.blob[i] == self.result[i] for i in range(len(self.blob)) if i not in allowed))
        self.assertNotEqual(self.blob, self.result)

    def test_outside_slot_mutations_rejected(self):
        slots, allowed = t.normal_byte_slots(self.blob, self.doc)
        candidates = [0, 8, 20, slots[0][0] - 1, slots[-1][1], len(self.blob)-1]
        for index in candidates:
            self.assertNotIn(index, allowed)
            altered = bytearray(self.result); altered[index] ^= 1
            self.reject(t.validate_restored_bytes, self.blob, bytes(altered), self.source)

    def test_wrong_normal_slot_values_rejected(self):
        slots, _ = t.normal_byte_slots(self.blob, self.doc)
        for index in [0, 1, 7, 575, 1151]:
            altered = bytearray(self.result); begin, end = slots[index]; altered[begin:end] = struct.pack('<3f', 0, 1, 0)
            self.reject(t.validate_restored_bytes, self.blob, bytes(altered), self.source)
        self.reject(t.validate_restored_bytes, self.blob, self.blob, self.source)

    def test_overlap_and_normal_metadata_rejected(self):
        for mutate in [lambda d: d['bufferViews'][1].update(byteOffset=0), lambda d: d['accessors'][1].update(min=[-1, -1, -1]),
                       lambda d: d['accessors'][1].update(normalized=True), lambda d: d['bufferViews'][1].update(byteStride=8),
                       lambda d: d['accessors'][1].update(byteOffset=1), lambda d: d['accessors'][1].update(count=1151)]:
            doc = deepcopy(self.doc); mutate(doc)
            self.reject(t.normal_byte_slots, self.blob, doc)

    def test_material_and_schema_mutations_rejected(self):
        for mutate in [lambda d: d['materials'][0]['pbrMetallicRoughness'].update(metallicFactor=1),
                       lambda d: d['materials'][0].update(doubleSided=False), lambda d: d['nodes'][0].update(translation=[3958, 0, 3667]),
                       lambda d: d.update(images=[{}])]:
            self.reject(t.restore_bytes, altered_document(self.blob, mutate), self.source)

    def test_triangle_reversal_rejected(self):
        for face in range(384):
            raw = deepcopy(self.raw); start = face * 3
            raw['indices'][start+1], raw['indices'][start+2] = raw['indices'][start+2], raw['indices'][start+1]
            self.reject(t.assigned_normals, raw, self.source)

    def test_actual_corner_and_loop_corruption_rejected(self):
        for mutate in [lambda s: s['corner_normals'][0].__setitem__(0, 0), lambda s: s['corner_normals'][0].__setitem__(0, float('nan')),
                       lambda s: s['polygon_loop_indices'][0].__setitem__(0, 1), lambda s: s['loop_vertex_indices'].__setitem__(0, 1),
                       lambda s: s['loop_polygon_indices'].__setitem__(0, 1), lambda s: s['positions'][0].__setitem__(0, s['positions'][0][0] + .001)]:
            source = deepcopy(self.source); mutate(source)
            self.reject(t.assigned_normals, self.raw, source)

    def test_rounded_raw_tamper_rejected(self):
        slots, _ = t.normal_byte_slots(self.blob, self.doc)
        changed = bytearray(self.blob); begin, end = slots[0]; changed[begin:end] = struct.pack('<3f', 1, 0, 0)
        self.reject(t.restore_bytes, bytes(changed), self.source)

    def test_default_never_creates_output_or_starts_process(self):
        with (patch.object(sys, 'argv', ['run_transfer58k.py']), patch.object(r.tempfile, 'mkdtemp', side_effect=AssertionError('No output')),
              patch.object(r.support, 'run_child', side_effect=AssertionError('No native')), patch.object(t, 'restore_bytes', side_effect=AssertionError('No GLB'))):
            self.assertEqual(r.main(), 0)

    def test_limits_and_no_blender_command(self):
        self.assertEqual(r.TOTAL_SECONDS, 120); self.assertEqual(r.NATIVE_SECONDS, (30, 20, 20)); self.assertEqual(r.support.MAX_RSS_KIB, 1572864)
        script = (t.HERE / 'run_transfer58k.py').read_text()
        self.assertNotIn('c.BLENDER', script); self.assertNotIn('bpy', script)
        self.assertEqual((t.HERE / 'probe58k.gd').read_bytes(), (c.HERE / 'probe58k.gd').read_bytes())
        for path in t.HERE.glob('*.py'):
            ast.parse(path.read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
