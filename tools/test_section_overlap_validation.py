import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from validate_section_overlap import EXPECTED, validate_section_overlap

class SectionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); (self.root/'assets/models').mkdir(parents=True)
        self.frozen = {}; entries = []
        for name in sorted(EXPECTED):
            content = name.encode(); path = self.root/'assets/models'/f'{name}.glb'; path.write_bytes(content)
            digest = hashlib.sha256(content).hexdigest(); self.frozen['res://assets/models/'+path.name] = {'sha256':digest}
            entries.append({'name':name,'passed':True,'sha256':digest,'invalid_projected_faces':0,'downward_nonfloor_faces':0,'overlapping_projected_roof_area_m2':0.0})
        self.report = {'passed':True,'assets':entries}; self.path = self.root/'report.json'

    def validate(self):
        self.path.write_text(json.dumps(self.report))
        return validate_section_overlap(self.root,self.path,self.frozen)

    def test_exact_frozen_assets_pass(self):
        self.assertEqual(len(self.validate()['asset_sha256']),5)

    def test_failed_report_rejected(self):
        self.report['passed']=False
        with self.assertRaises(ValueError):self.validate()

    def test_failed_asset_rejected(self):
        self.report['assets'][0]['passed']=False
        with self.assertRaises(ValueError):self.validate()

    def test_duplicate_asset_rejected(self):
        self.report['assets'][0]=copy.deepcopy(self.report['assets'][1])
        with self.assertRaises(ValueError):self.validate()

    def test_stale_report_rejected(self):
        self.report['assets'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):self.validate()

    def test_changed_actual_asset_rejected(self):
        name=self.report['assets'][0]['name']; (self.root/'assets/models'/f'{name}.glb').write_bytes(b'changed')
        with self.assertRaises(ValueError):self.validate()

    def test_missing_frozen_asset_rejected(self):
        self.frozen.pop(next(iter(self.frozen)))
        with self.assertRaises(ValueError):self.validate()

if __name__=='__main__':unittest.main()
