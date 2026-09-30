"""Reject partial or invalid physical seating reports without launching a game."""
import copy,unittest
from validation_manifest import validate_rim_rows

class RimContractTests(unittest.TestCase):
    def setUp(self):
        self.inputs={'res://scenes/world/World.tscn':{'sha256':'a'*64}}
        self.report={'passed':True,'world_sha256':'a'*64,'samples':120,
            'assets':[{'name':'cliff_'+name,'passed':True,'contact_edges':3,'samples':20,'misses':0,
                'exposed_samples':0,'minimum_above_terrain_metres':-1.6,'maximum_above_terrain_metres':-1.1}
                for name in ['crown','western_slab','front_columns','central_wall','shadow_buttress','eastern_plateau']]}
    def test_complete_report(self):validate_rim_rows(self.report,self.inputs)
    def test_reject_bad_evidence(self):
        changes=[lambda r:r['assets'].pop(),lambda r:r['assets'][0].update(name='cliff_western_slab'),
            lambda r:r.update(world_sha256='b'*64),lambda r:r.update(samples=119),
            lambda r:r['assets'][0].update(misses=1),lambda r:r['assets'][0].update(exposed_samples=1),
            lambda r:r['assets'][0].update(maximum_above_terrain_metres=.03),
            lambda r:r['assets'][0].update(maximum_above_terrain_metres=float('nan')),
            lambda r:r['assets'][0].update(contact_edges=11)]
        for change in changes:
            with self.subTest(change=change):
                report=copy.deepcopy(self.report);change(report)
                with self.assertRaises(ValueError):validate_rim_rows(report,self.inputs)
if __name__=='__main__':unittest.main()
