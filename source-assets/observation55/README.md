# Native observation candidate55

Game55Observation.tscn inherits the saved53west native scene. It changes only the root controller subclass and an opt-in observation switch. The two lake observations now place the same actual airship and camera so the complete ship and water mirror fit together. Ship size, camera XZ/FOV, underlying geometry/materials/collision/scatter and other reference entries remain unchanged. These are persistent navigation poses, not screenshot-only replacements. The default project entry is unchanged.

Actual saved-scene validation:
- Scope readback observation55-scope-20261001T084506Z-opfl4ekt:11294 nodes, stored properties/exact MultiMesh buffers, effective graph owners/groups/persistent connections preserved. Rain28800/Snow19200 floats valid. Root subclass and export are the only exclusions. Native scene inheritance is inspected directly.
- First scope attempt084315 retained as failed because premature renderer shutdown leaked two textures. Added3frames+post-draw before freeing and8after final free; corrected independent run clean0. No world geometry correction was hidden.
- observation55-renderer-20261001T084531Z-z02rqqhw:two saved poses and four actual main/raw-reflection PNGs, clean0. Both placements reproduce exact C transform bytes, preserve scale, synchronize gameplay heading, pass complete actual geometry/frustum and conservative body/propeller/camera/water clearance. Disabled switch restores original observation transforms; repeated enable restores saved transform bytes.
- player-flight55-renderer-20261001T084651Z-2kjjevt4:ordinary boot, F2 exits observation without turning ship, physical Input.parse events W and Space exercise original move_and_slide.12.23010254m travel, peak13.7500038m/s, stable anchored stop and all keys released, zero collisions/damage. Three actual images reviewed. This proves a bounded automated-input path, not native OS keyboard focus or full-world flight.

Actual images are Godot4.5.1 Compatibility/Mesa llvmpipe software rendering. Complete GOAL, independent visual acceptance and hardwareGPU remain false. Boat width/height ratio, giant repeated sky clouds, sharp mountain forms, greenbanks and broader environment references remain open. Original350m path and1344 conversion-pixel failures remain recorded.

Open scenes/candidate55-observation/Game55Observation.tscn in the original project to inspect. Bracket reference navigation uses the saved controller; F2 returns to ordinary follow-camera flight. No project default promotion is implied.
