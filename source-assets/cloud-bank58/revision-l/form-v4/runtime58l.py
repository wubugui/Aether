"""Pinned runtime and scoped imports of unchanged historical validators; inert on import."""
from __future__ import annotations
import contextlib, importlib, sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PYTHON = ROOT.parent / 'tools-feiting/blender-4.5.14-linux-x64/4.5/python/bin/python3.11'
PYTHON_SHA = '60b08089c60cbe81827b135c8fd9e206ba2ee6bf54aa1dbd0d6f56ac2d5914f6'
PYTHON_VERSION = '3.11.15 (main, Apr 25 2025, 12:39:20) [GCC 11.2.1 20220127 (Red Hat 11.2.1-9)]'
VERSION = 'cloudbank58l-form-v4'
# New-environment budget only; historical source/views retain their original 120s.
SOURCE_BUDGET = dict(total_wall_seconds=180, finalization_reserve_seconds=60)
PUBLISHED_PREDECESSOR = '7c52378d53bc6c1e79339b4ec869061d398d3e53'
PUBLISHED_RECOVERY = '31d3e0d0e5f71ad00cdbaa4a045c412d4d6f2d7b'
_NAMES = ('geometry58l', 'native_support58l', 'native58l', 'diagnostic58l', 'run58l_form_v2', 'recovery58l', 'views58l')

@contextlib.contextmanager
def legacy():
    """Retain old module globals and dynamic imports during old read-only checks.

    Restore every colliding module/path on exit. Never alter original files or
    monkeypatch their validation functions. Shared v3 supervision stays shared.
    """
    saved = {name: sys.modules.get(name) for name in _NAMES}
    old_path = sys.path[:]
    try:
        for name in _NAMES: sys.modules.pop(name, None)
        sys.path[:0] = [str(HERE.parent / p) for p in ('form-v2-views-v1', 'form-v2-recovery-v1', 'form-v2')]
        views = importlib.import_module('views58l')
        yield views.recovery, views
    finally:
        for name in _NAMES:
            sys.modules.pop(name, None)
            if saved[name] is not None: sys.modules[name] = saved[name]
        sys.path[:] = old_path

def runtime(native_process=False):
    import hashlib, numpy
    from native_support58l import require
    require(sys.version == PYTHON_VERSION, 'Exact official bundled Python 3.11.15 runtime')
    require(PYTHON.is_file() and not PYTHON.is_symlink(), 'Pinned real official Python executable')
    with PYTHON.open('rb') as f: actual = hashlib.file_digest(f, 'sha256').hexdigest()
    require(actual == PYTHON_SHA, 'Pinned official Python executable SHA')
    if not native_process:
        require(Path(sys.executable).resolve() == PYTHON.resolve(), 'Wrapper and observer use pinned Python')
    require(numpy.__version__ == '1.26.4' and Path(numpy.__file__).resolve().is_relative_to(PYTHON.parents[1]),
            'Official bundled NumPy dependency')
    return dict(executable=sys.executable, version=sys.version, numpy_version=numpy.__version__,
                python_sha256=actual, numpy_file=numpy.__file__)

def install_pidfd_bridge():
    # Invoke the reviewed bridge itself; do not create another implementation.
    with legacy() as (recovery, views): recovery.install_pidfd_bridge()

@contextlib.contextmanager
def previous():
    """Scope unchanged completed form-v3 modules, including its own runtime.

    No validator is patched. All current modules and search paths are restored.
    """
    names = _NAMES + ('runtime58l', 'run58l_form_v3')
    saved = {name: sys.modules.get(name) for name in names}
    old_path = sys.path[:]
    try:
        for name in names: sys.modules.pop(name, None)
        sys.path[:0] = [str(HERE.parent / p) for p in ('form-v3-views-v1', 'form-v3')]
        yield importlib.import_module('views58l')
    finally:
        for name in names:
            sys.modules.pop(name, None)
            if saved[name] is not None: sys.modules[name] = saved[name]
        sys.path[:] = old_path

def inspect_historical():
    """Read real completed form-v3 source/views under the explicit recovery gate."""
    from inspect_predecessor58l import inspect_completed
    runtime()
    return inspect_completed()
