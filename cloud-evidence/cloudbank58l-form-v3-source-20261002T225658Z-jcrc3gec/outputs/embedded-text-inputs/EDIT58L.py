# Explicit editing only. This Text is not an auto-run module.
import bpy
ns = {"__name__": "l58_embedded_support"}
exec(compile(bpy.data.texts["NATIVE_SUPPORT58L.py"].as_string(), "NATIVE_SUPPORT58L.py", "exec"), ns)
ps = {"__name__": "l58_embedded_topology"}
exec(compile(bpy.data.texts["POLY58K.py"].as_string(), "POLY58K.py", "exec"), ps)
gs = {"__name__": "l58_embedded_geometry", "__file__": "/isolated/source-assets/cloud-bank58/revision-l/form-v3/geometry58l.py", "_EMBEDDED_TOPOLOGY": ps}
exec(compile(bpy.data.texts["GEOMETRY58L.py"].as_string(), "GEOMETRY58L.py", "exec"), gs)
ns2 = {"__name__": "l58_explicit_edit", "_EMBEDDED_SUPPORT": ns, "_EMBEDDED_GEOMETRY": gs}
exec(compile(bpy.data.texts["NATIVE58L.py"].as_string(), "NATIVE58L.py", "exec"), ns2)
ns2["rebuild_from_controls"]()
