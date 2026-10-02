"""Pure check of the final trial source freeze; starts no native process."""
import ast
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import run_world58k as runner
import provenance58k as p


def check():
    frozen = runner.preparation()
    for path in p.HERE.glob('*.py'):
        ast.parse(path.read_text())
    for path in p.HERE.iterdir():
        runner.require(path.suffix not in ('.blend','.glb','.scn','.tscn','.png','.jpg'),'Source-only preparation must contain no generated native asset or image')
    runner.require(not list(p.HERE.glob('*-attempt.json')) and not list(p.HERE.glob('*-terminal.json')),'No native attempt is claimed in source preparation')
    runner.require(p.sha(p.NATIVE/'roundtrip.tscn') == runner.NATIVE_SHA,'Original native K asset remains exact')
    actual = runner.original.file_manifest(p.PROJECT)
    previous = json.loads((p.NATIVE/'main-project-after.json').read_text())
    runner.require(actual == previous,'Entire main project unchanged from accepted native v3 protection manifest')
    runner.require(runner.support.MAX_RSS_KIB == runner.LIMITS['maximum_aggregate_rss_kib'] == 3145728,'Explicit independent 3 GiB world budget')
    plan = json.loads((p.HERE/'placement-provenance.json').read_text())
    return dict(passed=True, frozen_file_count=len(frozen['files']), main_project_file_count=len(actual),
        main_project_unchanged=True, accepted_native_sha256=runner.NATIVE_SHA,
        engine_started=False, native_parse_passed=False, world_loaded=False, images=0,
        selected_root=plan['selected_root'], independent_layout_choice=True,
        original_front_unoccluded_centroid_sample_count=plan['original_front_projected_k']['clear_centroid_samples_after_single_replacement'],
        pixel_coverage_proven=False, visual_acceptance=False, limits=runner.LIMITS)


if __name__ == '__main__':
    print(json.dumps(check(),indent=2,allow_nan=False))
