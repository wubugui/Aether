extends SceneTree
const NativeMouse=preload("../native_mouse61.gd")

class Sink:
 extends Node
 var rows:=[]
 var angle:=Vector2.ZERO
 func _input(event: InputEvent) -> void:
  if not event is InputEventMouseMotion: return
  rows.append({"kind":"motion","relative":NativeMouse.pair(event.relative),"position":NativeMouse.pair(event.position),"global_position":NativeMouse.pair(event.global_position),"right":Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT),"button_mask":event.button_mask,"input_mapping":NativeMouse.snapshot(get_tree().root)})
  # Same arithmetic as the frozen game, but this sink is not a world run.
  if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
   angle+=event.relative*Vector2(-.004,-.003)
   angle.y=clampf(angle.y,-1.05,1.05)

var checks:=[]
var failed:=false
var output: String

func record(name: String, ok: bool, details: Variant=null) -> void:
 checks.append({"name":name,"passed":ok,"details":details})
 if not ok: failed=true

func _initialize() -> void:
 output=OS.get_cmdline_user_args()[0]
 call_deferred("run")

func roundtrip(label: String, transform: Transform2D, intended: Vector2) -> void:
 var center:=Vector2(836,470.5)
 var converted:=NativeMouse.convert(transform,center,intended)
 record(label+"_conversion_valid",converted.ok)
 if not converted.ok: return
 var event:=InputEventMouseMotion.new()
 event.relative=converted.relative;event.position=converted.position;event.global_position=converted.position
 var local: InputEventMouseMotion=event.xformed_by(transform.affine_inverse())
 var detail: Dictionary={"transform_hex":var_to_bytes(transform).hex_encode(),"intended_local_relative":NativeMouse.pair(intended),"sent_window_relative":NativeMouse.pair(event.relative),"received_local_relative":NativeMouse.pair(local.relative),"intended_local_center":NativeMouse.pair(center),"sent_window_position":NativeMouse.pair(event.position),"received_local_position":NativeMouse.pair(local.position)}
 record(label+"_actual_xformed_by_roundtrip",absf(local.relative.x-intended.x)<NativeMouse.RELATIVE_EPSILON and absf(local.relative.y-intended.y)<NativeMouse.RELATIVE_EPSILON and local.position.distance_to(center)<NativeMouse.POSITION_EPSILON,detail)
 record(label+"_source_event_not_mutated",event.relative==converted.relative and event.position==converted.position)

func button(pressed: bool) -> void:
 var converted:=NativeMouse.convert(root.get_final_transform(),root.get_visible_rect().get_center(),Vector2.ZERO)
 var event:=InputEventMouseButton.new()
 event.button_index=MOUSE_BUTTON_RIGHT;event.pressed=pressed
 event.button_mask=MOUSE_BUTTON_MASK_RIGHT if pressed else 0
 event.position=converted.position;event.global_position=event.position;event.window_id=root.get_window_id()
 Input.parse_input_event(event);Input.flush_buffered_events()

func dispatch(label: String, sink: Sink) -> void:
 var intended:=Vector2(-12.5,0)
 var before:=NativeMouse.snapshot(root)
 var center:=root.get_visible_rect().get_center()
 var converted:=NativeMouse.convert(root.get_final_transform(),center,intended)
 record(label+"_live_mapping_valid",converted.ok and before.valid_transform,before)
 if not converted.ok: return
 button(true)
 record(label+"_native_button_pressed",Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT))
 var count:=sink.rows.size()
 var previous:=sink.angle
 var event:=InputEventMouseMotion.new()
 event.relative=converted.relative;event.position=converted.position;event.global_position=event.position
 event.window_id=root.get_window_id();event.button_mask=MOUSE_BUTTON_MASK_RIGHT
 Input.parse_input_event(event);Input.flush_buffered_events()
 var after:=NativeMouse.snapshot(root)
 var rows:=sink.rows.slice(count)
 var audit:=NativeMouse.delivery_check(rows,intended,center,before,after)
 var detail: Dictionary={"mapping_before":before,"mapping_after":after,"sent_window_relative":NativeMouse.pair(event.relative),"intended_viewport_relative":NativeMouse.pair(intended),"sent_window_position":NativeMouse.pair(event.position),"delivered":rows,"delivery_check":audit,"angle_before":NativeMouse.pair(previous),"angle_after":NativeMouse.pair(sink.angle)}
 record(label+"_actual_parse_flush_dispatch",audit.passed,detail)
 record(label+"_unchanged_angle_tolerance",absf(sink.angle.x-previous.x-.05)<.00001 and absf(sink.angle.y-previous.y)<.00001,detail)
 button(false)
 record(label+"_native_button_released",not Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT))
 if rows.size()!=1: return
 record(label+"_missing_event_rejected",not NativeMouse.delivery_check([],intended,center,before,after).passed)
 record(label+"_duplicate_event_rejected",not NativeMouse.delivery_check([rows[0],rows[0]],intended,center,before,after).passed)
 var wrong: Array=rows.duplicate(true);wrong[0].relative=[-17.7268886566162,0]
 record(label+"_old_scaled_delta_rejected",not NativeMouse.delivery_check(wrong,intended,center,before,after).passed)
 var changed: Dictionary=after.duplicate(true);changed.final_transform.hex+="changed"
 record(label+"_changed_transform_rejected",not NativeMouse.delivery_check(rows,intended,center,before,changed).passed)
 var unseen: Array=rows.duplicate(true);unseen[0].input_mapping=changed
 record(label+"_witness_transform_change_rejected",not NativeMouse.delivery_check(unseen,intended,center,before,after).passed)
 var released: Array=rows.duplicate(true);released[0].right=false
 record(label+"_unheld_button_rejected",not NativeMouse.delivery_check(released,intended,center,before,after).passed)

func run() -> void:
 roundtrip("identity",Transform2D.IDENTITY,Vector2(-12.5,0))
 roundtrip("uniform",Transform2D(Vector2(.705,0),Vector2(0,.705),Vector2.ZERO),Vector2(-12.5,0))
 roundtrip("nonuniform_translated",Transform2D(Vector2(.5,0),Vector2(0,.75),Vector2(37,-19)),Vector2(-12.5,4.25))
 roundtrip("sheared_translated",Transform2D(Vector2(.8,.1),Vector2(.2,1.3),Vector2(37,-19)),Vector2(-12.5,4.25))
 roundtrip("reflected",Transform2D(Vector2(-.8,0),Vector2(0,1.3),Vector2(37,-19)),Vector2(-12.5,4.25))
 record("singular_rejected",not NativeMouse.convert(Transform2D(Vector2(1,2),Vector2(2,4),Vector2.ZERO),Vector2.ZERO,Vector2.ONE).ok)
 record("infinite_basis_rejected",not NativeMouse.convert(Transform2D(Vector2(INF,0),Vector2.UP,Vector2.ZERO),Vector2.ZERO,Vector2.ONE).ok)
 record("nan_origin_rejected",not NativeMouse.convert(Transform2D(Vector2.RIGHT,Vector2.DOWN,Vector2(NAN,0)),Vector2.ZERO,Vector2.ONE).ok)
 record("nonfinite_delta_rejected",not NativeMouse.convert(Transform2D.IDENTITY,Vector2.ZERO,Vector2(INF,0)).ok)
 record("nonfinite_center_rejected",not NativeMouse.convert(Transform2D.IDENTITY,Vector2(NAN,0),Vector2.ONE).ok)
 var sink:=Sink.new();root.add_child(sink)
 root.content_scale_size=Vector2i(1672,941)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.size=Vector2i(1180,664)
 await process_frame
 await process_frame
 record("headless_content_scale_nonidentity",root.get_final_transform()!=Transform2D.IDENTITY,NativeMouse.snapshot(root))
 dispatch("canvas_items_live",sink)
 root.global_canvas_transform=Transform2D(Vector2(.8,.1),Vector2(.2,1.3),Vector2(37,-19))
 await process_frame
 dispatch("canvas_plus_shear_live",sink)
 sink.queue_free()
 await process_frame
 await process_frame
 var result: Dictionary={"version":"orbit61-native-input-units-v5","engine":Engine.get_version_info(),"display_server":DisplayServer.get_name(),"passed":not failed,"checks":checks,"scope":"Actual InputEventMouseMotion.xformed_by and actual Input.parse_input_event/flush to Node._input in a headless synthetic root Window. No game/world, real display, image, hardware GPU, production final transform, camera motion or orbit-runtime acceptance."}
 var file:=FileAccess.open(output,FileAccess.WRITE)
 file.store_string(JSON.stringify(result,"  ")+"\n");file.close()
 print("ORBIT61_INPUT_UNITS ",not failed," checks=",checks.size())
 quit(1 if failed else 0)
