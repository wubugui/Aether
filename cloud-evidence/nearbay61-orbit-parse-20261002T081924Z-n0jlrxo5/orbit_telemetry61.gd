extends RefCounted
## Diagnostic timing only. No field here authorizes runtime completion.
var started_usec: int=Time.get_ticks_usec()
var counters: Dictionary={}
var timers: Dictionary={}
var open_operations: Dictionary={}
var last_process_usec := -1
var last_process_wall_seconds := 0.0
var last_engine_delta_seconds := 0.0
var process_wall_seconds := 0.0
var process_delta_seconds := 0.0

func count(label: String, amount: int=1) -> void:
 counters[label]=int(counters.get(label,0))+amount

func begin(label: String) -> int:
 var now:=Time.get_ticks_usec()
 open_operations[label]=now
 return now

func end(label: String, began: int) -> void:
 var seconds: float=(Time.get_ticks_usec()-began)/1000000.0
 var row: Dictionary=timers.get(label,{"calls":0,"total_seconds":0.0,"max_seconds":0.0,"last_seconds":0.0})
 row.calls+=1;row.total_seconds+=seconds;row.max_seconds=maxf(row.max_seconds,seconds);row.last_seconds=seconds
 timers[label]=row
 open_operations.erase(label)

func process(delta: float) -> void:
 var now:=Time.get_ticks_usec()
 if last_process_usec>=0:
  last_process_wall_seconds=(now-last_process_usec)/1000000.0
  process_wall_seconds+=last_process_wall_seconds
 last_process_usec=now
 last_engine_delta_seconds=delta;process_delta_seconds+=delta
 count("late_process_callbacks")

func snapshot() -> Dictionary:
 var operations: Dictionary={}
 var now:=Time.get_ticks_usec()
 for label in open_operations: operations[label]=(now-int(open_operations[label]))/1000000.0
 return {"diagnostic_only":true,"wall_seconds":(now-started_usec)/1000000.0,"counters":counters.duplicate(true),"timers":timers.duplicate(true),"open_operation_elapsed_seconds":operations,"process_interarrival_wall_seconds_sum":process_wall_seconds,"engine_process_delta_seconds_sum":process_delta_seconds,"last_process_interarrival_wall_seconds":last_process_wall_seconds,"last_engine_process_delta_seconds":last_engine_delta_seconds}
