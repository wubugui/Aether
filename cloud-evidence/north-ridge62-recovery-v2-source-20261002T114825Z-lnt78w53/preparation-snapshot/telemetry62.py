"""Native stage telemetry only. Does not supervise or start any subprocess."""
import json,os,resource,time
from pathlib import Path
_START=time.monotonic();_PATH=None;_LABEL=None;_EVENTS=[]

def initialize(out,label):
    global _PATH,_LABEL
    _PATH=Path(out);_PATH.mkdir(parents=True,exist_ok=True);_LABEL=label
    emit('python_entry')

def emit(stage,**details):
    usage=resource.getrusage(resource.RUSAGE_SELF)
    row=dict(stage=stage,pid=os.getpid(),elapsed_seconds=time.monotonic()-_START,native_user_seconds=usage.ru_utime,native_system_seconds=usage.ru_stime,native_peak_rss_kib=usage.ru_maxrss,**details)
    _EVENTS.append(row)
    line=json.dumps(row,separators=(',',':'),allow_nan=False)
    print('NORTH62_STAGE '+line,flush=True)
    if _PATH is not None:
        with (_PATH/(_LABEL+'-events.jsonl')).open('a')as f:f.write(line+'\n');f.flush();os.fsync(f.fileno())
        temp=_PATH/(_LABEL+'-progress.json.tmp');temp.write_text(line+'\n');temp.replace(_PATH/(_LABEL+'-progress.json'))
    return row

def report():return list(_EVENTS)
