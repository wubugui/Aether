# Why Mesh.get_faces is not raw native mesh authority

The installed Godot4.5.1 intake showed a concrete difference between saved cirque `ArrayMesh.surface_get_arrays` and `Mesh.get_faces`:890expanded positions differed, including106atY≥0; maximum3Dworld deviation0.0001230203m. The original `ConcavePolygonShape3D.get_faces` arrays matched the expanded raw GPU arrays exactly asfloat32.

This is explained by the official4.5.1 implementation, checked2026-10-01:

- [Mesh::get_faces](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/mesh.cpp#L473-L483) reads a generated TriangleMesh cache. Its construction takes the raw surface arrays, then passes them to TriangleMesh.create
- [TriangleMesh::create](https://github.com/godotengine/godot/blob/4.5.1-stable/core/math/triangle_mesh.cpp#L125-L155) applies `snappedf(0.0001)` to each vertex before storing the deduplicated vertex table. TriangleMesh.get_faces returns those stored positions

Thus the observed discrepancy is a0.1mmlocal grid snap followed by normalfloat32world transformation, rather than merely an unchanged raw-array read with formatting differences. Whole-triangle byte preservation must use actual surface arrays/indices and the actual collider arrays. Mesh.get_faces is appropriate only when that derived geometry and its precision are explicitly intended.

Current54v2source uses `v2/native-authority/cirque-native-authority.json`, whose692triangles come from the raw saved53GPUarrays and are byte-equal to the original collider. Its432wet/cross-water and19protected dry faces are retained exactly. Earlier derived-geometry attempts and their failed/mis-scoped claims remain available and are not the final authority.

No existing53resource was changed after this finding. Future strict builder/verifier code should not convert an exact native-array claim into a Mesh.get_faces comparison. Automatic `Mesh.create_trimesh_shape` also calls this derived route; direct original/authorized collider arrays remain necessary where exact wet geometry is required.
