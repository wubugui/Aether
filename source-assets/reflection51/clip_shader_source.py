"""Auditable source-only injection for the tested native reflection-pass clip.

Not a material converter and not a GPU acceptance test. Unknown vertex paths
fail closed. Every source byte can be recovered by removing the exact blocks.
"""
from __future__ import annotations
import hashlib
import re

NS = "lake51_reflection_"
GLOBAL = "\n/* LAKE51_GLOBAL_BEGIN */\nvarying float lake51_reflection_world_y;\nuniform bool lake51_reflection_clip_enabled = true;\nuniform float lake51_reflection_plane_y = 0.0;\n/* LAKE51_GLOBAL_END */\n"
VERTEX = "\n/* LAKE51_VERTEX_BEGIN */\n    lake51_reflection_world_y = (MODEL_MATRIX * vec4(VERTEX, 1.0)).y;\n/* LAKE51_VERTEX_END */\n"
FRAGMENT = "\n/* LAKE51_FRAGMENT_BEGIN */\n    if (lake51_reflection_clip_enabled && (CAMERA_VISIBLE_LAYERS & 524288u) != 0u && lake51_reflection_world_y < lake51_reflection_plane_y) { discard; }\n/* LAKE51_FRAGMENT_END */\n"
NEW_VERTEX = "\n/* LAKE51_NEW_VERTEX_BEGIN */\nvoid vertex() {" + VERTEX + "}\n/* LAKE51_NEW_VERTEX_END */\n"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def mask_comments(text: str) -> str:
    """Keep source offsets/newlines while ignoring comments and quoted text."""
    out = list(text)
    i = 0
    while i < len(text):
        if text.startswith("//", i):
            end = text.find("\n", i)
            if end < 0:
                end = len(text)
        elif text.startswith("/*", i):
            stop = text.find("*/", i + 2)
            if stop < 0:
                raise ValueError("Unterminated block comment")
            end = stop + 2
        elif text[i] in "\"'":
            quote, end = text[i], i + 1
            while end < len(text):
                if text[end] == "\\":
                    end += 2
                elif text[end] == quote:
                    end += 1
                    break
                else:
                    end += 1
            else:
                raise ValueError("Unterminated string")
        else:
            i += 1
            continue
        for j in range(i, min(end, len(text))):
            if text[j] not in "\r\n":
                out[j] = " "
        i = end
    return "".join(out)


def function_span(text: str, name: str):
    clean = mask_comments(text)
    found = list(re.finditer(r"\bvoid\s+" + re.escape(name) + r"\s*\(\s*\)\s*\{", clean))
    if len(found) > 1:
        raise ValueError(f"Multiple {name} functions")
    if not found:
        return None
    opening = found[0].end() - 1
    depth = 1
    for i in range(opening + 1, len(clean)):
        depth += (clean[i] == "{") - (clean[i] == "}")
        if depth == 0:
            return opening, i, clean[opening + 1:i]
    raise ValueError(f"Unterminated {name} function")


def remove_injection(text: str, added_vertex: bool) -> str:
    blocks = [GLOBAL, FRAGMENT, NEW_VERTEX if added_vertex else VERTEX]
    for block in blocks:
        if text.count(block) != 1:
            raise ValueError("Injected block missing, modified or repeated")
        text = text.replace(block, "", 1)
    return text


def inject(source: str, expected_sha256: str):
    if sha(source) != expected_sha256:
        raise ValueError("Source SHA mismatch")
    clean = mask_comments(source)
    if NS in source or "LAKE51_" in source:
        raise ValueError("Namespace/marker collision")
    if re.search(r"^\s*#", clean, re.M):
        raise ValueError("Preprocessor source requires independent expansion/audit")
    declarations = list(re.finditer(r"\bshader_type\s+spatial\s*;", clean))
    if len(declarations) != 1:
        raise ValueError("Expected one spatial shader declaration")
    if re.search(r"\b(world_vertex_coords|skip_vertex_transform)\b", clean):
        raise ValueError("Unsupported coordinate convention")
    vertex = function_span(source, "vertex")
    if vertex:
        body = vertex[2]
        if re.search(r"\b(return|POSITION)\b", body):
            raise ValueError("Early return/custom projection requires separate audit")
    if not function_span(source, "fragment"):
        raise ValueError("Missing fragment function")
    p = declarations[0].end()
    result = source[:p] + GLOBAL + source[p:]
    span = function_span(result, "vertex")
    added = span is None
    if added:
        result += NEW_VERTEX
    else:
        result = result[:span[1]] + VERTEX + result[span[1]:]
    fragment = function_span(result, "fragment")
    result = result[:fragment[0]+1] + FRAGMENT + result[fragment[0]+1:]
    recovered = remove_injection(result, added)
    if recovered != source or sha(recovered) != expected_sha256:
        raise AssertionError("Source round-trip must be byte exact")
    return result, {"source_sha256": expected_sha256, "output_sha256": sha(result),
                    "round_trip_exact": True, "added_vertex_function": added,
                    "marker_camera_bit": 19, "water_plane_default_y": 0.0,
                    "insertion_scope": "One varying+two uniforms; vertex final worldY; fragment reflection-marker-only discard",
                    "gpu_compilation_verified": False, "visual_acceptance": False}


def self_test():
    samples = [
        "shader_type spatial;\nvoid vertex(){ VERTEX.x += 1.; }\nvoid fragment(){ ALBEDO=vec3(1.); }",
        "// braces { ignored\r\nshader_type spatial;\r\nvoid fragment(){ /* } */ ALBEDO=vec3(1.); }\r\n",
        "shader_type spatial;void vertex(){if(VERTEX.x>0.){VERTEX.z+=1.;}}void fragment(){if(UV.x<0.){discard;}}",
    ]
    for source in samples:
        output, report = inject(source, sha(source))
        assert remove_injection(output, report["added_vertex_function"]) == source
    rejected = [
        "shader_type spatial;render_mode world_vertex_coords;void fragment(){}",
        "shader_type spatial;render_mode skip_vertex_transform;void fragment(){}",
        "shader_type spatial;void vertex(){return;}void fragment(){}",
        "shader_type spatial;void vertex(){POSITION=vec4(1.);}void fragment(){}",
        'shader_type spatial;\n#include "unknown.gdshaderinc"\nvoid fragment(){}',
        "shader_type sky;void sky(){}",
        "shader_type spatial;void vertex(){}",
        "shader_type spatial;void vertex(){}void vertex(){}void fragment(){}",
    ]
    for source in rejected:
        try:
            inject(source, sha(source))
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe/unknown source must be rejected")
    try:
        inject(samples[0], "0"*64)
    except ValueError:
        pass
    else:
        raise AssertionError("Wrong expected hash accepted")
    return {"positive_round_trips": len(samples), "rejected_unknowns": len(rejected), "wrong_hash_rejected": True}


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2))
