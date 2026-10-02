"""Path-only adapter: execute unchanged source-v1 geometry; no new shape or gate.

Keep the author candidate/version and all geometry functions exactly original.
Only the source/embedded-native package location is this recovery directory.
"""
from pathlib import Path
import hashlib
_original = Path(__file__).resolve().parent.parent/'source-v1'
_original_geometry = (_original/'geometry58l.py').read_bytes()
if hashlib.sha256(_original_geometry).hexdigest() != '5342902d33ceead7213b558a265d36da92686649a0487035409abdcb383d4b7d':
    raise ValueError('Unchanged original geometry required')
exec(compile(_original_geometry, str(_original/'geometry58l.py'), 'exec'), globals())
CANDIDATE_PATH = _original/'candidate.json'
BINDING_PATH = _original/'bindings.json'
SOURCE = HERE/'cloud_bank58l_recovery_v1.blend'
