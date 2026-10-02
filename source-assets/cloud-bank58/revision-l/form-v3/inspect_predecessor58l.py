"""Read-only historical validation; writes only the named new preparation report."""
import json, sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime58l
if __name__ == '__main__':
    value = runtime58l.inspect_historical()
    destination = runtime58l.HERE / 'PREDECESSOR_RESULT.json'
    with destination.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps(dict(path=str(destination), original_source_stage=value['original_source_stage'],
                         views_chain_verified=value['completed_views']['views_chain_verified'])))
