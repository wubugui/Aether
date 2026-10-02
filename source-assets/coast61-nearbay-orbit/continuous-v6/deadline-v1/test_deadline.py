#!/usr/bin/env python3
"""Pure source-predicate/order and isolated Python acceptance tests; never Godot."""
from __future__ import annotations
import ast
from contextlib import contextmanager
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import sys
import time
import unittest
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ORBIT = HERE.parents[1]
SOURCE = (ORBIT / 'verify_orbit61.gd').read_text()
spec = importlib.util.spec_from_file_location('base_wrapper_tests', HERE.parent / 'test_wrappers.py')
BASE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BASE)

def section(name):
    return SOURCE.split('func '+name+'(', 1)[1].split('\nfunc ', 1)[0]

@contextmanager
def isolated():
    case = BASE.WrapperTests('test_orbit_positive_acceptance_logic_only')
    case.setUp()
    try:
        case.prepare_orbit()
        yield case
    finally:
        case.tearDown()

class DeadlineTests(unittest.TestCase):
    def test_actual_source_predicate_rejects_late_phase_even_with_early_sample(self):
        helper = section('within_wall_deadline')
        condition = re.search(r'^ if (.+): return true$', helper, re.M).group(1)
        self.assertEqual(condition, 'elapsed_msec>=0 and elapsed_msec<=MAX_WALL_SECONDS*1000 and wall_deadline_exceeded_at.is_empty()')
        predicate = compile(ast.parse(condition.replace('wall_deadline_exceeded_at.is_empty()', '(not wall_deadline_exceeded_at)'), mode='eval'), '<GDScript predicate translated only>', 'eval')
        def accepts(elapsed, first):
            return eval(predicate, {'__builtins__': {}}, {'elapsed_msec': elapsed, 'MAX_WALL_SECONDS': 600.0, 'wall_deadline_exceeded_at': first})
        self.assertTrue(accepts(599999, {}))
        self.assertTrue(accepts(600000, {}))  # Original >600 boundary is unchanged.
        for phase in ['audit_after_segment_queries', 'capture_after_image_write', 'capture_after_hash_and_rays',
                      'capture_after_physics', 'finish_after_final_hash_before_pass',
                      'finish_after_final_report_and_sha', 'finish_after_receipt_flush_rename_and_sha', 'finish_before_cleanup']:
            with self.subTest(phase=phase):
                self.assertTrue(accepts(599000, {}))  # Last sample is under600.
                self.assertFalse(accepts(600001, {}))  # Later phase must still fail.
                self.assertFalse(accepts(599999, {'boundary': phase, 'elapsed_msec': 600001}))
        self.assertFalse(accepts(-1, {}))

    def test_source_clock_start_and_limits_are_unchanged_and_not_injectable(self):
        self.assertEqual(SOURCE.count('start_wall=Time.get_ticks_msec()'), 1)
        self.assertTrue(section('run').split('\n')[1].strip() == 'start_wall=Time.get_ticks_msec()')
        self.assertIn('const MAX_WALL_SECONDS := 600.0', SOURCE)
        helper = section('within_wall_deadline')
        self.assertTrue(helper.startswith('boundary: String, completing: bool=false) -> bool:'))
        self.assertIn('var elapsed_msec: int=Time.get_ticks_msec()-start_wall', helper)
        self.assertNotIn('Engine.get_process_frames', helper)
        self.assertIn("default=720", (ORBIT/'run_orbit61.py').read_text())
        self.assertIn('args.wall_timeout <= 720', (ORBIT/'run_orbit61.py').read_text())

    def test_source_audit_capture_and_final_acceptance_order(self):
        audit = section('audit_pending')
        self.assertLess(audit.index('sweep(visual_space'), audit.index('within_wall_deadline("audit_after_segment_queries")'))
        self.assertLess(audit.index('within_wall_deadline("audit_after_segment_queries")'), audit.index('sequence.audit('))
        self.assertLess(audit.index('within_wall_deadline("audit_before_capture_completion")'), audit.index('captured=latest.name'))
        capture = section('after_draw')
        self.assertLess(capture.index('image.save_png'), capture.index('within_wall_deadline("capture_after_image_write")'))
        self.assertLess(capture.index('"nearest_local_rays":local_rays()'), capture.index('within_wall_deadline("capture_after_hash_and_rays")'))
        finish = section('finish')
        self.assertLess(finish.index('FileAccess.get_sha256(path)'), finish.index('within_wall_deadline("finish_after_final_hash_before_pass")'))
        self.assertLess(finish.index('within_wall_deadline("finish_after_final_hash_before_pass")'), finish.index('passed=deadline_ok'))
        self.assertLess(finish.index('report(true)'), finish.index('within_wall_deadline("finish_after_final_report_and_sha",true)'))
        self.assertLess(finish.index('write_completion_receipt(report_sha)'), finish.index('within_wall_deadline("finish_after_receipt_flush_rename_and_sha",true)'))
        self.assertLess(finish.index('within_wall_deadline("finish_before_cleanup",true)'), finish.index('ORBIT61_TERMINAL_WALL '))
        self.assertLess(finish.index('ORBIT61_TERMINAL_WALL '), finish.index('game.queue_free()'))
        self.assertEqual(finish.count('report(true)'), 2)  # Main write plus one conditional failed rewrite.
        self.assertEqual(finish.count('write_completion_receipt(report_sha)'), 2)
        self.assertNotIn('await finish', finish)
        receipt = section('write_completion_receipt')
        self.assertIn('receipt.flush();receipt.close()', receipt)
        self.assertIn('DirAccess.rename_absolute', receipt)
        self.assertNotIn('within_wall_deadline', receipt)  # Caller observes only after return.

    def run_mutation(self, mutate, child_change=None):
        with isolated() as case:
            launch = case.runner.child_run
            def changed(*args):
                process = launch(*args)
                mutate(case.out)
                if child_change: process.update(child_change)
                return process
            case.runner.child_run = changed
            result = case.orbit_run()
            self.assertFalse(result['passed'])
            self.assertFalse(result['first_item_runtime_passed'])
            self.assertTrue(result['input_aftercheck_attempted'])
            return result

    @staticmethod
    def mutate_terminal(out, fn):
        path=out/'renderer.stdout.log'
        record=json.loads(path.read_text().split('ORBIT61_TERMINAL_WALL ',1)[1])
        fn(record)
        path.write_text('ORBIT61_TERMINAL_WALL '+json.dumps(record)+'\n')

    def test_positive_and_exact_600_acceptance_logic_only(self):
        with isolated() as case:
            result=case.orbit_run()
            self.assertTrue(result['passed'])
            self.assertEqual(result['verification_completed_wall_seconds'],591)
        with isolated() as case:
            launch=case.runner.child_run
            def endpoint(*args):
                result=launch(*args)
                def exact(record):
                    w=record['wall_deadline'];w['verification_completed_wall_seconds']=600
                    w['last_check'].update(elapsed_msec=600000,wall_seconds=600)
                self.mutate_terminal(case.out,exact)
                return result
            case.runner.child_run=endpoint
            self.assertTrue(case.orbit_run()['passed'])

    def test_missing_receipt_and_wrong_report_hash_are_rejected(self):
        self.run_mutation(lambda out:(out/'images/orbit-completion.json').unlink())
        self.run_mutation(lambda out:self.mutate_terminal(out,lambda r:r.update(native_report_sha256='0'*64)))
        self.run_mutation(lambda out:(out/'images/orbit-report.json').write_text('{"complete":true,"first_item_runtime_passed":true,"modified":true}'))

    def test_missing_duplicate_malformed_terminal_and_wrong_receipt_hash_rejected(self):
        self.run_mutation(lambda out:(out/'renderer.stdout.log').write_text(''))
        self.run_mutation(lambda out:(out/'renderer.stdout.log').write_text((out/'renderer.stdout.log').read_text()*2))
        self.run_mutation(lambda out:(out/'renderer.stdout.log').write_text('ORBIT61_TERMINAL_WALL {bad}\n'))
        self.run_mutation(lambda out:self.mutate_terminal(out,lambda r:r.update(completion_receipt_sha256='0'*64)))
        self.run_mutation(lambda out:(out/'renderer.stdout.log').write_text((out/'renderer.stdout.log').read_text().replace('{','{"version":"duplicate",',1)))

    def test_negative_nonfinite_nonnumeric_and_over600_terminal_walls_rejected(self):
        for seconds in [-.001,600.001,float('nan'),float('inf'),-float('inf'),'599',True,None]:
            with self.subTest(seconds=repr(seconds)):
                self.run_mutation(lambda out:self.mutate_terminal(out,lambda r:r['wall_deadline'].update(verification_completed_wall_seconds=seconds)))
        self.run_mutation(lambda out:(out/'renderer.stdout.log').write_text((out/'renderer.stdout.log').read_text().replace('591.0','1e999')))

    def test_receipt_invalid_wall_and_terminal_order_rejected(self):
        for seconds in [-1,601,float('nan'),True,None]:
            def mutate(out):
                p=out/'images/orbit-completion.json';r=json.loads(p.read_text())
                r['wall_deadline']['verification_completed_wall_seconds']=seconds;p.write_text(json.dumps(r))
            self.run_mutation(mutate)
        def backwards(record):
            w=record['wall_deadline'];w['verification_completed_wall_seconds']=589
            w['last_check'].update(elapsed_msec=589000,wall_seconds=589)
        self.run_mutation(lambda out:self.mutate_terminal(out,backwards))

    def test_sticky_exceeded_boundary_wrong_limit_and_nonliteral_pass_rejected(self):
        for mutate in [lambda r:r['wall_deadline'].update(first_exceeded_at={'boundary':'capture','elapsed_msec':600001}),
                       lambda r:r['wall_deadline'].update(limit_seconds=720),
                       lambda r:r.update(first_item_runtime_passed='true'),
                       lambda r:r['wall_deadline']['last_check'].update(boundary='process_begin'),
                       lambda r:r['wall_deadline']['last_check'].update(elapsed_msec=True)]:
            self.run_mutation(lambda out:self.mutate_terminal(out,mutate))

    def test_successful_wall_evidence_cannot_override_child_exit_or_timeout(self):
        for change in [{'returncode':1},{'timeout_triggered':True},{'native_exit_observed':False},{'wrapper_received_signal':15}]:
            self.run_mutation(lambda out:None,change)


def main():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(DeadlineTests)
    names=[test.id() for test in suite]
    stream=io.StringIO();began=time.monotonic()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    print(stream.getvalue(),file=sys.stderr)
    sources=[ORBIT/'verify_orbit61.gd',ORBIT/'run_orbit61.py',HERE.parent/'test_wrappers.py',Path(__file__)]
    print(json.dumps({'version':'orbit61-deadline-v1-python-only','passed':result.wasSuccessful(),
       'tests_run':result.testsRun,'test_names':names,'failures':len(result.failures),'errors':len(result.errors),
       'wall_seconds':time.monotonic()-began,'godot_invoked':False,'gdscript_parse_passed':False,
       'native_clock_tested':False,'world_run_passed':False,
       'scope':'Actual source predicate translated for pure logic negatives; source-order assertions; isolated wrapper tests with explicitly synthetic native JSON/stdout. No native clock, GDScript execution, GL or world success.',
       'tested_source_sha256':{str(p.relative_to(ORBIT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}},indent=2))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__': raise SystemExit(main())
