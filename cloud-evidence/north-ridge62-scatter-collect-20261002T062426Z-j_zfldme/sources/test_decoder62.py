"""Synthetic fail-closed parser tests; --actual adds guarded read-only source checks.

Run: python -B test_decoder62.py && python -B -O test_decoder62.py
No engine, subprocess, resource writes, copied buffers, or asserted safety gates.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest

sys.dont_write_bytecode = True
import decoder62 as d


def p(fmt, *values):
    return struct.pack('<' + fmt, *values)


def string(value):
    raw = value.encode('utf-8') + b'\0'
    return p('I', len(raw)) + raw


def v(kind, value=None):
    head = p('I', kind)
    if kind == 1:
        return head
    if kind == 2:
        return head + p('I', value)
    if kind == 3:
        return head + p('i', value)
    if kind == 40:
        return head + p('q', value)
    if kind in (4, 41):
        return head + p('f' if kind == 4 else 'd', value)
    if kind in (5, 44):
        return head + string(value)
    if kind in (15, 50):
        return head + p(str(len(value)) + 'f', *value)
    if kind == 24:
        return head + p('I', value[0]) + (p('I', value[1]) if len(value) > 1 else b'')
    if kind == 26:
        return head + p('I', len(value)) + b''.join(v(5, k) + val for k, val in value)
    if kind == 30:
        return head + p('I', len(value)) + b''.join(value)
    if kind == 31:
        return head + p('I', len(value)) + value + b'\0' * ((-len(value)) % 4)
    if kind == 33:
        return head + p('I', len(value)) + p(str(len(value)) + 'f', *value)
    if kind == 34:
        return head + p('I', len(value)) + b''.join(string(s) for s in value)
    return head


IDENTITY = [1.0, 0.0, 0.0, 3.0, 0.0, 1.0, 0.0, -4.0, 0.0, 0.0, 1.0, 5.0]
EXT = [('ArrayMesh', 'res://assets/meshes/oak.res', d.INVALID_UID)]


def main_props(count=1, colors=False, custom=False, buffer=True):
    props = [('transform_format', v(3, 1))]
    if colors:
        props.append(('use_colors', v(2, True)))
    if custom:
        props.append(('use_custom_data', v(2, True)))
    if count:
        props.append(('instance_count', v(3, count)))
    props.append(('mesh', v(24, (3, 0))))
    if buffer:
        row = IDENTITY + ([0.25, 0.5, 0.75, 1.0] if colors else []) + ([2.0, 3.0, 4.0, 5.0] if custom else [])
        props.append(('buffer', v(33, row * count)))
    props.append(('script', v(1)))
    return props


def blob(records=None, external=None, inline=False, flags=3, version=6, main_type=None):
    records = records if records is not None else [('MultiMesh', main_props())]
    external = EXT if external is None else external
    names = list(dict.fromkeys(k for _, props in records for k, _ in props))
    header = bytearray(b'RSRC' + p('5I', 0, 0, 4, 5, version) + string(main_type or records[-1][0]))
    header += p('QIQ', 0, flags, d.INVALID_UID) + p('11I', *([0] * 11))
    header += p('I', len(names)) + b''.join(string(n) for n in names)
    header += p('I', len(external))
    for typ, path, uid in external:
        header += string(typ) + string(path) + p('Q', uid)
    header += p('I', len(records))
    offset_fields = []
    for i, (typ, _) in enumerate(records):
        header += string('local://' + typ + '_' + str(i))
        offset_fields.append(len(header))
        header += p('Q', 0)
    encoded = []
    offsets = []
    for typ, props in records:
        offsets.append(len(header) + sum(map(len, encoded)))
        body = string(typ) + p('I', len(props))
        for name, value in props:
            raw = name.encode() + b'\0'
            body += (p('I', 0x80000000 | len(raw)) + raw if inline else p('I', names.index(name))) + value
        encoded.append(body)
    for field, offset in zip(offset_fields, offsets):
        struct.pack_into('<Q', header, field, offset)
    return bytes(header) + b''.join(encoded) + b'RSRC', {'offset_fields': offset_fields, 'offsets': offsets}


def replace_prop(props, name, value):
    return [(k, value if k == name else x) for k, x in props]


def surface(**overrides):
    values = {'format': v(40, 34896613377), 'primitive': v(3, 3),
              'vertex_data': v(31, b'\0' * 24), 'vertex_count': v(3, 3),
              'aabb': v(15, [-1, 0, -2, 2, 3, 4]), 'uv_scale': v(50, [0, 0, 0, 0]),
              'index_data': v(31, p('3H', 0, 1, 2)), 'index_count': v(3, 3)}
    values.update(overrides)
    return v(26, list(values.items()))


def internal_blob(surface_value=None, material_props=None, main_extra=()):
    mat = material_props or [('resource_name', v(5, 'pigment')), ('cull_mode', v(3, 2)),
                             ('vertex_color_use_as_albedo', v(2, 1)), ('roughness', v(4, 0.95)), ('script', v(1))]
    shadow = [('ArrayMesh', [('_surfaces', v(30, [surface()])), ('script', v(1))])]
    mesh = [('ArrayMesh', [('_surfaces', v(30, [surface_value or surface(material=v(24, (2, 0)))])),
                           ('shadow_mesh', v(24, (2, 1))), ('script', v(1))])]
    mm = replace_prop(main_props(), 'mesh', v(24, (2, 2))) + list(main_extra)
    return blob([('StandardMaterial3D', mat)] + shadow + mesh + [('MultiMesh', mm)], external=[])[0]


class DecoderTests(unittest.TestCase):
    def reject(self, raw, message=None):
        if message:
            with self.assertRaisesRegex(d.DecodeError, message):
                d.decode_multimesh(raw)
        else:
            with self.assertRaises(d.DecodeError):
                d.decode_multimesh(raw)

    def test_external_exact_bytes_and_defaults(self):
        raw, _ = blob()
        row = d.decode_multimesh(raw, include_buffer=True)
        self.assertEqual(row['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(row['source_bytes'], len(raw))
        payload = p('12f', *IDENTITY)
        self.assertEqual(row['raw_buffer'], payload)
        self.assertEqual(row['buffer_sha256'], hashlib.sha256(payload).hexdigest())
        self.assertEqual(row['buffer_float_count'], 12)
        self.assertEqual(row['stride_floats'], 12)
        self.assertEqual(row['visible_instance_count'], -1)
        self.assertEqual(row['effective_visible_instance_count'], 1)
        self.assertEqual(row['custom_aabb'], [0.0] * 6)
        self.assertEqual(row['mesh']['path'], EXT[0][1])
        self.assertNotIn('raw_buffer', d.decode_multimesh(raw))
        json.dumps(d.decode_multimesh(raw), allow_nan=False)

    def test_strides_and_visibility(self):
        for colors in (False, True):
            for custom in (False, True):
                props = main_props(count=2, colors=colors, custom=custom)
                props.insert(-2, ('visible_instance_count', v(3, 1)))
                props.insert(1, ('custom_aabb', v(15, [-10, -20, -30, 20, 40, 60])))
                row = d.decode_multimesh(blob([('MultiMesh', props)])[0])
                self.assertEqual(row['stride_floats'], 12 + 4 * colors + 4 * custom)
                self.assertEqual(row['buffer_float_count'], 2 * row['stride_floats'])
                self.assertEqual(row['effective_visible_instance_count'], 1)
                self.assertEqual(row['custom_aabb'], [-10, -20, -30, 20, 40, 60])

    def test_saved_empty_and_inline_names(self):
        row = d.decode_multimesh(blob([('MultiMesh', main_props(0, buffer=False))], inline=True)[0])
        self.assertEqual(row['instance_count'], 0)
        self.assertEqual(row['buffer_payload_offset'], None)
        self.assertEqual(row['buffer_hash_basis'], 'empty_default_no_saved_payload')
        self.assertEqual(row['buffer_sha256'], hashlib.sha256(b'').hexdigest())

    def test_internal_mesh_material_shadow_aabb(self):
        row = d.decode_multimesh(internal_blob())
        summary = row['mesh_summary']
        self.assertEqual(summary['saved_surface_aabbs'], [[-1, 0, -2, 2, 3, 4]])
        self.assertEqual(summary['shadow_mesh']['index'], 1)
        self.assertEqual(summary['material_references'][0]['index'], 0)
        self.assertFalse(summary['vertex_geometry_verified'])
        self.assertEqual(len(row['resource_provenance']['resources']), 4)
        json.dumps(row, allow_nan=False)

    def test_every_truncation_and_suffix(self):
        raw, _ = blob()
        for end in range(len(raw)):
            with self.subTest(end=end):
                self.reject(raw[:end])
        self.reject(raw + b'\0')
        self.reject(raw[:-4] + b'FAIL')
        self.reject(b'RSCC' + raw[4:])

    def test_header_format_flags_metadata_endian_reserved(self):
        raw, _ = blob()
        header_tail = 24 + len(string('MultiMesh'))
        for offset, fmt, value in [(4, 'I', 1), (8, 'I', 1), (12, 'I', 5), (16, 'I', 6),
                                   (20, 'I', 7), (header_tail, 'Q', 123),
                                   (header_tail + 8, 'I', 7), (header_tail + 20, 'I', 1)]:
            modified = bytearray(raw)
            struct.pack_into('<' + fmt, modified, offset, value)
            self.reject(bytes(modified))
        self.reject(blob(main_type='ArrayMesh')[0])

    def test_offsets_gap_overlap_out_of_range(self):
        raw, layout = blob()
        for off in (0, layout['offsets'][0] - 1, layout['offsets'][0] + 1, len(raw), 2**64 - 1):
            modified = bytearray(raw)
            struct.pack_into('<Q', modified, layout['offset_fields'][0], off)
            self.reject(bytes(modified))
        raw = internal_blob()
        doc = d.parse_rsrc(raw)
        end = doc['resources'][0]['end_offset']
        self.reject(raw[:end] + b'\0' + raw[end:])

    def test_bad_property_name_and_duplicate(self):
        raw, _ = blob()
        row = d.decode_multimesh(raw)
        off = row['property_provenance']['transform_format']['property_offset']
        modified = bytearray(raw)
        struct.pack_into('<I', modified, off, 0x7fffffff)
        self.reject(bytes(modified))
        props = main_props() + [('script', v(1))]
        self.reject(blob([('MultiMesh', props)])[0], 'duplicate')
        self.reject(blob([('MultiMesh', main_props() + [('mystery', v(1))])])[0], 'unknown')

    def test_wrong_variant_bool_script_or_reference(self):
        for name, value in [('transform_format', v(2, 1)), ('buffer', v(31, b'1234')),
                            ('script', v(24, (3, 0))), ('mesh', v(24, (3, 99))),
                            ('mesh', v(24, (2, 0))), ('mesh', v(24, (1,)))]:
            self.reject(blob([('MultiMesh', replace_prop(main_props(), name, value))])[0])
        self.reject(blob([('MultiMesh', [('use_colors', v(2, 2))] + main_props())])[0])
        self.reject(blob([('MultiMesh', [('resource_local_to_scene', v(2, 1))] + main_props())])[0])
        self.reject(blob([('MultiMesh', main_props())], external=[('Mystery', 'res://x', d.INVALID_UID)])[0])

    def test_count_stride_buffer_nonfinite_and_order(self):
        for name, value in [('instance_count', v(3, -1)), ('instance_count', v(3, 2)),
                            ('buffer', v(33, IDENTITY[:-1])), ('buffer', v(33, IDENTITY + [0])),
                            ('transform_format', v(3, 0)), ('buffer', v(999))]:
            self.reject(blob([('MultiMesh', replace_prop(main_props(), name, value))])[0])
        for bad in (float('inf'), float('-inf'), float('nan')):
            self.reject(blob([('MultiMesh', replace_prop(main_props(), 'buffer', v(33, [bad] + IDENTITY[1:])) )])[0], 'nonfinite')
        self.reject(blob([('MultiMesh', main_props(buffer=False))])[0], 'no saved buffer')
        for visible in (-2, 2):
            self.reject(blob([('MultiMesh', main_props() + [('visible_instance_count', v(3, visible))])])[0])
        props = main_props()
        props[0], props[1] = props[1], props[0]
        self.reject(blob([('MultiMesh', props)])[0], 'after allocation')
        props = main_props()
        props.insert(0, props.pop(-2))
        self.reject(blob([('MultiMesh', props)])[0], 'before allocation')

    def test_string_and_packed_bounds(self):
        raw, _ = blob()
        modified = bytearray(raw)
        struct.pack_into('<I', modified, 24, 0xffffffff)
        self.reject(bytes(modified))
        modified = bytearray(raw)
        modified[28 + len('MultiMesh')] = 1
        self.reject(bytes(modified), 'terminator')
        off = d.decode_multimesh(raw)['property_provenance']['buffer']['variant_offset'] + 4
        modified = bytearray(raw)
        struct.pack_into('<I', modified, off, 0xffffffff)
        self.reject(bytes(modified), 'packed payload length')

    def test_all_internal_properties_checked(self):
        self.reject(internal_blob(material_props=[('mystery', v(3, 1))]), 'unknown StandardMaterial3D')
        self.reject(internal_blob(surface_value=surface(mystery=v(3, 1))), 'unknown ArrayMesh surface')
        self.reject(internal_blob(surface_value=surface(aabb=v(15, [0, 0, 0, -1, 1, 1]))), 'negative AABB')
        self.reject(internal_blob(surface_value=surface(index_data=v(31, p('3H', 0, 1, 3)))), 'index out of range')
        self.reject(internal_blob(surface_value=surface(index_count=v(3, 99))), 'size mismatch')
        self.reject(internal_blob(surface_value=surface(format=v(40, 34896613377 | (1 << 34)))), 'surface format/version')
        self.reject(internal_blob(surface_value=surface(format=v(40, 34896613377 & ~(1 << 12)))), 'index flag')
        self.reject(internal_blob(surface_value=surface(material=v(24, (2, 1)))), 'surface material')

    def test_dictionary_cannot_impersonate_typed_values(self):
        fake_packed = v(26, [('packed_type', v(5, 'PackedByteArray')), ('count', v(3, 24)),
                             ('payload_bytes', v(3, 24)), ('payload_offset', v(3, 0))])
        self.reject(internal_blob(surface_value=surface(vertex_data=fake_packed)), 'invalid packed')
        fake_aabb = v(26, [('type', v(5, 'AABB')), ('values', v(30, [v(4, 0)] * 6))])
        self.reject(internal_blob(surface_value=surface(aabb=fake_aabb)), 'invalid surface AABB')
        fake_ref = v(26, [('resource_ref', v(5, 'internal')), ('index', v(3, 0))])
        self.reject(internal_blob(surface_value=surface(material=fake_ref)), 'invalid resource reference')

    def test_dictionary_duplicate_shared_depth_padding(self):
        duplicate = v(26, [('aabb', v(15, [0, 0, 0, 1, 1, 1])), ('aabb', v(15, [0, 0, 0, 1, 1, 1]))])
        self.reject(internal_blob(surface_value=duplicate), 'duplicate dictionary')
        deep = v(1)
        for _ in range(35):
            deep = v(30, [deep])
        self.reject(blob([('MultiMesh', main_props() + [('mystery', deep)])])[0], 'nesting depth')
        self.reject(blob([('MultiMesh', main_props() + [('mystery', p('2I', 30, 0x80000000))])])[0], 'shared container')
        bad_padding = p('2I', 31, 1) + b'a\1\0\0'
        self.reject(internal_blob(surface_value=surface(vertex_data=bad_padding)), 'padding')


def check_actual():
    """Read exactly the report's708 binaries; verify frozen identities before/after."""
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here.parent))
    import dependency_guard62 as guard
    before, _ = guard.validate_dependencies()
    try:
        report_path = here.parents[2] / 'cloud-evidence/north-ridge62-collect-20261002T053100Z-3mmbw0ol/native-intake.json'
        import gzip
        raw_report = report_path.read_bytes() if report_path.is_file() else gzip.decompress(report_path.with_suffix('.json.gz').read_bytes())
        d.require(hashlib.sha256(raw_report).hexdigest() ==
                  '5d6e5719b9b5f22397338ab508324ec180afd5a1d54554dcb66294ed79e88df2',
                  'pinned native report identity changed')
        report = json.loads(raw_report)
        rows = report['scatter_unresolved']
        d.require(len(rows) == 775, 'pinned report row count changed')
        binary = [r for r in rows if '::' not in r['resource']]
        d.require(len(binary) == 708, 'pinned binary row count changed')
        review = guard.load_review()
        instances = 0
        populated = empty = internal = 0
        identities = []
        for row in binary:
            uri = row['resource']
            path = guard.canonical_path(guard.PROJECT, uri)
            result = d.read_multimesh(path, include_buffer=True)
            expected = review['files'][uri]
            d.require(result['source_sha256'] == expected['sha256'] and result['source_bytes'] == expected['bytes'],
                      'decoder source identity mismatch: ' + uri)
            d.require(hashlib.sha256(result.pop('raw_buffer')).hexdigest() == result['buffer_sha256'],
                      'decoder payload identity mismatch: ' + uri)
            d.require(result['stride_floats'] == 12, 'actual stride changed')
            json.dumps(result, allow_nan=False)
            instances += result['instance_count']
            populated += result['instance_count'] > 0
            empty += result['instance_count'] == 0
            internal += result['mesh']['resource_ref'] == 'internal'
            identities.append([uri, result['source_sha256'], result['buffer_sha256'], result['buffer_float_count']])
        for name in ('oak', 'poplar', 'rock', 'bush', 'pine'):
            resource = d.read_rsrc(guard.PROJECT / ('assets/meshes/' + name + '.res'))
            d.require(resource['header']['main_type'] == 'ArrayMesh', 'actual mesh class mismatch')
        d.require((instances, populated, empty, internal) == (51753, 702, 6, 4), 'actual source summary changed')
        digest = hashlib.sha256(json.dumps(identities, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()
        return {'binary_resources': 708, 'saved_instances': instances, 'populated_resources': populated,
                'empty_resources': empty, 'internal_mesh_resources': internal, 'standalone_mesh_resources': 5,
                'ordered_identity_rows_sha256': digest, 'godot_invoked': False, 'all_occupancy_complete': False}
    finally:
        after, _ = guard.validate_dependencies()
        d.require(after == before, 'immutable dependencies changed during read')


if __name__ == '__main__':
    actual = '--actual' in sys.argv
    args = [x for x in sys.argv if x != '--actual']
    result = unittest.main(argv=args, exit=False).result
    if not result.wasSuccessful():
        raise SystemExit(1)
    if actual:
        print(json.dumps(check_actual(), indent=2))
