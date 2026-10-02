#!/usr/bin/env python3
"""Read-only, fail-closed identities for the frozen Game61 dependency review.

No engine, import, cache repair, baseline refresh or source decoding is performed.
The optional project argument supports isolated test copies, not new approvals.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
AETHER = HERE.parents[1]
PROJECT = AETHER / 'candidates/round40-exclusive-20260930/project'
REVIEW = HERE / 'DEPENDENCY_REVIEW.json.gz'
PRIOR = AETHER / 'cloud-evidence/player-nearbay61-renderer-20261001T131646Z-f5163t8s/input-sha256.json'
REVIEW_GZIP_SHA256 = 'e39ef6863849f6034f9c7fb3efeb97a191e39d3cacc9fdab9903692a832fe722'
REVIEW_JSON_SHA256 = '4aa3634f3ec1d1e380d53d724ffa707af4bf66b7136c0bd5fc9592d4d9e80601'
PRIOR_SHA256 = '3329d137d9c43c0fbd2f43f8ca52c4529b8590d891c5fca6fdd376fe3c2b1db9'
AUDITORS = {
    'audit-tools/audit_north62_deps.py': ('graph_source_code', '7efbb80f98581453faaaa6b8c3fc70c0d4747848f1778bb13676d1130ca72f5a'),
    'audit-tools/north62_binary_review.py': ('binary_audit_source_code', 'f89c31a863550f75bc18de17804f1157e843fde1dc096986afac21fcf0fee448'),
}
CONTROL_PATHS = ('project.godot', 'override.cfg', '.godot/global_script_class_cache.cfg',
                 '.godot/extension_list.cfg', '.godot/uid_cache.bin')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError('Dependency guard: ' + message)


def digest(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def canonical_path(project: Path, uri: str) -> Path:
    require(uri.startswith('res://'), 'non-project dependency: ' + uri)
    suffix = uri[6:]
    parts = PurePosixPath(suffix).parts
    require(bool(parts) and not suffix.startswith('/') and '..' not in parts and
            '.' not in parts and str(PurePosixPath(suffix)) == suffix,
            'noncanonical resource path: ' + uri)
    path = project / suffix
    require(path.resolve() == path.absolute(), 'symlinked dependency path: ' + uri)
    return path


def check_identity(path: Path, expected: dict, label: str) -> None:
    # lexists rejects dangling symlinks, including at paths required to be absent.
    if expected.get('exists', True) is False:
        require(not os.path.lexists(path), 'reviewed-absent path appeared: ' + label)
        return
    require(not path.is_symlink() and path.is_file(), 'missing/nonregular file: ' + label)
    require(path.stat().st_size == expected['bytes'], 'byte length changed: ' + label)
    require(digest(path) == expected['sha256'], 'SHA256 changed: ' + label)


def load_review(review_path: Path = REVIEW) -> dict:
    check_identity(review_path, {'bytes': 91486, 'sha256': REVIEW_GZIP_SHA256}, 'frozen review gzip')
    compressed = review_path.read_bytes()
    require(hashlib.sha256(compressed).hexdigest() == REVIEW_GZIP_SHA256, 'review changed while reading')
    raw = gzip.decompress(compressed)
    require(len(raw) == 730050 and hashlib.sha256(raw).hexdigest() == REVIEW_JSON_SHA256,
            'frozen review JSON identity mismatch')
    review = json.loads(raw)
    require(len(review['files']) == 1483, 'reviewed closure count changed')
    require(len(review['prior_manifest_coverage_gap']['not_covered']) == 51, 'reviewed delta count changed')
    facts = review['startup_and_remap_controls']['project_facts']
    require(facts['nonempty_autoload'] is False and
            facts['translation_or_resource_remap_settings_present'] is False and
            facts['global_script_class_cache_text'] == 'list=[]\n' and
            facts['per_dependency_remap_files'] == [] and
            facts['external_resource_valid_uid_declarations'] == 0,
            'unsupported frozen startup/remap claims')
    return review


def validate_dependencies(project: Path = PROJECT, prior: Path = PRIOR,
                          review_path: Path = REVIEW) -> tuple[dict[str, str], dict]:
    """Return pinned input identities and evidence, or raise before an engine starts.

Prior keys retain their original absolute identities, even in an isolated fixture
project. Its original 1477 files remain the runner's separate, unchanged guard.
"""
    review = load_review(review_path)
    require(prior.is_file() and not prior.is_symlink() and digest(prior) == PRIOR_SHA256,
            'historical 1477 manifest identity changed')
    prior_bytes = prior.read_bytes()
    require(hashlib.sha256(prior_bytes).hexdigest() == PRIOR_SHA256, 'prior manifest changed while reading')
    old = json.loads(prior_bytes)
    require(len(old) == 1477, 'historical manifest count changed')
    delta = {uri for uri in review['files'] if str(PROJECT / uri[6:]) not in old}
    require(delta == set(review['prior_manifest_coverage_gap']['not_covered']), 'exact 51-file delta changed')
    for uri, row in review['files'].items():
        prior_sha = old.get(str(PROJECT / uri[6:]))
        require(prior_sha is None or prior_sha == row['sha256'], 'old/review identity conflict: ' + uri)

    identities = {str(review_path): REVIEW_GZIP_SHA256, str(prior): PRIOR_SHA256}
    controls = review['startup_and_remap_controls']
    for relative in CONTROL_PATHS:
        path = canonical_path(project, 'res://' + relative)
        check_identity(path, controls[relative], relative)
        if controls[relative]['exists']:
            identities[str(path)] = controls[relative]['sha256']

    # Pinned settings/cache bytes carry the reviewed no-autoload/no-remap facts.
    # No current content is ever adopted as an approved replacement baseline.
    for uri, row in review['files'].items():
        path = canonical_path(project, uri)
        check_identity(path, row, uri)
        identities[str(path)] = row['sha256']
        for ending in ('.remap', '.import'):
            sidecar_uri = uri + ending
            sidecar = path.with_name(path.name + ending)
            if sidecar_uri not in review['files']:
                require(not os.path.lexists(sidecar), 'unreviewed remap/import sidecar: ' + sidecar_uri)

    for relative, (embedded_key, expected_sha) in AUDITORS.items():
        path = HERE / relative
        require(path.is_file() and digest(path) == expected_sha, 'packaged auditor identity changed: ' + relative)
        require(path.read_text() == review['audit_method'][embedded_key], 'packaged/embedded auditor mismatch: ' + relative)
        identities[str(path)] = expected_sha

    evidence = {
        'status': 'frozen_dependency_identities_verified',
        'review_gzip_sha256': REVIEW_GZIP_SHA256, 'review_json_sha256': REVIEW_JSON_SHA256,
        'reviewed_closure_files': 1483, 'reviewed_closure_bytes': sum(r['bytes'] for r in review['files'].values()),
        'exact_prior_manifest_delta_files': 51, 'prior_manifest_sha256': PRIOR_SHA256,
        'startup_control_identities_verified': list(CONTROL_PATHS),
        'reviewed_absent_controls_still_absent': [p for p in CONTROL_PATHS if not controls[p]['exists']],
        'unreviewed_dependency_remap_or_import_sidecars': [],
        'packaged_auditors_match_frozen_embedded_sources': True,
        'project_autoload_empty': True, 'global_script_class_cache_empty': True,
        'uid_cache_matches_review': True, 'godot_invoked': False,
        'native_parse_passed': False, 'native_collection_passed': False,
        'all_occupancy_complete': False,
    }
    return dict(sorted(identities.items())), evidence


if __name__ == '__main__':
    print(json.dumps(validate_dependencies()[1], indent=2))
