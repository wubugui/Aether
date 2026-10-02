"""Bounded, read-only Godot 4.5 RSRC format-6 scatter decoder (stdlib only).

No ResourceLoader, scripts, native engine, import/cache work, or source writes.
The supported profile is little-endian, float32, named IDs plus UIDs, no legacy
metadata. Unknown variants/classes/properties and malformed records fail closed.
Packed payloads are represented by their ORIGINAL byte-range hashes, never by a
re-serialized float array. include_buffer returns the main payload only in RAM.

Primary specifications, pinned to Godot 4.5.1-stable:
https://github.com/godotengine/godot/blob/4.5.1-stable/core/io/resource_format_binary.cpp
https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/multimesh.cpp
https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/mesh.cpp

This is saved-data evidence, not native/rendered or occupancy verification.
ArrayMesh AABBs are saved metadata; vertex geometry is deliberately not decoded.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import struct

MAX_FILE_BYTES = 256 * 1024 * 1024
MAX_STRING_BYTES = 1024 * 1024
MAX_ITEMS = 1_000_000
MAX_DEPTH = 32
INVALID_UID = (1 << 64) - 1


class DecodeError(ValueError):
    """Unsupported or malformed saved data; no partial result is successful."""


class _Fixed(dict):
    """JSON-safe tag that cannot be forged by a saved Dictionary Variant."""


class _Packed(dict):
    """JSON-safe packed payload metadata with parser-established provenance."""


class _ResourceRef(dict):
    """JSON-safe reference already range-checked by the binary reader."""


def require(condition, message):
    if not condition:
        raise DecodeError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _finite(values, label):
    require(all(math.isfinite(v) for v in values), 'nonfinite ' + label)


def _int(value, label, minimum=0, maximum=0x7fffffff):
    require(type(value) is int and minimum <= value <= maximum, 'invalid ' + label)
    return value


def _aabb(value, label):
    require(isinstance(value, _Fixed) and value.get('type') == 'AABB', 'invalid ' + label)
    v = value['values']
    require(len(v) == 6 and all(x >= 0 for x in v[3:]), 'negative AABB size: ' + label)
    _finite(v, label)
    _finite([v[i] + v[i + 3] for i in range(3)], label + ' endpoint')
    return v


class _Reader:
    def __init__(self, data):
        require(type(data) is bytes and 4 <= len(data) <= MAX_FILE_BYTES, 'invalid file size/type')
        self.data = data
        self.pos = 0
        self.end = len(data)
        self.names = []
        self.external = []
        self.internal = []
        self.resource_index = -1
        self.variants = 0
        self.kinds = set()

    def take(self, size):
        require(0 <= size <= self.end - self.pos, 'truncated/boundary overflow at byte ' + str(self.pos))
        start = self.pos
        self.pos += size
        return self.data[start:self.pos]

    def read(self, fmt):
        values = struct.unpack('<' + fmt, self.take(struct.calcsize('<' + fmt)))
        return values[0] if len(values) == 1 else values

    def count(self, min_bytes=4):
        n = self.read('I')
        require(n <= MAX_ITEMS and n <= (self.end - self.pos) // min_bytes, 'container count overflow')
        return n

    def string(self, length=None):
        n = self.read('I') if length is None else length
        require(n <= MAX_STRING_BYTES, 'string length overflow')
        raw = self.take(n)
        # Saver emits exactly one terminal NUL; loader also accepts length zero.
        if not n:
            return ''
        require(raw[-1:] == b'\0' and b'\0' not in raw[:-1], 'noncanonical string terminator')
        try:
            return raw[:-1].decode('utf-8', errors='strict')
        except UnicodeDecodeError as exc:
            raise DecodeError('invalid UTF-8 string') from exc

    def named(self):
        index = self.read('I')
        if index & 0x80000000:
            return self.string(index & 0x7fffffff)
        require(index < len(self.names), 'property/name index out of range')
        return self.names[index]

    def variant(self, depth=0):
        require(depth <= MAX_DEPTH, 'variant nesting depth exceeded')
        self.variants += 1
        require(self.variants <= MAX_ITEMS, 'variant budget exceeded')
        kind = self.read('I')
        self.kinds.add(kind)
        if kind == 1:
            return None
        if kind == 2:
            n = self.read('I')
            require(n in (0, 1), 'noncanonical bool')
            return bool(n)
        if kind in (3, 40):
            return self.read('i' if kind == 3 else 'q')
        if kind in (4, 41):
            n = self.read('f' if kind == 4 else 'd')
            _finite([n], 'scalar')
            return n
        if kind in (5, 44):
            return self.string()
        fixed = {10: ('Vector2', 2, 'f'), 11: ('Rect2', 4, 'f'),
                 12: ('Vector3', 3, 'f'), 13: ('Plane', 4, 'f'),
                 14: ('Quaternion', 4, 'f'), 15: ('AABB', 6, 'f'),
                 16: ('Basis', 9, 'f'), 17: ('Transform3D', 12, 'f'),
                 18: ('Transform2D', 6, 'f'), 20: ('Color', 4, 'f'),
                 45: ('Vector2i', 2, 'i'), 46: ('Rect2i', 4, 'i'),
                 47: ('Vector3i', 3, 'i'), 50: ('Vector4', 4, 'f'),
                 51: ('Vector4i', 4, 'i'), 52: ('Projection', 16, 'f')}
        if kind in fixed:
            name, count, code = fixed[kind]
            values = list(self.read(str(count) + code))
            _finite(values, name)
            result = _Fixed(type=name, values=values)
            if kind == 15:
                _aabb(result, 'saved AABB')
            return result
        if kind == 24:
            tag = self.read('I')
            if tag == 0:
                return None
            require(tag in (2, 3), 'unsupported resource reference tag')
            index = self.read('I')
            if tag == 2:
                require(index < len(self.internal), 'internal resource index out of range')
                require(index < self.resource_index, 'forward/self internal resource reference')
                return _ResourceRef(resource_ref='internal', index=index, path=self.internal[index]['path'])
            require(index < len(self.external), 'external resource index out of range')
            return _ResourceRef(self.external[index], resource_ref='external')
        if kind in (26, 30):
            count = self.read('I')
            require(not count & 0x80000000, 'shared container flag unsupported')
            require(count <= MAX_ITEMS and count <= (self.end - self.pos) // (8 if kind == 26 else 4),
                    'container length overflow')
            if kind == 30:
                return [self.variant(depth + 1) for _ in range(count)]
            result = {}
            for _ in range(count):
                key = self.variant(depth + 1)
                require(type(key) is str and key not in result, 'non-string/duplicate dictionary key')
                result[key] = self.variant(depth + 1)
            return result
        if kind == 34:
            return _Packed(packed_type='PackedStringArray', values=[self.string() for _ in range(self.count())])
        packed = {31: ('PackedByteArray', 1, None), 32: ('PackedInt32Array', 4, None),
                  33: ('PackedFloat32Array', 4, 'f'), 35: ('PackedVector3Array', 12, 'f'),
                  36: ('PackedColorArray', 16, 'f'), 37: ('PackedVector2Array', 8, 'f'),
                  48: ('PackedInt64Array', 8, None), 49: ('PackedFloat64Array', 8, 'd'),
                  53: ('PackedVector4Array', 16, 'f')}
        if kind in packed:
            name, size, code = packed[kind]
            count = self.read('I')
            require(count <= MAX_FILE_BYTES // size and count <= (self.end - self.pos) // size,
                    'packed payload length overflow')
            start = self.pos
            payload = self.take(count * size)
            if code:
                require(all(math.isfinite(v[0]) for v in struct.iter_unpack('<' + code, payload)),
                        'nonfinite packed payload')
            if kind == 31:
                require(self.take((-count) % 4) == b'\0' * ((-count) % 4), 'nonzero packed padding')
            return _Packed(packed_type=name, variant_kind=kind, count=count,
                           payload_offset=start, payload_bytes=len(payload),
                           payload_sha256=sha256(payload))
        raise DecodeError('unsupported Variant kind ' + str(kind))

    def parse(self):
        require(self.take(4) == b'RSRC', 'unsupported magic/compression')
        endian, legacy_real64, major, minor, version = self.read('5I')
        require(endian == 0 and legacy_real64 == 0, 'unsupported endian/legacy-real64')
        require(major == 4 and 0 <= minor <= 5 and version == 6, 'unsupported engine/format version')
        main_type = self.string()
        metadata, flags, uid = self.read('QIQ')
        require(metadata == 0, 'legacy metadata unsupported')
        require(flags == 3, 'unsupported flags; named IDs and UIDs required, float32 only')
        require(not any(self.read('11I')), 'nonzero reserved header')
        self.names = [self.string() for _ in range(self.count())]
        require(len(set(self.names)) == len(self.names), 'duplicate string table entry')
        for i in range(self.count(16)):
            typ, path, ext_uid = self.string(), self.string(), self.read('Q')
            require(bool(typ) and bool(path), 'empty external resource type/path')
            # No UID lookup is performed. Non-invalid UID needs caller remap proof.
            self.external.append({'index': i, 'type': typ, 'path': path, 'uid': ext_uid,
                                  'uid_lookup_required': ext_uid != INVALID_UID})
        for i in range(self.count(12)):
            self.internal.append({'index': i, 'path': self.string(), 'offset': self.read('Q')})
        require(bool(self.internal), 'no internal resource records')
        require(len({r['path'] for r in self.internal}) == len(self.internal), 'duplicate internal resource path')
        require(all(r['path'].startswith('local://') and len(r['path']) > 8 for r in self.internal),
                'nonlocal internal resource path')
        require(self.internal[0]['offset'] == self.pos, 'header/record gap or overlap')
        offsets = [r['offset'] for r in self.internal] + [len(self.data) - 4]
        require(all(a < b for a, b in zip(offsets, offsets[1:])), 'unordered/out-of-range record offsets')
        require(self.data[-4:] == b'RSRC', 'invalid suffix marker')
        records = []
        for i, entry in enumerate(self.internal):
            require(self.pos == entry['offset'], 'record offset mismatch')
            self.end = offsets[i + 1]
            self.resource_index = i
            typ = self.string()
            props, provenance = {}, {}
            for _ in range(self.count(8)):
                start = self.pos
                name = self.named()
                require(bool(name) and name not in props, 'empty/duplicate property name')
                variant_start = self.pos
                require(self.end - self.pos >= 4, 'truncated property variant')
                kind = struct.unpack_from('<I', self.data, self.pos)[0]
                props[name] = self.variant()
                provenance[name] = {'property_offset': start, 'variant_offset': variant_start,
                                    'variant_kind': kind, 'end_offset': self.pos}
            require(self.pos == self.end, 'unread/trailing resource record bytes')
            records.append(dict(entry, type=typ, end_offset=self.end,
                                properties=props, property_provenance=provenance))
        require(records[-1]['type'] == main_type, 'main resource class mismatch')
        result = {'source_sha256': sha256(self.data), 'source_bytes': len(self.data),
                  'header': {'engine_version': [major, minor], 'format_version': version,
                             'flags': flags, 'uid': uid, 'main_type': main_type,
                             'metadata_offset': metadata, 'byte_order': 'little', 'real_width': 32},
                  'external_resources': self.external, 'resources': records,
                  'variant_kinds': sorted(self.kinds), 'all_record_boundaries_validated': True}
        _validate_resources(result, self.data)
        return result


_COMMON = {'resource_local_to_scene': (2,), 'resource_name': (5,), 'script': (1, 24)}
_SCHEMAS = {
    'MultiMesh': dict(_COMMON, transform_format=(3,), use_colors=(2,), use_custom_data=(2,),
                      custom_aabb=(15,), instance_count=(3,), visible_instance_count=(3,),
                      mesh=(24,), buffer=(33,), physics_interpolation_quality=(3,)),
    'ArrayMesh': dict(_COMMON, _surfaces=(30,), _blend_shape_names=(34,), blend_shape_mode=(3,),
                     custom_aabb=(15,), shadow_mesh=(24,), lightmap_size_hint=(45,)),
    # This deliberately narrow reviewed material profile has no displacement.
    'StandardMaterial3D': dict(_COMMON, cull_mode=(3,), vertex_color_use_as_albedo=(2,),
                               roughness=(4, 41)),
}
_SURFACE_KEYS = {'format', 'primitive', 'vertex_data', 'vertex_count', 'attribute_data',
                 'skin_data', 'aabb', 'uv_scale', 'index_data', 'index_count', 'lods',
                 'bone_aabbs', 'blend_shapes', 'material', 'name', '2d'}


def _ref_type(value, doc, expected, label, nullable=False):
    if value is None:
        require(nullable, 'missing ' + label)
        return None
    require(isinstance(value, _ResourceRef) and value.get('resource_ref') in ('internal', 'external'),
            'invalid resource reference: ' + label)
    typ = doc['resources'][value['index']]['type'] if value['resource_ref'] == 'internal' else value['type']
    require(typ in expected, 'unsupported resource type for ' + label + ': ' + typ)
    return typ


def _packed(value, label, kind='PackedByteArray'):
    require(isinstance(value, _Packed) and value.get('packed_type') == kind, 'invalid packed ' + label)
    return value


def _validate_surface(s, doc, data):
    require(type(s) is dict and set(s) <= _SURFACE_KEYS, 'unknown ArrayMesh surface property')
    require({'format', 'primitive', 'vertex_data', 'vertex_count', 'aabb'} <= set(s), 'missing surface property')
    fmt = _int(s['format'], 'surface format', maximum=(1 << 63) - 1)
    # 4.5.1 RenderingServer::ArrayFormat: bits0..29 are known flags/custom
    # formats; current version is1 in bits35..42. No legacy conversion here.
    require((fmt >> 35) == 1 and not fmt & ~(((1 << 30) - 1) | (1 << 35)),
            'unsupported ArrayMesh surface format/version')
    require(bool(fmt & 1), 'surface has no vertex format')
    require(bool(fmt & (1 << 12)) == ('index_data' in s), 'surface index flag/payload mismatch')
    _int(s['primitive'], 'surface primitive', maximum=4)
    _int(s['vertex_count'], 'surface vertex_count')
    _aabb(s['aabb'], 'surface AABB')
    for key in ('vertex_data', 'attribute_data', 'skin_data', 'blend_shapes'):
        if key in s:
            _packed(s[key], key)
    require(('index_data' in s) == ('index_count' in s), 'incomplete surface index pair')
    if 'index_count' in s:
        _int(s['index_count'], 'surface index_count')
        _packed(s['index_data'], 'index_data')
        width = 2 if s['vertex_count'] <= 65536 else 4
        require(s['index_data']['count'] == s['index_count'] * width, 'index payload size mismatch')
        _validate_indices(s['index_data'], data, s['vertex_count'], width)
    if 'material' in s:
        _ref_type(s['material'], doc, {'StandardMaterial3D'}, 'surface material', nullable=True)
    if 'name' in s:
        require(type(s['name']) is str, 'invalid surface name')
    if '2d' in s:
        require(type(s['2d']) is bool, 'invalid surface 2d flag')
    if 'uv_scale' in s:
        require(isinstance(s['uv_scale'], _Fixed) and s['uv_scale'].get('type') == 'Vector4', 'invalid uv_scale')
    if 'bone_aabbs' in s:
        require(type(s['bone_aabbs']) is list, 'invalid bone_aabbs')
        for box in s['bone_aabbs']:
            _aabb(box, 'bone AABB')
    if 'lods' in s:
        lods = s['lods']
        require(type(lods) is list and len(lods) % 2 == 0, 'invalid surface lods')
        for edge, packed in zip(lods[::2], lods[1::2]):
            require(type(edge) is float and edge >= 0 and math.isfinite(edge), 'invalid LOD edge')
            _packed(packed, 'lods')
            _validate_indices(packed, data, s['vertex_count'], 2 if s['vertex_count'] <= 65536 else 4)


def _validate_indices(packed, data, vertex_count, width):
    require(packed['payload_bytes'] % width == 0, 'unaligned surface index payload')
    start = packed['payload_offset']
    raw = data[start:start + packed['payload_bytes']]
    require(all(i[0] < vertex_count for i in struct.iter_unpack('<H' if width == 2 else '<I', raw)),
            'surface vertex index out of range')


def _validate_resources(doc, data):
    for ext in doc['external_resources']:
        require(ext['type'] in _SCHEMAS, 'unsupported external resource class ' + ext['type'])
    for r in doc['resources']:
        typ, props = r['type'], r['properties']
        require(typ in _SCHEMAS, 'unsupported resource class ' + typ)
        schema = _SCHEMAS[typ]
        for name in props:
            require(name in schema, 'unknown ' + typ + ' property ' + name)
            require(r['property_provenance'][name]['variant_kind'] in schema[name],
                    'wrong Variant kind for ' + typ + '.' + name)
        require(props.get('script') is None, 'non-null script unsupported')
        require(not props.get('resource_local_to_scene', False), 'local-to-scene resource unsupported')
        if 'custom_aabb' in props:
            _aabb(props['custom_aabb'], 'custom_aabb')
        if typ == 'MultiMesh':
            require(r is doc['resources'][-1], 'nested MultiMesh resource unsupported')
        if typ == 'ArrayMesh':
            surfaces = props.get('_surfaces', [])
            require(type(surfaces) is list and len(surfaces) <= 256, 'invalid ArrayMesh surfaces')
            for surface in surfaces:
                _validate_surface(surface, doc, data)
            require(props.get('blend_shape_mode', 1) in (0, 1), 'invalid blend shape mode')
            if 'shadow_mesh' in props:
                _ref_type(props['shadow_mesh'], doc, {'ArrayMesh'}, 'shadow mesh', nullable=True)
            if 'lightmap_size_hint' in props:
                v = props['lightmap_size_hint']['values']
                require(all(x >= 0 for x in v), 'negative lightmap size')
        if typ == 'StandardMaterial3D':
            require(props.get('cull_mode', 0) in (0, 1, 2), 'invalid cull mode')
            require(0 <= props.get('roughness', 1.0) <= 1, 'invalid roughness')


def parse_rsrc(data):
    """Parse immutable bytes; return JSON-safe metadata for every saved record.

    Does not follow external dependencies or execute classes. Unknown saved
    properties fail even if their class is otherwise supported.
    """
    return _Reader(data).parse()


def _read_bytes(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'not a regular non-symlink resource file')
    require(path.stat().st_size <= MAX_FILE_BYTES, 'file size limit exceeded')
    with path.open('rb') as handle:
        data = handle.read(MAX_FILE_BYTES + 1)
    require(len(data) <= MAX_FILE_BYTES, 'file size limit exceeded during read')
    return data


def read_rsrc(path):
    """Read all supported saved resources, including standalone ArrayMesh files."""
    return parse_rsrc(_read_bytes(path))


def _mesh_summary(ref, doc):
    if ref is None:
        return {'classification': 'missing_mesh', 'saved_properties': None}
    if ref['resource_ref'] == 'external':
        return {'classification': 'external_mesh_requires_separate_saved_read',
                'binding': ref, 'saved_properties': None}
    r = doc['resources'][ref['index']]
    p = r['properties']
    unsupported = []
    if p.get('_blend_shape_names', {}).get('values'):
        unsupported.append('blend_shapes')
    for surface in p.get('_surfaces', []):
        for key in ('skin_data', 'blend_shapes', 'bone_aabbs'):
            if surface.get(key):
                unsupported.append(key)
        if surface.get('2d', False) or surface['format'] & (1 << 25):
            unsupported.append('2d_surface')
    return {'classification': 'unsupported_deforming_mesh' if unsupported else 'saved_arraymesh_metadata_only',
            'unsupported_features': sorted(set(unsupported)), 'binding': ref,
            'resource_index': r['index'], 'resource_path': r['path'],
            'saved_properties': p, 'property_provenance': r['property_provenance'],
            'saved_surface_aabbs': [s['aabb']['values'] for s in p.get('_surfaces', [])],
            'custom_aabb': p.get('custom_aabb', {'type': 'AABB', 'values': [0.0] * 6})['values'],
            'material_references': [s.get('material') for s in p.get('_surfaces', [])],
            'shadow_mesh': p.get('shadow_mesh'), 'vertex_geometry_verified': False}


def decode_multimesh(data, *, include_buffer=False):
    """Decode one saved 3D MultiMesh. Defaults are explicit and provenance-tagged."""
    doc = parse_rsrc(data)
    require(doc['header']['main_type'] == 'MultiMesh', 'main resource is not MultiMesh')
    main = doc['resources'][-1]
    p = main['properties']
    transform_format = p.get('transform_format', 0)
    require(transform_format == 1, 'only TRANSFORM_3D is supported')
    colors, custom = p.get('use_colors', False), p.get('use_custom_data', False)
    count = _int(p.get('instance_count', 0), 'instance_count')
    order = {name: i for i, name in enumerate(p)}
    if count:
        for field in ('transform_format', 'use_colors', 'use_custom_data'):
            if field in p:
                require(order[field] < order['instance_count'], 'layout property saved after allocation')
        for field in ('visible_instance_count', 'buffer'):
            if field in p:
                require(order['instance_count'] < order[field], 'instance property saved before allocation')
    visible = _int(p.get('visible_instance_count', -1), 'visible_instance_count', minimum=-1, maximum=count)
    require(p.get('physics_interpolation_quality', 0) in (0, 1), 'invalid physics interpolation quality')
    mesh = p.get('mesh')
    _ref_type(mesh, doc, {'ArrayMesh'}, 'MultiMesh.mesh', nullable=count == 0)
    stride = 12 + 4 * int(colors) + 4 * int(custom)
    buffer = p.get('buffer')
    if buffer is None:
        require(count == 0, 'nonempty MultiMesh has no saved buffer')
        payload = b''
        offset = None
        floats = 0
    else:
        _packed(buffer, 'MultiMesh buffer', 'PackedFloat32Array')
        floats = buffer['count']
        require(floats == count * stride, 'buffer float count/stride mismatch')
        offset = buffer['payload_offset']
        payload = data[offset:offset + buffer['payload_bytes']]
    defaults = {'transform_format': 0, 'use_colors': False, 'use_custom_data': False,
                'instance_count': 0, 'visible_instance_count': -1, 'custom_aabb': [0.0] * 6}
    result = {'source_sha256': doc['source_sha256'], 'source_bytes': doc['source_bytes'],
              'buffer_sha256': sha256(payload), 'buffer_bytes': len(payload),
              'buffer_float_count': floats, 'buffer_payload_offset': offset,
              'buffer_byte_order': 'little', 'buffer_hash_basis': 'exact_saved_payload_bytes',
              'instance_count': count, 'transform_format': transform_format,
              'use_colors': colors, 'use_custom_data': custom, 'stride_floats': stride,
              'visible_instance_count': visible, 'effective_visible_instance_count': count if visible == -1 else visible,
              'custom_aabb': p.get('custom_aabb', {'values': [0.0] * 6})['values'],
              'mesh': mesh, 'mesh_summary': _mesh_summary(mesh, doc),
              'main_resource_index': main['index'], 'property_provenance': main['property_provenance'],
              'omitted_defaults': {k: v for k, v in defaults.items() if k not in p},
              'resource_provenance': doc, 'godot_invoked': False, 'all_occupancy_complete': False}
    if buffer is None:
        result['buffer_hash_basis'] = 'empty_default_no_saved_payload'
    if include_buffer:
        result['raw_buffer'] = payload
    return result


def read_multimesh(path, *, include_buffer=False):
    """Return exact saved payload facts; include_buffer adds only raw_buffer bytes."""
    return decode_multimesh(_read_bytes(path), include_buffer=include_buffer)
