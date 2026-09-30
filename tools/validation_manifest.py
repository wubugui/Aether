"""Fail-closed, same-input validation of the real Godot game and Windows pack.

Use validate_demo.ps1, or `inspect` for a read-only dependency audit. The import
and export-preset preparation are logged before freezing imported resources;
the source inventory is also captured before that preparation. Fixed-name
runtime reports are preserved, checked and archived into a unique run folder.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time
import uuid
import zlib

PROVENANCE_PATHS = (
    'scenes/world/World.tscn', 'scenes/prefabs/Airship.tscn',
    'scripts/game.gd', 'scripts/world_math.gd', 'scripts/hud.gd',
    'assets/mountain_kit.json', 'assets/cliff_kit.json', 'assets/road_kit.json',
)
LEGACY = {'assets/open_world.glb', 'assets/world.glb', 'assets/clean_plate.png',
          'assets/reference.jpg', 'assets/world_occluded_color_reference.png'}
TEXT = {'.gd', '.gdshader', '.tscn', '.tres', '.cfg', '.godot', '.json', '.import'}
RESOURCE_TYPES = TEXT | {'.res', '.glb', '.gltf', '.bin', '.png', '.jpg', '.jpeg',
                         '.svg', '.webp', '.ttf', '.otf', '.wav', '.ogg', '.mp3', '.uid'}
ERROR_PATTERN = re.compile(r'SCRIPT ERROR|\bERROR:|Traceback \(most recent call last\)', re.I)
HASH_PATTERN = re.compile(r'^[0-9a-f]{64}$')
EXPECTED_COUNTS = {'game-test': 36, 'packaged-game': 37, 'cliffs-contact': 21,
                   'mountains-contact': 33, 'road-surfaces': 40642,
                   'tour-test': 7, 'stream-test': 4, 'cliff-tour-test': 6, 'geology': 18}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def file_record(path):
    path = Path(path)
    before = path.stat()
    digest = sha256(path)
    after = path.stat()
    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
            f'File changed while hashing: {path}')
    return {'sha256': digest, 'bytes': after.st_size, 'mtime_ns': after.st_mtime_ns}


def dependency_files(root, imported=False):
    """Conservative closure including catalog loads and binary-resource roots.

    Native scene/resource directories and all assets JSON are explicit roots,
    so constructed load paths and binary .res references cannot evade hashing.
    The reference and JSON native_source files are QA inputs, never 3D images.
    """
    root = Path(root).resolve()
    found, pending = set(), []

    def add(path, required=False):
        path = Path(path)
        if not path.is_absolute():
            path = root / path
        path = path.resolve()
        require(path.is_relative_to(root), f'Dependency outside workspace: {path}')
        relative = path.relative_to(root).as_posix()
        if relative.removesuffix('.import') in LEGACY:
            return
        if relative.startswith(('captures/', 'reviews/', 'build/')):
            return
        if relative.startswith('.godot/') and not imported:
            return
        if path.is_file():
            if path not in found:
                found.add(path)
                pending.append(path)
        elif required:
            raise ValueError(f'Missing required dependency: {relative}')

    for item in ['project.godot', 'export_presets.cfg', 'scenes/game.tscn',
                 'assets/airship.glb', 'assets/propeller.glb',
                 'tools/validate_demo.ps1', 'tools/validation_manifest.py',
                 'tools/verify_cliff_flight.gd', 'tools/verify_road_surfaces.gd',
                 'tools/verify_geology_assets.py', 'tools/prepare_windows_export.py',
                 'tools/compare_reference.py']:
        add(item, required=True)
    for folder in ['scenes/world', 'scenes/prefabs', 'scenes/terrain', 'scenes/environment',
                   'scripts', 'materials', 'addons', 'assets']:
        for path in sorted((root / folder).rglob('*')):
            if path.is_file() and path.suffix.lower() in RESOURCE_TYPES:
                add(path)
    for optional_tool in ['tools/verify_cliff_ground_rims.gd', 'tools/verify_native_terrain_material.gd']:
        if (root / optional_tool).is_file():
            add(optional_tool, required=True)
    catalog = read_json(root / 'assets/asset_catalog.json')
    require(isinstance(catalog, list) and catalog, 'Empty or invalid dynamic asset catalog')
    for item in catalog:
        add(f'scenes/prefabs/{item["name"]}.tscn', required=True)
        add(item['path'], required=True)
    for path in (root / '.tools/godot').glob('*.exe'):
        add(path)
    if imported:
        for name in ['global_script_class_cache.cfg', 'uid_cache.bin']:
            add(root / '.godot' / name)
    while pending:
        path = pending.pop()
        if path.suffix.lower() in TEXT:
            content = path.read_text(encoding='utf-8-sig')
            for reference in re.findall(r'["\'](res://[^"\']+)["\']', content):
                target = reference.removeprefix('res://')
                add(target, required=(path.suffix == '.import' and imported
                                      and target.startswith('.godot/imported/')))
            if path.suffix == '.json':
                def visit(value):
                    if isinstance(value, dict):
                        for key, child in value.items():
                            if key in {'path', 'native_source'} and isinstance(child, str):
                                if child.startswith(('assets/', 'blender/', 'scenes/')):
                                    add(child, required=True)
                            visit(child)
                    elif isinstance(value, list):
                        for child in value:
                            visit(child)
                visit(json.loads(content))
        for ending in ['.import', '.uid']:
            sidecar = Path(str(path) + ending)
            if sidecar.is_file():
                add(sidecar)
        if imported and path.relative_to(root).as_posix().startswith('.godot/imported/'):
            # Godot also consults this companion when deciding whether the
            # cached resource is current during a later export/import pass.
            add(path.with_suffix('.md5'))
    reference = root / 'assets/reference.jpg'
    require(reference.is_file(), 'Missing reference for evidence identity')
    found.add(reference)
    return sorted(found)


def snapshot_inputs(root, imported=False):
    root = Path(root).resolve()
    return {'res://' + p.relative_to(root).as_posix(): file_record(p)
            for p in dependency_files(root, imported)}


def input_diff(before, after):
    return {key: {'before': before.get(key), 'after': after.get(key)}
            for key in sorted(before.keys() | after.keys())
            if key not in before or key not in after
            or before[key]['sha256'] != after[key]['sha256']}


def validate_logs(stdout, stderr, exit_code):
    require(exit_code == 0, f'Process exited with code {exit_code}')
    for path in [stdout, stderr]:
        require(Path(path).is_file(), f'Missing process log: {path}')
        match = ERROR_PATTERN.search(Path(path).read_text(encoding='utf-8', errors='replace'))
        require(match is None, f'Engine/script error in {path}: {match.group(0) if match else ""}')


def validate_package_launch(command, cwd, package_directory):
    """Never let a template binary fall back to the host project resources."""
    package_directory = Path(package_directory).resolve()
    arguments = [str(value) for value in command]
    require(Path(cwd).resolve() == package_directory, 'Package stage must use its independent package CWD')
    require(Path(arguments[0]).resolve() == package_directory / 'Aether.exe', 'Unexpected package executable')
    require('--' in arguments, 'Package launch must separate engine and test arguments')
    engine_arguments = arguments[1:arguments.index('--')]
    require('--main-pack' in engine_arguments, 'Package stage requires an explicit --main-pack')
    index = engine_arguments.index('--main-pack')
    require(index + 1 < len(engine_arguments), 'Missing main PCK path')
    pack = Path(engine_arguments[index + 1])
    require(pack.is_absolute() and pack.resolve() == package_directory / 'Aether.pck',
            'Package stage must select this run\'s absolute PCK path')
    require(not any(arg == '--path' or arg.startswith('--path=') for arg in engine_arguments),
            'Package stage cannot select an external project path')


def validate_png(path):
    data = Path(path).read_bytes()
    require(data[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid raw PNG: {path}')
    offset, width, height, compressed, ended = 8, None, None, [], False
    while offset + 12 <= len(data):
        size = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + size]
        require(offset + size + 12 <= len(data), 'Truncated PNG chunk')
        checksum = struct.unpack_from('>I', data, offset + 8 + size)[0]
        require(zlib.crc32(kind + payload) & 0xffffffff == checksum, 'Corrupt PNG chunk')
        if kind == b'IHDR':
            width, height = struct.unpack_from('>II', payload)
        elif kind == b'IDAT':
            compressed.append(payload)
        elif kind == b'IEND':
            ended = True
            require(offset + size + 12 == len(data), 'Unexpected data after PNG end')
        offset += size + 12
    require(ended and (width, height) == (1672, 941) and compressed,
            'Capture must be a complete, unmodified 1672 x 941 PNG')
    require(len(zlib.decompress(b''.join(compressed))) >= height * width * 3,
            'Incomplete PNG pixel data')


def kit_assets(root, *libraries):
    result = {}
    for library in libraries:
        for item in read_json(Path(root) / 'assets' / (library + '.json')):
            require(item['name'] not in result, f'Duplicate kit name: {item["name"]}')
            result[item['name']] = item
    return result


def matching_hash(value, path, inputs):
    key = 'res://' + path.removeprefix('res://')
    require(key in inputs and isinstance(value, str)
            and value.lower() == inputs[key]['sha256'], f'Hash mismatch or untracked input: {path}')


def validate_provenance(report, run_id, inputs, started_ns, finished_ns, package=None):
    provenance = report.get('provenance')
    require(isinstance(provenance, dict), 'Missing report provenance')
    require(provenance.get('run_id') == run_id, 'Report belongs to another run')
    require(provenance.get('packaged') is (package is not None), 'Wrong source/package provenance')
    require(isinstance(provenance.get('engine'), str) and provenance['engine'], 'Missing engine identity')
    try:
        timestamp = datetime.fromisoformat(provenance['utc'].replace('Z', '+00:00'))
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        stamp = timestamp.timestamp()
    except (KeyError, ValueError, TypeError) as error:
        raise ValueError('Invalid provenance UTC timestamp') from error
    require(started_ns // 1_000_000_000 <= stamp <= finished_ns / 1e9 + 1,
            'Provenance timestamp is outside this stage')
    hashes = provenance.get('sha256')
    require(isinstance(hashes, dict) and hashes, 'Missing provenance hashes')
    required = {'res://' + value for value in PROVENANCE_PATHS}
    if package is not None:
        # Godot converts tscn/gd into packed resources. FileAccess cannot expose
        # those original texts, but can hash the exported JSON and EXE/PCK.
        required = {'res://assets/mountain_kit.json'} | set(package)
    normalized = {key.replace('\\', '/'): value for key, value in hashes.items()}
    require(required <= normalized.keys(), 'Incomplete required provenance hash set')
    for key, value in normalized.items():
        require(isinstance(value, str) and HASH_PATTERN.fullmatch(value.lower()),
                f'Invalid SHA256 in provenance: {key}')
        if key.startswith('res://'):
            matching_hash(value, key, inputs)
        else:
            require(package is not None and key in package
                    and value.lower() == package[key]['sha256'], f'Wrong executable/PCK hash: {key}')


def validate_report(name, report, root, run_id, inputs, started_ns, finished_ns, package=None):
    require(isinstance(report, dict) and report.get('passed') is True, f'{name}: passed must be true')
    if name != 'geology':
        validate_provenance(report, run_id, inputs, started_ns, finished_ns, package)
    if name in {'game-test', 'packaged-game', 'cliffs-contact', 'mountains-contact'}:
        checks = report.get('checks')
        require(isinstance(checks, list) and len(checks) == EXPECTED_COUNTS[name],
                f'{name}: expected exactly {EXPECTED_COUNTS[name]} checks')
        require(all(isinstance(check, dict) and check.get('passed') is True for check in checks),
                f'{name}: failed or invalid individual check')
        if name in {'game-test', 'packaged-game'}:
            labels = [check.get('name') for check in checks]
            require(all(isinstance(label, str) and label for label in labels)
                    and len(set(labels)) == len(labels), 'Missing or duplicate game checks')
        else:
            library = 'cliff_kit' if name == 'cliffs-contact' else 'mountain_kit'
            assets = kit_assets(root, library)
            require(Counter(check.get('name') for check in checks)
                    == Counter({key: 3 for key in assets}), 'Incomplete per-asset contact coverage')
            for asset in assets:
                directions = set()
                for check in checks:
                    if check['name'] == asset:
                        directions.add(tuple(float(v) for v in re.findall(
                            r'-?\d+(?:\.\d+)?', check.get('approach', ''))))
                require(directions == {(0., 0., -1.), (1., 0., 0.), (0., 1., 0.)},
                        f'Incorrect front/side/descent coverage: {asset}')
            matching_hash(report.get('world_sha256'), 'scenes/world/World.tscn', inputs)
            matching_hash(report.get('ship_prefab_sha256'), 'scenes/prefabs/Airship.tscn', inputs)
    elif name == 'cliff-ground-rims':
        validate_rim_rows(report, inputs)
    elif name == 'road-surfaces':
        roads = report.get('roads')
        assets = kit_assets(root, 'road_kit')
        require(isinstance(roads, list) and len(roads) == len(assets) == 3, 'Expected exactly three roads')
        require({road.get('name') for road in roads} == set(assets), 'Incomplete road identity set')
        require(report.get('samples') == 40642
                and sum(road.get('sample_count', 0) for road in roads) == 40642,
                'Expected exactly 40642 road surface samples')
        require(report.get('world_unchanged') is True, 'Road test modified world')
        matching_hash(report.get('world_sha256'), 'scenes/world/World.tscn', inputs)
        for road in roads:
            require(road.get('passed') is True and road.get('failed_samples') == 0
                    and road.get('sample_count', 0) > 0 and road['sample_count'] % 7 == 0
                    and 0 <= road.get('maximum_height_error_metres', float('inf')) <= .08,
                    'Failed or empty road interior checks')
            matching_hash(road.get('glb_sha256'), assets[road['name']]['path'], inputs)
    elif name in {'tour-test', 'cliff-tour-test'}:
        require(report.get('waypoints_reached') == EXPECTED_COUNTS[name], 'Wrong completed waypoint count')
        require(isinstance(report.get('samples'), list) and report['samples'], 'Missing physical flight samples')
        require(report.get('health') == 1 and report.get('shield') == 1, 'Tour ended damaged')
        require(report.get('minimum_clearance_metres', -1) > (15 if name == 'tour-test' else 10), 'Insufficient tour clearance')
        require(report.get('distance_metres', -1) > (9000 if name == 'tour-test' else 650), 'Incomplete tour distance')
        if name == 'cliff-tour-test':
            require(report.get('camera_obstruction_samples') == 0, 'Cliff tour camera obstruction')
            matching_hash(report.get('world_sha256'), 'scenes/world/World.tscn', inputs)
    elif name == 'stream-test':
        legs = report.get('legs')
        require(isinstance(legs, list) and len(legs) == 4, 'Expected four streaming flight legs')
        require({leg.get('direction') for leg in legs} == {'east', 'west', 'north', 'south'},
                'Incomplete streaming directions')
        require(report.get('missing_terrain_or_collision_samples') == 0, 'Streaming missed terrain/collision')
        for leg in legs:
            require(leg.get('passed') is True and leg.get('distance_metres', -1) >= 4000
                    and leg.get('missing_terrain_or_collision_samples') == 0
                    and isinstance(leg.get('samples'), list) and leg['samples'], 'Failed or empty streaming leg')
    elif name == 'geology':
        assets = kit_assets(root, 'cliff_kit', 'mountain_kit')
        rows = report.get('assets')
        require(isinstance(rows, list) and len(rows) == len(assets) == 18, 'Expected eighteen geology assets')
        require({row.get('name') for row in rows} == set(assets), 'Incomplete geology asset identities')
        for row in rows:
            require(row.get('passed') is True and row.get('nonmanifold_or_open_edges') == 0
                    and row.get('degenerate_faces') == 0 and row.get('images') == 0
                    and 0 <= row.get('volume_relative_error', float('inf')) < .0001,
                    'Failed exported geology check')
            matching_hash(row.get('glb_sha256'), assets[row['name']]['path'], inputs)
    else:
        raise ValueError(f'No positive report contract for stage: {name}')


def validate_rim_rows(report, inputs):
    names = {'cliff_' + name for name in ('crown', 'western_slab', 'front_columns',
                                        'central_wall', 'shadow_buttress', 'eastern_plateau')}
    rows = report.get('assets')
    require(isinstance(rows, list) and len(rows) == 6 and {r.get('name') for r in rows} == names,
            'Expected all six distinct current cliff contact rims')
    matching_hash(report.get('world_sha256'), 'scenes/world/World.tscn', inputs)
    require(report.get('passed') is True and report.get('samples') == sum(r.get('samples', 0) for r in rows),
            'Rim sample totals or result mismatch')
    for row in rows:
        low, high = row.get('minimum_above_terrain_metres'), row.get('maximum_above_terrain_metres')
        require(row.get('passed') is True and row.get('contact_edges', 0) > 0
                and row.get('samples', 0) >= row['contact_edges'] * 2
                and row.get('misses') == 0 and row.get('exposed_samples') == 0,
                'Empty, missing or exposed ground-rim samples')
        require(all(isinstance(v, (int, float)) and math.isfinite(v) for v in (low, high))
                and low <= high <= .02, 'Invalid or floating contact-rim range')


@contextmanager
def exclusive_lock(path):
    """Protect fixed report sinks from concurrent runs of this pipeline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as handle:
        if handle.tell() == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


class ValidationRun:
    def __init__(self, root, round_name, export_windows=False, capture_views=False):
        self.root = Path(root).resolve()
        self.run_id = round_name + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex
        self.directory = self.root / 'captures/validation_runs' / self.run_id
        self.directory.mkdir(parents=True, exist_ok=False)
        # Prevent later editor/export scans from importing QA PNGs and the pack
        # back into this project or changing UID caches because of our outputs.
        (self.directory / '.gdignore').write_text('# Validation evidence only.\n', encoding='utf-8')
        self.inputs = None
        self.package = None
        self.manifest = {'schema_version': 1, 'run_id': self.run_id, 'round': round_name,
                         'started_utc': utc_now(), 'workspace': str(self.root),
                         'run_directory': str(self.directory), 'status': 'running', 'passed': False,
                         'export_windows_requested': export_windows, 'capture_views_requested': capture_views,
                         'expected_counts': EXPECTED_COUNTS, 'stages': [], 'artifacts': {},
                         'visual_acceptance_proven': False}
        self.save()
        print('VALIDATION RUN ' + str(self.directory), flush=True)

    def save(self):
        write_json(self.directory / 'manifest.json', self.manifest)

    def bind(self, path):
        path = Path(path).resolve()
        require(path.is_relative_to(self.directory), 'Evidence must reside in this unique run directory')
        key = path.relative_to(self.directory).as_posix()
        self.manifest['artifacts'][key] = file_record(path)
        return key

    def assert_inputs(self):
        if self.inputs is not None:
            changes = input_diff(self.inputs, snapshot_inputs(self.root, imported=True))
            if changes:
                difference_report = self.directory / 'input-changes.json'
                write_json(difference_report, changes)
                self.manifest['input_changes'] = self.bind(difference_report)
                raise ValueError('Frozen run dependencies changed: ' + ', '.join(list(changes)[:8]))

    def execute(self, command, stdout, stderr, cwd=None):
        options = {}
        if os.name == 'nt':
            startup = subprocess.STARTUPINFO()
            startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup.wShowWindow = subprocess.SW_HIDE
            options.update(startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW)
        with stdout.open('wb') as out, stderr.open('wb') as err:
            result = subprocess.run([str(value) for value in command], cwd=cwd or self.root,
                                    stdout=out, stderr=err, timeout=1800, **options)
        return result.returncode

    def stage(self, name, command, report=None, image=None, outputs=(), metrics=False, cwd=None):
        require(not any(stage['name'] == name for stage in self.manifest['stages']), 'Duplicate stage name')
        working_directory = Path(cwd or self.root).resolve()
        require(working_directory.is_dir(), 'Missing stage working directory')
        if name in {'packaged-game', 'packaged-opening'}:
            validate_package_launch(command, working_directory, self.directory / 'package')
        self.assert_inputs()
        stdout, stderr = self.directory / (name + '.log'), self.directory / (name + '-error.log')
        if report and Path(report).exists():
            previous = self.directory / 'previous-reports' / (name + '.json')
            previous.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(report, previous)
            self.bind(previous)
        for output in ([image] if image else []) + list(outputs):
            require(not Path(output).exists(), f'Stage output already exists: {output}')
            Path(output).parent.mkdir(parents=True, exist_ok=True)
        stage = {'name': name, 'run_id': self.run_id, 'status': 'running', 'command': [str(v) for v in command],
                 'cwd': str(working_directory),
                 'passed': False, 'started_ns': time.time_ns(), 'started_utc': utc_now(),
                 'input_manifest_sha256': self.manifest['artifacts'].get('inputs.json', {}).get('sha256')}
        self.manifest['stages'].append(stage)
        self.save()
        print('Running ' + name, flush=True)
        try:
            stage['exit_code'] = self.execute(command, stdout, stderr, cwd=working_directory)
            stage['finished_ns'] = time.time_ns()
            # Preserve a fresh producer report even when its process rejects
            # the candidate. Log/exit validation must still fail the stage.
            # A stale sink is kept only under previous-reports, never rebound
            # as evidence from this invocation.
            if report:
                report = Path(report)
                if report.is_file() and report.stat().st_mtime_ns >= stage['started_ns']:
                    destination = self.directory / 'reports' / (name + '.json')
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(report, destination)
                    stage['report'] = self.bind(destination)
            validate_logs(stdout, stderr, stage['exit_code'])
            self.assert_inputs()
            if report:
                require('report' in stage,
                        f'{name}: missing or stale report')
                destination = self.directory / stage['report']
                value = read_json(destination)
                if metrics:
                    require(value.get('round') == self.run_id and value.get('completion_proven') is False,
                            'Reference diagnostic belongs to another run or claims acceptance')
                    require(value.get('size') == [1672, 941], 'Wrong diagnostic image size')
                    require(value.get('render_sha256') == sha256(self.directory / 'images/opening.png'),
                            'Metrics were computed from another opening image')
                    matching_hash(value.get('reference_sha256'), 'assets/reference.jpg', self.inputs)
                else:
                    validate_report(name, value, self.root, self.run_id, self.inputs,
                                    stage['started_ns'], stage['finished_ns'],
                                    self.package if name == 'packaged-game' else None)
                stage['report_contract_passed'] = True
                if name == 'geology':
                    stage['provenance'] = {'run_id': self.run_id, 'method': 'fresh report plus every asset SHA256 and frozen inputs',
                                           'report_mtime_ns': report.stat().st_mtime_ns}
            if image:
                require(Path(image).stat().st_mtime_ns >= stage['started_ns'], 'Stale capture output')
                validate_png(image)
                stage['image'] = self.bind(image)
            for output in outputs:
                require(Path(output).is_file() and Path(output).stat().st_size > 0
                        and Path(output).stat().st_mtime_ns >= stage['started_ns'], 'Missing or stale export output')
                self.bind(output)
            stage['status'] = 'passed'
            stage['passed'] = True
        except Exception as error:
            stage['status'], stage['error'] = 'failed', str(error)
            raise
        finally:
            stage['finished_utc'] = utc_now()
            for path in [stdout, stderr]:
                if path.exists():
                    self.bind(path)
            write_json(self.directory / 'stages' / (name + '.json'), stage)
            self.bind(self.directory / 'stages' / (name + '.json'))
            self.save()

    def run(self):
        engine = self.root / '.tools/godot/Godot_v4.5.1-stable_win64.exe'
        console = self.root / '.tools/godot/Godot_v4.5.1-stable_win64_console.exe'
        windows = self.manifest['export_windows_requested']
        capture_views = self.manifest['capture_views_requested']
        before = snapshot_inputs(self.root, imported=False)
        write_json(self.directory / 'preparation-inputs.json', {'run_id': self.run_id, 'files': before})
        self.bind(self.directory / 'preparation-inputs.json')
        if windows:
            self.stage('prepare-export', [sys.executable, 'tools/prepare_windows_export.py'])
        self.stage('import', [console, '--headless', '--editor', '--path', self.root, '--import', '--quit'])
        after = snapshot_inputs(self.root, imported=False)
        changes = input_diff(before, after)
        allowed = {'res://export_presets.cfg'} if windows else set()
        unexpected = [key for key in changes if key not in allowed and not key.endswith(('.import', '.uid'))]
        self.manifest['preparation_changes'] = changes
        self.save()
        require(not unexpected, 'Source inputs changed during preparation: ' + ', '.join(unexpected[:8]))
        self.inputs = snapshot_inputs(self.root, imported=True)
        frozen_source = {key: value for key, value in self.inputs.items() if not key.startswith('res://.godot/')}
        require(not input_diff(after, frozen_source), 'Source changed while freezing imported dependencies')
        write_json(self.directory / 'inputs.json', {'run_id': self.run_id, 'frozen_utc': utc_now(),
                   'scope': 'Native resource closure, dynamic catalogs, imported remaps, test tools and executable inputs',
                   'files': self.inputs})
        self.bind(self.directory / 'inputs.json')
        self.manifest['input_count'] = len(self.inputs)
        self.save()
        user_run = '--validation-run=' + self.run_id
        views = ['opening', 'mountain-back', 'cliff-back', 'cliff-side', 'reverse'] if capture_views else (['opening'] if windows else [])
        required = {'import', 'game-test', 'tour-test', 'stream-test', 'cliff-tour-test',
                    'cliffs-contact', 'mountains-contact', 'road-surfaces', 'geology'}
        for view in views:
            output = self.directory / 'images' / (view + '.png')
            self.stage('capture-' + view, [engine, '--path', self.root, '--', '--capture',
                       '--view=' + view, '--output=' + str(output), user_run], image=output)
            required.add('capture-' + view)
        if views:
            report = self.root / 'reviews' / ('round-' + self.run_id + '-metrics.json')
            self.stage('reference-metrics', [sys.executable, 'tools/compare_reference.py', '--candidate',
                       self.directory / 'images/opening.png', '--round', self.run_id], report=report, metrics=True)
            required.add('reference-metrics')
        sinks = {'game-test': 'game-validation.json', 'tour-test': 'flight-tour-validation.json',
                 'stream-test': 'stream-flight-validation.json', 'cliff-tour-test': 'cliff-tour-validation.json'}
        for name, sink in sinks.items():
            self.stage(name, [engine, '--path', self.root, '--', '--' + name, user_run],
                       report=self.root / 'captures' / sink)
        for name, mountain in [('cliffs-contact', False), ('mountains-contact', True)]:
            command = [engine, '--path', self.root, '--script', 'tools/verify_cliff_flight.gd', '--', user_run]
            if mountain:
                command.append('--mountain-test')
            sink = 'mountain-flight-validation.json' if mountain else 'cliff-flight-validation.json'
            self.stage(name, command, report=self.root / 'captures' / sink)
        self.stage('road-surfaces', [engine, '--path', self.root, '--script', 'tools/verify_road_surfaces.gd', '--', user_run],
                   report=self.root / 'captures/road-surface-validation.json')
        self.stage('geology', [sys.executable, 'tools/verify_geology_assets.py'],
                   report=self.root / 'captures/geology-asset-validation.json')
        if windows:
            exe, pack = self.directory / 'package/Aether.exe', self.directory / 'package/Aether.pck'
            self.stage('export', [console, '--headless', '--path', self.root, '--export-release', 'Windows Desktop', exe], outputs=[exe, pack])
            self.package = {p.as_posix(): file_record(p) for p in [exe, pack]}
            self.manifest['package'] = self.package
            report = self.directory / 'outputs/packaged-game.json'
            report.parent.mkdir(parents=True, exist_ok=True)
            self.stage('packaged-game', [exe, '--main-pack', pack, '--', '--game-test',
                       '--validation-output=' + str(report), user_run], report=report, cwd=exe.parent)
            output = self.directory / 'images/packaged-opening.png'
            self.stage('packaged-opening', [exe, '--main-pack', pack, '--', '--capture', '--view=opening',
                       '--output=' + str(output), user_run], image=output, cwd=exe.parent)
            require(sha256(output) == sha256(self.directory / 'images/opening.png'), 'This run source/package raw images differ')
            self.manifest['source_package_image_sha256_equal'] = True
            required.update({'prepare-export', 'export', 'packaged-game', 'packaged-opening'})
        self.assert_inputs()
        require({stage['name'] for stage in self.manifest['stages']} == required
                and all(stage['status'] == 'passed' for stage in self.manifest['stages']), 'Incomplete required stage set')
        for path, record in self.manifest['artifacts'].items():
            require(sha256(self.directory / path) == record['sha256'], 'Evidence changed after validation: ' + path)
        self.manifest.update(status='passed', passed=True, completed_utc=utc_now())
        self.save()
        print('Technical validation passed; visual acceptance remains unproven.\n' + str(self.directory / 'manifest.json'), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['run', 'inspect'])
    parser.add_argument('--workspace', default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--round', default='current')
    parser.add_argument('--export-windows', action='store_true')
    parser.add_argument('--capture-views', action='store_true')
    args = parser.parse_args()
    require(re.fullmatch(r'[a-zA-Z0-9_-]+', args.round), 'Unsafe round label')
    root = Path(args.workspace).resolve()
    if args.action == 'inspect':
        files = snapshot_inputs(root, imported=True)
        print(json.dumps({'read_only': True, 'files': len(files),
                          'bytes': sum(record['bytes'] for record in files.values()),
                          'imported_resources': sum(key.startswith('res://.godot/imported/') for key in files)}, indent=2))
        return
    with exclusive_lock(root / 'captures/.validation-pipeline.lock'):
        run = ValidationRun(root, args.round, args.export_windows, args.capture_views)
        try:
            run.run()
        except Exception as error:
            run.manifest.update(status='failed', passed=False, error=str(error), completed_utc=utc_now())
            run.save()
            print('VALIDATION FAILED: ' + str(error) + '\n' + str(run.directory / 'manifest.json'), file=sys.stderr)
            raise


if __name__ == '__main__':
    main()
