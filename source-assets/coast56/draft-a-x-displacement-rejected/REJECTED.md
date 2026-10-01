# Rejected before saving a candidate asset

The first editable-scope proposal moved native X positions along the coast. The static no-fold check found triangle791 changed projected signed area from-110.54049 to+43.49349 near frozen boundary vertices. It failed rather than weakening the constraint or tolerance. No candidate Blender scene or world was saved for this attempt.

The final source keeps all native XZ positions and index topology exact. It reshapes only heights using the current native triangle field, so every projected triangle is unchanged. Full source data, native collider replacement data and actual saved Blender readback are independently checked by `../verify_static56.py`.
