# Native mouse-motion units: observed failure and next proof

The harness sent relative (-12.5,0) for a requested 0.05-radian horizontal step. The native input witness received (-17.7268886566162,0) and the unchanged game's .004 sensitivity applied 0.0709075555205345 radians. The assertion correctly stopped; camera/ship paths stayed zero. The 0.00001-radian tolerance must not be widened to absorb this.

The project uses canvas_items and a 1672×941 logical viewport; the actual captured image is 1179×664. The observed X ratio 1.4181510925 agrees to float precision with 1672/1179=1.4181509754. The old run did not record get_final_transform(), so the exact live matrix is not retroactively claimed.

Godot4.5.1 Viewport::_make_input_local transforms native events by get_final_transform().affine_inverse(); Window::_window_input forwards through push_input. Therefore the proposed harness correction is to map desired viewport-local motion through the actual final transform's basis before Input.parse_input_event, then independently verify the delivered local relative motion, unchanged transform, and the existing bounded orbit increment. Do not change native game sensitivity or directly set game.orbit. A new focused fixture and actual runtime are still required.

Primary sources:
- https://github.com/godotengine/godot/blob/4.5.1-stable/scene/main/viewport.cpp#L1252-L1259
- https://github.com/godotengine/godot/blob/4.5.1-stable/scene/main/viewport.cpp#L1326-L1338
- https://github.com/godotengine/godot/blob/4.5.1-stable/scene/main/window.cpp#L1699-L1718
- https://docs.godotengine.org/en/4.5/classes/class_inputeventmousemotion.html#class-inputeventmousemotion-property-relative
