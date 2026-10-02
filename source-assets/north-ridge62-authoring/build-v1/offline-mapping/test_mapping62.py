#!/usr/bin/env python3
"""Offline positive/negative tests only; never loads native applications."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,sys,unittest
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('extract_mapping62',HERE/'extract_mapping62.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestMapping(unittest.TestCase):
 def test_all_current_sources_and_ordered_corners(self):
  summary=m.build(False)
  self.assertEqual(len(summary['meshes']),4)
  self.assertEqual(sum(x['index_count']for x in summary['meshes']),24576)
  self.assertTrue(all(x['survey_ordered_float32_match']for x in summary['meshes']))
 def test_saved_artifacts_and_reverse_mapping(self):
  s=json.loads((HERE/'mapping-summary.json').read_text())
  for fn,pin in s['artifacts'].items():
   raw=(HERE/fn).read_bytes();self.assertEqual(len(raw),pin['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),pin['sha256'])
  for src in s['meshes']:
   d=json.loads(gzip.decompress((HERE/src['mapping_file']).read_bytes()))
   self.assertEqual(len(d['source_vertices']),src['vertex_count'])
   seen=[]
   for v in d['source_vertices']:
    self.assertEqual(v['survey_face_corners'],[[k//3,k%3]for k in v['survey_expanded_corners']])
    for k in v['survey_expanded_corners']:self.assertEqual(d['index_sequence'][k],v['source_vertex']);seen.append(k)
   self.assertEqual(sorted(seen),list(range(src['index_count'])))
 def original(self):return (HERE/'Ground_-4_-7.source-block.tscn.txt').read_bytes()
 def reject(self,b):
  with self.assertRaises((ValueError,IndexError)):m.literals(b,'ArrayMesh_xat5f')
 def test_reject_changed_format(self):self.reject(self.original().replace(b'34896613391',b'34896613407'))
 def test_reject_changed_primitive(self):self.reject(self.original().replace(b'"primitive": 3',b'"primitive": 4'))
 def test_reject_unknown_property(self):self.reject(self.original().replace(b'}]\n',b'}]\nunknown = 2\n'))
 def test_reject_duplicated_surface_field(self):self.reject(self.original().replace(b'"format": 34896613391,',b'"format": 34896613391,\n"format": 34896613391,'))
 def test_reject_bad_base64(self):
  with self.assertRaises(ValueError):m.packed('PackedByteArray("not valid")')
 def test_reject_hidden_trailing(self):self.reject(self.original()+b'script = ExtResource("bad")\n')
 def test_reject_nonzero_uv_scale(self):self.reject(self.original().replace(b'Vector4(0, 0, 0, 0)',b'Vector4(1, 0, 0, 0)'))
if __name__=='__main__':unittest.main(verbosity=2)
