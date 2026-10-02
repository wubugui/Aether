"""Bounded pure tests. Uses AST literals to reproduce the rejected v1 conflicts.
No survey rerun, model, engine, source rewrite or network operation.
"""
import argparse,ast,copy,json,sys
from pathlib import Path
import numpy as np
from scipy.interpolate import PPoly
import revise_design_v2 as v

def original_near_arrays(path):
    tree=ast.parse(Path(path).read_text());result={};active=False
    for node in tree.body:
        if not isinstance(node,ast.Assign) or len(node.targets)!=1 or not isinstance(node.targets[0],ast.Name):continue
        key=node.targets[0].id
        try:
            if not isinstance(node.value,ast.Call) or not isinstance(node.value.func,ast.Attribute) or node.value.func.attr!='array':continue
            data=ast.literal_eval(node.value.args[0])
        except (ValueError,TypeError,IndexError):continue
        if key=='s' and data and data[0]==-240:active=True;result['s']=data
        elif active and key in ('top','bottom'):result[key]=data
    v.need(set(result)=={'s','top','bottom'},'OLD_NEAR_AST_SCHEMA')
    return result

def run(ctx,out):
    results=[]
    def test(name,fn):
        fn();results.append({'test':name,'passed':True})
    def must_reject(fn,prefix):
        try:fn()
        except v.Reject as e:v.need(str(e).startswith(prefix),'UNEXPECTED_REJECTION:'+str(e));return str(e)
        raise v.Reject('NEGATIVE_NOT_REJECTED:'+prefix)
    base=ctx['spec'];old=original_near_arrays(ctx['base']/'draw_design_schematics.py')
    def check_ok():
        r,ps,ns=v.validate(ctx);v.need(r['passed'],'VALID_V2_REJECTED');v.need(float(ps['near_A']['top'](0))==ns['A'][1]==1005,'A_AUTHORITY');v.need(np.array_equal(ns['V2'],[4480,740,4070]),'HUB_AUTHORITY')
        near=r['section_audits'][0];v.need(near['endpoint']['external_cell_discrete_lower_m']>117,'INTERNAL_HOLE_NOT_OUTER_EDGE');v.need(near['endpoint']['thickness_m']>=155-1e-9,'END_THICKNESS');v.need(near['guarded_belly_range_m']==[560,625],'NEAR_BELLY_FULL_RANGE')
    test('v2_full_two_section_consistency',check_ok)
    fixture_results=[]
    def design_negative(name,spec,expected):
        r,_,_=v.validate(ctx,spec);v.need(not r['passed'] and all(any(code.startswith(x) for code in r['issues']) for x in expected),'NEGATIVE_CODES:'+name)
        fixture_results.append({'fixture':name,'rejected':True,'observed_issues':r['issues']})
    s=copy.deepcopy(base);s['sections']['near_A']['bottom_y_m']=old['bottom']
    test('R1_reject_actual_v1_bottom_profile',lambda:design_negative('R1_actual_v1',s,['INTERIOR_THICKNESS','INTERIOR_BELLY_RANGE']))
    s2=copy.deepcopy(base);s2['sections']['near_A']['top_y_m']=old['top']
    test('R2_reject_actual_v1_A_height_and_peak',lambda:design_negative('R2_actual_v1',s2,['PROFILE_ANCHOR_DRIFT:near_A:A']))
    s3=copy.deepcopy(base);s3['nodes']['V2_bad']={'base_branch_index':0};s3['branch_valley_nodes'][0]='V2_bad'
    test('R3_reject_actual_v1_branch_junction',lambda:design_negative('R3_actual_v1',s3,['SHARED_JUNCTION_IDENTITY','SHARED_JUNCTION_HEIGHT']))
    both=copy.deepcopy(s3);both['sections']['near_A']['top_y_m']=old['top'];both['sections']['near_A']['bottom_y_m']=old['bottom']
    test('reject_all_three_original_conflicts_together',lambda:design_negative('R1_R2_R3_actual_v1',both,['INTERIOR_THICKNESS','PROFILE_ANCHOR_DRIFT','SHARED_JUNCTION_HEIGHT']))
    drift=copy.deepcopy(base);drift['nodes']['A']={'world_xyz_m':[4140,1006,3910]}
    test('detect_control_drift_against_unchanged_landmarks',lambda:design_negative('control_drift',drift,['CONTROL_LANDMARK_DRIFT:A']))
    belly_drift=copy.deepcopy(base);belly_drift['sections']['near_A']['bottom_y_m'][4]=580
    test('detect_shared_lower_intersection_drift_between_sections',lambda:design_negative('belly_intersection_drift',belly_drift,['PROFILE_BOTTOM_ANCHOR_DRIFT:near_A:A_belly']))
    peak_drift=copy.deepcopy(base);peak_drift['sections']['near_A']['top_y_m'][3]=1010
    test('detect_shifted_peak_even_when_A_anchor_height_is_correct',lambda:design_negative('peak_shift_drift',peak_drift,['PROFILE_CREST_DRIFT:near_A']))

    r,profiles,_=v.validate(ctx);trace=v.line_data(profiles)
    test('accept_resolved_plot_lines',lambda:v.check_plot_trace(trace,profiles))
    bad=copy.deepcopy(trace);bad['near_A']['top'][int(np.argmin(abs(np.array(bad['near_A']['x']))))]-=15
    test('detect_plotted_curve_control_drift',lambda:must_reject(lambda:v.check_plot_trace(bad,profiles),'PLOT_DATA_DRIFT:near_A:top'))
    record=json.loads((Path(out)/'plot-trace.json').read_text())
    test('accept_actual_saved_PNG_metadata_hash_and_artist_trace',lambda:v.check_rendered_receipt(ctx,out,record))
    stale=copy.deepcopy(record);stale['definition_file_sha256']='0'*64
    test('reject_stale_plot_definition_binding',lambda:must_reject(lambda:v.check_rendered_receipt(ctx,out,stale),'STALE_PLOT_DEFINITION'))
    altered=copy.deepcopy(record);altered['images'][0]['sha256']='0'*64
    test('detect_PNG_byte_identity_drift',lambda:must_reject(lambda:v.check_rendered_receipt(ctx,out,altered),'PNG_BYTE_DRIFT'))
    changed=copy.copy(ctx);changed['plan']=copy.deepcopy(ctx['plan']);changed['plan']['form']['interior_min_vertical_thickness_m']=119
    test('reject_weakening_original_120m_gate',lambda:must_reject(lambda:v.validate(changed),'ORIGINAL_GATES_CHANGED'))
    def interior_extremum():
        # f(t)=130 - 80t + 80t^2 has safe endpoints 130 but interior minimum110.
        pp=PPoly(np.array([[0.],[80.],[-80.],[130.]]),np.array([0.,1.]));lo,hi,at,_=v.polynomial_range(pp,0,1);v.need(lo==110 and hi==130 and at==.5,'MISSED_BETWEEN_SAMPLE_MINIMUM')
    test('continuous_polynomial_extremum_detects_endpoint_safe_interior_failure',interior_extremum)
    return {'status':'passed pure offline tests','python_optimized':not __debug__,'test_count':len(results),'tests':results,'actual_v1_literal_fixture':old,'fixture_source_sha256':v.sha(ctx['base']/'draw_design_schematics.py'),'negative_design_fixture_results':fixture_results,'old_v1_pass_rewritten':False,'native_started':False,'scope':'Two defined 1D sections and their plotting/control bindings, not whole candidate mesh or native validation'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--aether-root',required=True);ap.add_argument('--survey-npz',required=True);ap.add_argument('--rendered-dir',required=True);ap.add_argument('--definition',default=str(Path(__file__).parent/'profile-definition.json'));a=ap.parse_args();ctx=v.load_inputs(a.definition,a.aether_root,a.survey_npz);print(json.dumps(run(ctx,a.rendered_dir),indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
