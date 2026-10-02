#!/usr/bin/env python3
"""Pure protocol/source tests. No subprocess/native engine or writes."""
import copy,json,sys,unittest
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent)]
import version_schema62 as v
import run_proxy62_v2 as r
import test_proxy62 as original_tests
OriginalMath=original_tests.Math
OriginalProtocol=original_tests.Protocol

class VersionGuard(unittest.TestCase):
    def observation(self,value=None):
        observed=copy.deepcopy(v.EXPECTED_ENGINE if value is None else value)
        return {'engine_version_info':observed,'engine_version_guard':v.engine_guard(observed)}
    def test_known_native_reference_and_old_failure(self):
        p=json.loads((HERE/'provenance.json').read_text());observed=json.loads((r.legacy.AETHER/p['reference_result']).read_text())['engine']
        self.assertEqual(observed,v.EXPECTED_ENGINE);self.assertFalse(observed['string'].startswith('4.5.1.stable.official'))
        self.assertEqual(v.engine_mismatches(observed),[]);self.assertTrue(v.validate_engine_observation(self.observation(observed))['passed']);r.provenance_check()
    def test_each_wrong_value_fails_with_field_diagnostic(self):
        for key,value in v.EXPECTED_ENGINE.items():
            observed=copy.deepcopy(v.EXPECTED_ENGINE);observed[key]=value+1 if type(value)is int else value+'x'
            mismatches=v.engine_mismatches(observed);self.assertEqual(len(mismatches),1);self.assertEqual(mismatches[0]['field'],key);self.assertEqual(mismatches[0]['reason'],'value_mismatch')
            with self.assertRaises(ValueError):v.validate_engine_observation(self.observation(observed))
            self.assertFalse(v.validate_engine_observation(self.observation(observed),False)['passed'])
    def test_each_missing_field_fails(self):
        for key in v.EXPECTED_ENGINE:
            observed=copy.deepcopy(v.EXPECTED_ENGINE);del observed[key]
            self.assertEqual(v.engine_mismatches(observed)[0]['field'],key)
            with self.assertRaises(ValueError):v.validate_engine_observation(self.observation(observed))
    def test_each_wrong_type_rejected(self):
        for key,value in v.EXPECTED_ENGINE.items():
            for wrong in ([float(value),True,str(value),None]if type(value)is int else [7,None,False,[]]):
                observed=copy.deepcopy(v.EXPECTED_ENGINE);observed[key]=wrong
                mismatch=v.engine_mismatches(observed)[0];self.assertEqual(mismatch['field'],key);self.assertEqual(mismatch['reason'],'type_mismatch')
                with self.assertRaises(ValueError):v.validate_engine_observation(self.observation(observed))
    def test_hash_requires_full_exact_commit(self):
        for h in ['f62fdbde','f62fdbde15035c5576dad93e586201f4d41ef0cbx','F62FDBDE15035C5576DAD93E586201F4D41EF0CB','0'*40,'']:
            observed=copy.deepcopy(v.EXPECTED_ENGINE);observed['hash']=h
            with self.assertRaises(ValueError):v.validate_engine_observation(self.observation(observed))
    def test_display_prefix_cannot_override_structured_fields(self):
        observed=copy.deepcopy(v.EXPECTED_ENGINE);observed.update(major=5,hash='0'*40,string='4.5.1.stable.official.anything')
        with self.assertRaises(ValueError):v.validate_engine_observation(self.observation(observed))
        self.assertEqual({x['field']for x in v.engine_mismatches(observed)},{'major','hash','string'})
    def test_unknown_and_non_dictionary_fail(self):
        observed=copy.deepcopy(v.EXPECTED_ENGINE);observed['unreviewed']='extra'
        with self.assertRaises(ValueError):v.validate_engine_observation(self.observation(observed))
        for observed in [None,[],v.EXPECTED_ENGINE['string'],4]:
            with self.assertRaises(ValueError):v.validate_engine_observation({'engine_version_info':observed,'engine_version_guard':v.engine_guard(observed)})
    def test_missing_or_forged_guard_fails(self):
        for action in ['remove_observed','remove_guard','guard_true_int','wrong_expected_float','wrong_policy','wrong_mismatches','old_string_only']:
            d=self.observation()
            if action=='remove_observed':del d['engine_version_info']
            if action=='remove_guard':del d['engine_version_guard']
            if action=='guard_true_int':d['engine_version_guard']['passed']=1
            if action=='wrong_expected_float':d['engine_version_guard']['expected']['major']=4.0
            if action=='wrong_policy':d['engine_version_guard']['policy']='loose'
            if action=='wrong_mismatches':d['engine_version_guard']['mismatches']=[{'field':'x'}]
            if action=='old_string_only':d={'engine_version':'4.5.1.stable.official'}
            with self.assertRaises(ValueError):v.validate_engine_observation(d)
    def test_full_mesh_schema_requires_version_and_retains_old_checks(self):
        case=original_tests.Protocol();case.setUp();native=case.fixture;request=v.request_v2(case.req)
        with self.assertRaises(ValueError):v.validate_native(native,request)
        native.update(self.observation());v.validate_native(native,request)
        wrong_request=copy.deepcopy(request);wrong_request['engine_version_info']['major']=4.0
        with self.assertRaises(ValueError):v.validate_native(native,wrong_request)
        native['visual_meshes'][0]['surfaces']=[]
        with self.assertRaises(ValueError):v.validate_native(native,request)
    def test_request_is_version_only_derivative(self):
        source=json.loads((HERE.parent/'native-request.json').read_text());new=v.request_v2(source);self.assertIn('engine_version',source);self.assertNotIn('engine_version',new)
        for key in set(source)-{'engine_version'}:self.assertEqual(source[key],new[key])
        self.assertEqual((HERE/'native-request-v2.json').read_bytes(),r.old.encode(new))
    def test_source_order_and_unchanged_v1_freeze(self):
        r.source_guards();r.old.freeze_check();self.assertEqual(r.old.digest(HERE.parent/'FINAL_SHA256.json'),r.BASELINE_FREEZE_SHA)

if __name__=='__main__':unittest.main(verbosity=2)
