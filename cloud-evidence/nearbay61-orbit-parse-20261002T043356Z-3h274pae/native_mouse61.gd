extends RefCounted
## Harness-only inverse of Godot4.5.1 Viewport::_make_input_local.
## Desired local relative uses only the basis; local position uses the full T.
const RELATIVE_EPSILON := .00001
const POSITION_EPSILON := .001

static func pair(value: Vector2) -> Array:
 return [value.x,value.y]

static func valid_transform(transform: Transform2D) -> bool:
 if not transform.x.is_finite() or not transform.y.is_finite() or not transform.origin.is_finite(): return false
 var determinant:=transform.determinant()
 if not is_finite(determinant) or determinant==0.0: return false
 var inverse:=transform.affine_inverse()
 return inverse.x.is_finite() and inverse.y.is_finite() and inverse.origin.is_finite()

static func snapshot(window: Window) -> Dictionary:
 var transform:=window.get_final_transform()
 var rect:=window.get_visible_rect()
 return {"final_transform":{"x":pair(transform.x),"y":pair(transform.y),"origin":pair(transform.origin),"determinant":transform.determinant(),"hex":var_to_bytes(transform).hex_encode()},"valid_transform":valid_transform(transform),"viewport_rect_position":pair(rect.position),"viewport_rect_size":pair(rect.size),"window_size":pair(Vector2(window.size)),"display_server_window_size":pair(Vector2(DisplayServer.window_get_size(window.get_window_id()))),"viewport_texture_size":pair(window.get_texture().get_size()),"content_scale_size":pair(Vector2(window.content_scale_size)),"content_scale_factor":window.content_scale_factor,"content_scale_mode":window.content_scale_mode,"content_scale_aspect":window.content_scale_aspect,"window_id":window.get_window_id()}

static func convert(transform: Transform2D, local_center: Vector2, intended_relative: Vector2) -> Dictionary:
 if not valid_transform(transform) or not local_center.is_finite() or not intended_relative.is_finite():
  return {"ok":false,"reason":"Nonfinite or singular input coordinate mapping"}
 var relative:=transform.basis_xform(intended_relative)
 var position:=transform*local_center
 if not relative.is_finite() or not position.is_finite():
  return {"ok":false,"reason":"Nonfinite mapped native event"}
 return {"ok":true,"relative":relative,"position":position}

static func delivery_check(rows: Array, intended_relative: Vector2, local_center: Vector2, before: Dictionary, after: Dictionary) -> Dictionary:
 var result: Dictionary={"event_count":rows.size(),"single_motion":rows.size()==1 and rows[0].get("kind")=="motion","mapping_stable":before==after and before.get("valid_transform",false),"received_relative_matches":false,"received_center_matches":false,"right_button_held":false,"witness_mapping_matches":false,"passed":false}
 if not result.single_motion: return result
 var row: Dictionary=rows[0]
 var relative:=Vector2(row.relative[0],row.relative[1])
 var position:=Vector2(row.position[0],row.position[1])
 result.received_relative_matches=relative.is_finite() and absf(relative.x-intended_relative.x)<RELATIVE_EPSILON and absf(relative.y-intended_relative.y)<RELATIVE_EPSILON
 result.received_center_matches=position.is_finite() and position.distance_to(local_center)<POSITION_EPSILON
 result.right_button_held=row.get("right",false) and (int(row.get("button_mask",0)) & MOUSE_BUTTON_MASK_RIGHT)!=0
 result.witness_mapping_matches=row.get("input_mapping",{})==before
 result.passed=result.mapping_stable and result.received_relative_matches and result.received_center_matches and result.right_button_held and result.witness_mapping_matches
 return result
