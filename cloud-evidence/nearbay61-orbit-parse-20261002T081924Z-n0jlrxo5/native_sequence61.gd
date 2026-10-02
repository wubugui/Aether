extends RefCounted
## Pure ordering guard shared by production and the light synthetic fixture.
var last_sample := -1
var last_audit := -1
var samples := 0
var audits := 0
var pending_frames: Array[int]=[]
var event_active := false
var event_frame := -1
var required_event_frame := -1
var completed_events := 0
var failure := ""

func reject(reason: String) -> bool:
 failure=reason
 return false

func sample(frame: int) -> bool:
 if not failure.is_empty(): return false
 if last_sample>=0 and frame!=last_sample+1: return reject("Duplicate or missing actual process frame")
 last_sample=frame;samples+=1;pending_frames.append(frame)
 if event_active and required_event_frame<0 and frame>event_frame: required_event_frame=frame
 return true

func audit(frame: int) -> bool:
 if not failure.is_empty(): return false
 if pending_frames.is_empty() or pending_frames[0]!=frame: return reject("Audit is missing, duplicate or out of order")
 pending_frames.pop_front();last_audit=frame;audits+=1
 return true

func begin_event(frame: int) -> bool:
 if not failure.is_empty(): return false
 if event_active or not pending_frames.is_empty() or samples!=audits: return reject("Input attempted before exact pending segments audited")
 if last_sample>frame: return reject("Input frame precedes last sampled process")
 event_active=true;event_frame=frame;required_event_frame=-1
 return true

func event_ready() -> bool:
 return failure.is_empty() and event_active and required_event_frame>event_frame and last_audit>=required_event_frame and pending_frames.is_empty() and samples==audits

func complete_event() -> bool:
 if not event_ready(): return reject("Input has no newer actual process and associated complete physics audit")
 event_active=false;completed_events+=1
 return true

func capture_ready(frame: int) -> bool:
 return failure.is_empty() and not event_active and frame>=0 and last_sample>=frame and last_audit>=frame and pending_frames.is_empty() and samples==audits

func snapshot() -> Dictionary:
 return {"last_sample_frame":last_sample,"last_audit_frame":last_audit,"sample_count":samples,"audit_count":audits,"pending_count":pending_frames.size(),"event_active":event_active,"event_frame":event_frame,"required_event_frame":required_event_frame,"completed_events":completed_events,"failure":failure}
