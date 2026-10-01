"""Read only uncompressed Godot 4 RSRC MultiMesh main-resource properties.

Format reference: Godot 4.5 core/io/resource_format_binary.{cpp,h}.
This is a bounded binary decoder, not ResourceLoader or an engine invocation.
Unknown types or flags fail explicitly; no scanning for accidental byte patterns.
"""
import struct
import numpy as np

def read_multimesh(path):
    data = path.read_bytes()
    assert data[:4] == b'RSRC', (path, 'Unsupported magic/compression')
    pos = 4
    def read(fmt):
        nonlocal pos
        n = struct.calcsize(fmt)
        result = struct.unpack_from(fmt, data, pos)
        pos += n
        return result[0] if len(result) == 1 else result
    def string():
        nonlocal pos
        n = read('<I')
        assert 0 <= n <= len(data)-pos
        s = data[pos:pos+n]; pos += n
        return s.rstrip(b'\0').decode('utf-8')
    assert read('<I') == 0, 'Big endian unsupported'
    assert read('<I') == 0, 'Legacy real64 unsupported'
    major, minor, version = read('<III')
    assert major == 4 and version <= 6
    assert string() == 'MultiMesh'
    metadata = read('<Q'); flags = read('<I'); uid = read('<Q')
    assert flags & ~3 == 0, (path, 'Unsupported flags', flags)
    assert all(v == 0 for v in read('<11I'))
    names = [string() for _ in range(read('<I'))]
    external = []
    for _ in range(read('<I')):
        t, p = string(), string()
        eu = read('<Q') if flags & 2 else None
        external.append({'type':t, 'path':p, 'uid':eu})
    internal = [(string(), read('<Q')) for _ in range(read('<I'))]
    assert internal and internal[-1][1] < len(data)
    pos = internal[-1][1]
    assert string() == 'MultiMesh'
    def variant():
        nonlocal pos
        kind = read('<I')
        if kind == 1: return None
        if kind == 2: return bool(read('<I'))
        if kind == 3: return read('<i')
        if kind == 4: return read('<f')
        if kind == 5: return string()
        if kind == 15: return list(read('<6f'))
        if kind == 24:
            tag = read('<I')
            if tag == 0: return None
            if tag in (2,3): return {'object_tag':tag, 'index':read('<I')}
            if tag == 1: return {'object_tag':tag, 'type':string(), 'path':string()}
            raise ValueError((path, 'Unknown object tag', tag))
        if kind == 33:
            n = read('<I'); end = pos+n*4
            assert end <= len(data)
            a = np.frombuffer(data[pos:end], dtype='<f4').copy(); pos=end
            return a
        raise ValueError((path, 'Unsupported Variant', kind))
    result = {}
    for _ in range(read('<I')):
        ni = read('<I')
        assert ni < len(names), (path, ni)
        name = names[ni]
        assert name not in result
        result[name] = variant()
    assert data[pos:pos+4] == b'RSRC' and pos+4 == len(data), (path, 'Trailing/unread data', pos,len(data))
    result['_binary'] = {'engine_version':[major,minor], 'format':version, 'flags':flags,'file_bytes':len(data),'external':external, 'main_offset':internal[-1][1]}
    return result
