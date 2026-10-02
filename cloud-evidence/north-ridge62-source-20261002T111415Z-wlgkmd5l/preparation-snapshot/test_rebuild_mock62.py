"""Reviewer-owned pure author-logic tests; never imports or starts real Blender.

The bpy module, object storage, embedded-text loader and write_mesh are replaced
with Python test doubles. Passing these tests is NOT native mesh/API evidence.
"""
import copy
import sys
import types
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import contract62 as c

fake_bpy = types.ModuleType('bpy')
sys.modules['bpy'] = fake_bpy
import rebuild62 as rebuild


class Vec(list):
    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = float(np.float32(value))


class Object(dict):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.mode = 'OBJECT'
        self.matrix_world = np.eye(4).tolist()


class RebuildAuthorLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binding = c.read(c.HERE / 'bindings62.json')

    def setUp(self):
        self.b = copy.deepcopy(self.binding)
        self.objects = {}
        self.mesh_names = ['R62_MASTER_CONTROL', 'R62_MASTER_EVALUATED'] + [
            'R62_' + name for name in c.TILES
        ]
        for name in self.mesh_names:
            ob = Object(name)
            ob.data = types.SimpleNamespace(is_editmode=False, update=lambda: None)
            self.objects[name] = ob
        self.control = self.objects['R62_MASTER_CONTROL']
        xyz = [[r['xz'][0], r['target_y'], r['xz'][1]] for r in self.b['controls']]
        self.control.data.vertices = [
            types.SimpleNamespace(co=Vec(v)) for v in c.f32(c.local(xyz))
        ]
        for row, vertex in zip(self.b['controls'][12:], self.control.data.vertices[12:]):
            handle = Object('R62_HANDLE_' + row['name'])
            handle.location = Vec(vertex.co)
            handle['last_synced_height'] = float(handle.location.z)
            self.objects[handle.name] = handle
        fake_bpy.data = types.SimpleNamespace(objects=self.objects)
        fake_bpy.context = types.SimpleNamespace(
            scene={}, view_layer=types.SimpleNamespace(update=lambda: None)
        )
        rebuild.modules = lambda: (c, self.b)
        self.writes = []
        rebuild.write_mesh = lambda *args, **kwargs: self.writes.append(args[0].name)
        self.handle = self.objects['R62_HANDLE_' + self.b['controls'][14]['name']]

    def test_initial_is_frozen_and_has_five_derived_writes(self):
        result = rebuild.rebuild(initial=True)
        self.assertEqual(c.digest(result['vertices']), c.digest(c.expected(self.b)['vertices']))
        self.assertEqual(self.writes, self.mesh_names[1:])
        self.assertFalse(fake_bpy.context.scene['edited_after_frozen_build'])

    def test_handle_edit_and_repeat_are_idempotent(self):
        self.handle.location.z += 10
        first = rebuild.rebuild()
        second = rebuild.rebuild()
        self.assertEqual(c.digest(first['vertices']), c.digest(second['vertices']))
        self.assertEqual(self.control.data.vertices[14].co.z, 755)
        self.assertEqual(self.handle.location.z, 755)
        self.assertTrue(fake_bpy.context.scene['edited_after_frozen_build'])
        self.assertFalse(fake_bpy.context.scene['world_integration_allowed'])

    def test_control_and_handle_deltas_add(self):
        self.control.data.vertices[14].co.z += 20
        self.handle.location.z += 5
        rebuild.rebuild()
        self.assertEqual(self.control.data.vertices[14].co.z, 770)
        self.assertEqual(self.handle.location.z, 770)

    def test_boundary_height_rejected_before_write(self):
        self.control.data.vertices[0].co.z += 1
        with self.assertRaisesRegex(ValueError, 'Boundary height locked'):
            rebuild.rebuild()
        self.assertEqual(self.writes, [])

    def test_control_horizontal_edit_rejected_before_write(self):
        self.control.data.vertices[14].co[0] += 1
        with self.assertRaisesRegex(ValueError, 'Control XZ locked'):
            rebuild.rebuild()
        self.assertEqual(self.writes, [])

    def test_handle_horizontal_edit_rejected_before_write(self):
        self.handle.location[0] += 1
        with self.assertRaisesRegex(ValueError, 'Semantic XZ locked'):
            rebuild.rebuild()
        self.assertEqual(self.writes, [])

    def test_all_six_mesh_mode_guards_reject_before_write(self):
        for name in self.mesh_names:
            for field in ['mode', 'is_editmode']:
                with self.subTest(mesh=name, field=field):
                    ob = self.objects[name]
                    ob.mode = 'EDIT' if field == 'mode' else 'OBJECT'
                    ob.data.is_editmode = field == 'is_editmode'
                    with self.assertRaisesRegex(ValueError, 'Exit Edit Mode'):
                        rebuild.rebuild()
                    self.assertEqual(self.writes, [])
                    ob.mode = 'OBJECT'
                    ob.data.is_editmode = False

    def test_all_six_mesh_transform_guards_reject_before_write(self):
        for name in self.mesh_names:
            for field in ['translation', 'scale']:
                with self.subTest(mesh=name, field=field):
                    ob = self.objects[name]
                    ob.matrix_world[0][3 if field == 'translation' else 0] += 1
                    with self.assertRaises(ValueError):
                        rebuild.rebuild()
                    self.assertEqual(self.writes, [])
                    ob.matrix_world = np.eye(4).tolist()


if __name__ == '__main__':
    unittest.main(verbosity=2)
