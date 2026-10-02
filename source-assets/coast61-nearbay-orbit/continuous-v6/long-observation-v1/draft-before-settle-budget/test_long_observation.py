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
        self.assertEqual(condition, 'elapsed_msec>=0 and elapsed_msec<=observation_budget_seconds*1000 and wall_deadline_exceeded_at.is_empty()')
        predicate = compile(ast.parse(condition.replace('wall_deadline_exceeded_at.is_empty()', '(not wall_deadline_exceeded_at)'), mode='eval'), '<GDScript predicate translated only>', 'eval')
        def accepts(elapsed, first):
            return eval(predicate, {'__builtins__': {}}, {'elapsed_msec': elapsed, 'observation_budget_seconds': 600, 'wall_deadline_exceeded_at': first})
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
        self.assertIn('validate_budgets(args.observation_budget, args.wall_timeout)', (ORBIT/'run_orbit61.py').read_text())

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


    def test_default600_and_explicit900_configuration(self):
        with isolated() as case:
            for native, outer in [(600, 720), (600, 60), (900, 1020)]:
                case.runner.validate_budgets(native, outer)
            for native in [None, True, False, '900', 900.0, 0, -1, 601, 899, 901, 1200, float('inf')]:
                with self.subTest(native=repr(native)), self.assertRaises(ValueError):
                    case.runner.validate_budgets(native, 1020)
            for native, outer in [(600, 721), (600, 1020), (900, 720), (900, 1019), (900, 1021)]:
                with self.subTest(native=native, outer=outer), self.assertRaises(ValueError):
                    case.runner.validate_budgets(native, outer)
            for outer in [None, True, '1020', 0, -1, float('nan'), float('inf'), -float('inf')]:
                with self.subTest(outer=repr(outer)), self.assertRaises(ValueError):
                    case.runner.validate_budgets(900, outer)
        with isolated() as case:
            case.args.run_renderer=False;case.args.parse_only=True
            case.args.observation_budget=900;case.args.wall_timeout=1020
            self.assertFalse(case.orbit_run()['passed']);self.assertEqual(case.launches,0)
        wrapper=(ORBIT/'run_orbit61.py').read_text()
        self.assertIn("choices=(600, 900), default=600", wrapper)
        self.assertIn("'--wall-timeout', type=float, default=720", wrapper)

    def test_native_budget_admission_before_source_and_world(self):
        init=section('_initialize')
        self.assertIn('value in ["600","900"]', init)
        self.assertIn('observation_budget_valid and budget_arguments==1', init)
        run=section('run')
        self.assertLess(run.index('if not observation_budget_valid:'), run.index('source_hashes='))
        self.assertLess(run.index('if not observation_budget_valid:'), run.index('load(SCENE)'))
        self.assertIn('quit(2);return', run.split('if not observation_budget_valid:',1)[1].split('\n',1)[0])
        # Production predicate translated for source-only exact boundary testing.
        condition=re.search(r'^ if (.+): return true$',section('within_wall_deadline'),re.M).group(1)
        predicate=compile(ast.parse(condition.replace('wall_deadline_exceeded_at.is_empty()', '(not wall_deadline_exceeded_at)'), mode='eval'),'<synthetic predicate only>','eval')
        for msec, allowed in [(600001,True),(899999,True),(900000,True),(900001,False),(-1,False)]:
            self.assertIs(eval(predicate, {'__builtins__': {}}, {'elapsed_msec': msec, 'observation_budget_seconds':900, 'wall_deadline_exceeded_at':{}}), allowed)
        self.assertFalse(eval(predicate, {'__builtins__': {}}, {'elapsed_msec':899999, 'observation_budget_seconds':900, 'wall_deadline_exceeded_at':{'elapsed_msec':900001}}))
        performance=section('strict_600_performance_passed').split(' return ',1)[1].strip()
        self.assertEqual(performance,'passed and not failed and verification_completed_wall_seconds!=null and verification_completed_wall_seconds>=0 and verification_completed_wall_seconds<=MAX_WALL_SECONDS')
        for seconds,passed,failed,expected in [(600,True,False,True),(600.001,True,False,False),(899,True,False,False),(599,False,False,False),(599,True,True,False),(None,True,False,False),(-1,True,False,False)]:
            self.assertIs(eval(performance.replace('null','None'),{'__builtins__':{}},{'passed':passed,'failed':failed,'verification_completed_wall_seconds':seconds,'MAX_WALL_SECONDS':600}),expected)

    def long_case(self, case, receipt_msec=899000, terminal_msec=900000):
        case.args.observation_budget=900
        case.args.wall_timeout=1020
        original=case.runner.child_run
        def launch(command, out, env, timeout, label, observation_budget_seconds):
            self.assertEqual(timeout,1020)
            self.assertEqual(command.count('--observation-budget-seconds=900'),1)
            row=original(command,out,env,timeout,label,observation_budget_seconds)
            report_path=out/'images/orbit-report.json'
            report=json.loads(report_path.read_text());report['requested_observation_budget_seconds']=900;report['wall_deadline']['limit_seconds']=900
            report_path.write_text(json.dumps(report))
            receipt_path=out/'images/orbit-completion.json'
            receipt=json.loads(receipt_path.read_text())
            def alter(record,msec):
                record['requested_observation_budget_seconds']=900
                record['native_report_sha256']=case.support.sha(report_path)
                record['strict_600_performance_passed']=msec<=600000
                wall=record['wall_deadline'];wall['limit_seconds']=900;wall['verification_completed_wall_seconds']=msec/1000
                wall['last_check'].update(elapsed_msec=msec,wall_seconds=msec/1000)
            alter(receipt,receipt_msec);receipt_path.write_text(json.dumps(receipt))
            def terminal(record):
                alter(record,terminal_msec)
                record['completion_receipt_sha256']=case.support.sha(receipt_path)
            self.mutate_terminal(out,terminal)
            return row
        case.runner.child_run=launch

    def test_900_boundary_and_separate_false600_performance(self):
        for msec, allowed in [(600000,True),(600001,True),(899999,True),(900000,True),(900001,False)]:
            with self.subTest(msec=msec), isolated() as case:
                self.long_case(case,receipt_msec=msec-1,terminal_msec=msec)
                result=case.orbit_run()
                self.assertIs(result['passed'],allowed)
                self.assertIs(result['strict_600_performance_passed'],allowed and msec<=600000)
                if allowed:
                    self.assertEqual(result['requested_observation_budget_seconds'],900)
                    self.assertEqual(result['verification_completed_wall_seconds'],msec/1000)
                    self.assertIs(result['native_completion']['terminal']['strict_600_performance_passed'],msec<=600000)

    def test_requested_budget_missing_wrong_or_unsafe_fails_in_all_three_records(self):
        for name in ['report','receipt','terminal']:
            for budget in ['MISSING', None, True, '900', 900.0, 600, 0, -1, 901, float('inf')]:
                with self.subTest(name=name,budget=repr(budget)), isolated() as case:
                    self.long_case(case)
                    old=case.runner.child_run
                    def changed(*args):
                        row=old(*args)
                        path=case.out/('images/orbit-report.json' if name=='report' else 'images/orbit-completion.json')
                        if name=='terminal':
                            self.mutate_terminal(case.out,lambda r:r.pop('requested_observation_budget_seconds') if budget=='MISSING' else r.update(requested_observation_budget_seconds=budget))
                        else:
                            record=json.loads(path.read_text())
                            if budget=='MISSING': record.pop('requested_observation_budget_seconds')
                            else: record['requested_observation_budget_seconds']=budget
                            path.write_text(json.dumps(record))
                            # Rebind both SHA values so rejection tests budget equality, not stale hashes.
                            rp=case.out/'images/orbit-report.json';cp=case.out/'images/orbit-completion.json'
                            receipt=json.loads(cp.read_text());receipt['native_report_sha256']=case.support.sha(rp);cp.write_text(json.dumps(receipt))
                            self.mutate_terminal(case.out,lambda r:r.update(native_report_sha256=case.support.sha(rp),completion_receipt_sha256=case.support.sha(cp)))
                        return row
                    case.runner.child_run=changed
                    self.assertFalse(case.orbit_run()['passed'])
        with isolated() as case:
            case.args.observation_budget=None
            self.assertFalse(case.orbit_run()['passed']);self.assertEqual(case.launches,0)

    def test_false_or_missing_performance_declarations_fail_closed(self):
        for seconds,value in [(800000,True),(600000,False),(800000,None),(800000,'false'),(800000,0),(600000,1)]:
            with self.subTest(seconds=seconds,value=value),isolated() as case:
                self.long_case(case,seconds-1,seconds)
                old=case.runner.child_run
                def changed(*args):
                    row=old(*args);self.mutate_terminal(case.out,lambda r:r.update(strict_600_performance_passed=value));return row
                case.runner.child_run=changed
                self.assertFalse(case.orbit_run()['passed'])

    def test_long_success_cannot_override_exit_source_log_receipt_failures(self):
        for kind in ['exit','timeout','signal','exit_missing','source','log','receipt']:
            with self.subTest(kind=kind),isolated() as case:
                self.long_case(case)
                old=case.runner.child_run
                def changed(*args):
                    row=old(*args)
                    if kind=='exit': row['returncode']=1
                    if kind=='timeout': row['timeout_triggered']=True
                    if kind=='signal': row['wrapper_received_signal']=15
                    if kind=='exit_missing': row['native_exit_observed']=False
                    if kind=='source': case.asset.write_text('changed')
                    if kind=='log': (case.out/'renderer.stderr.log').write_text('ERROR: Synthetic hard failure\n')
                    if kind=='receipt': (case.out/'images/orbit-completion.json').unlink()
                    return row
                case.runner.child_run=changed
                result=case.orbit_run()
                self.assertFalse(result['passed']);self.assertFalse(result['strict_600_performance_passed'])

    def test_mechanical_function_bodies_and_helpers_unchanged(self):
        baseline=ORBIT.parents[1]/'cloud-evidence/nearbay61-orbit-renderer-20261002T070230Z-qx75unzy'
        old=(baseline/'verify_orbit61.gd').read_text()
        for name in ['motion','sample_process','audit_pending','after_draw','capture','wait_settled','wait_event_audited','native_desired','native_target','sweep','local_rays','classify_new_geometry','fixture_sync_snapshot','paused_fixture_unchanged']:
            with self.subTest(name=name):
                self.assertEqual(section(name),old.split('func '+name+'(',1)[1].split('\nfunc ',1)[0])
        for name in ['visible_geometry61.gd','native_sequence61.gd','native_mouse61.gd','orbit_telemetry61.gd','fixture_lifecycle61.gd']:
            with self.subTest(name=name): self.assertEqual((ORBIT/name).read_bytes(),(baseline/name).read_bytes())
        run=section('run');old_run=old.split('func run(',1)[1].split('\nfunc ',1)[0]
        added=' if not observation_budget_valid: push_error("Exactly one explicit observation budget of600 or900 seconds is required");quit(2);return\n'
        self.assertEqual(run.replace(added,''),old_run)
        self.assertIn('root.size=Vector2i(1180,664)',run)
        self.assertIn('const STEP_RADIANS := .05',SOURCE)
        self.assertIn('const SETTLE_METERS := .02',SOURCE)


    def test_shared_launcher_default_and_explicit_cap_with_actual_python_child(self):
        import os
        with isolated() as case:
            with self.assertRaises(ValueError):
                case.support.run_child([sys.executable,'-c','pass'],case.out,os.environ.copy(),case.root,1020,'without-opt-in')
            for cap in [None,True,720.0,900,1021,float('inf')]:
                with self.subTest(cap=repr(cap)),self.assertRaises(ValueError):
                    case.support.run_child([sys.executable,'-c','pass'],case.out,os.environ.copy(),case.root,1,'bad-cap',wall_timeout_limit=cap)
            row=case.support.run_child([sys.executable,'-c','print("actual Python child only")'],case.out,os.environ.copy(),case.root,1020,'explicit-cap-python',wall_timeout_limit=1020)
            self.assertTrue(case.support.process_passed(row));self.assertEqual(row['wall_timeout_seconds'],1020)
            self.assertEqual(len(row['cpu_affinity']),2)
            with self.assertRaises(ChildProcessError): os.waitpid(row['pid'],os.WNOHANG)
            # The main wrapper must actually pass the selected cap through, not just mock it.
            real_runner=BASE.load('actual_child_runner',case.orbit/'run_orbit61.py')
            real_runner.PROJECT=case.root
            row=real_runner.child_run([sys.executable,'-c','pass'],case.out,os.environ.copy(),1020,'main-opt-in-python',900)
            self.assertTrue(case.support.process_passed(row))
            with self.assertRaises(ValueError):
                real_runner.child_run([sys.executable,'-c','pass'],case.out,os.environ.copy(),1020,'main-default-python',600)

    def test_default600_native_argument_is_explicit(self):
        with isolated() as case:
            original=case.runner.child_run
            def launch(command,out,env,timeout,label,budget):
                self.assertEqual(command.count('--observation-budget-seconds=600'),1)
                self.assertEqual(timeout,720);self.assertEqual(budget,600)
                return original(command,out,env,timeout,label,budget)
            case.runner.child_run=launch
            self.assertTrue(case.orbit_run()['strict_600_performance_passed'])


def main():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(DeadlineTests)
    names=[test.id() for test in suite]
    stream=io.StringIO();began=time.monotonic()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    print(stream.getvalue(),file=sys.stderr)
    sources=[ORBIT/'verify_orbit61.gd',ORBIT/'run_orbit61.py',HERE.parent/'wrapper_support.py',HERE.parent/'test_wrappers.py',Path(__file__)]
    print(json.dumps({'version':'orbit61-long-observation-v1-python-only','passed':result.wasSuccessful(),
       'tests_run':result.testsRun,'test_names':names,'failures':len(result.failures),'errors':len(result.errors),
       'wall_seconds':time.monotonic()-began,'godot_invoked':False,'gdscript_parse_passed':False,
       'native_clock_tested':False,'world_run_passed':False,
       'scope':'Actual source predicate translated for pure logic negatives; source-order assertions; isolated wrapper tests with explicitly synthetic native JSON/stdout. No native clock, GDScript execution, GL or world success.',
       'tested_source_sha256':{str(p.relative_to(ORBIT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}},indent=2))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__': raise SystemExit(main())
