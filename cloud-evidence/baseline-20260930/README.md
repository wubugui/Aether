# Cloud continuation baseline — 2026-09-30

- Repository: https://github.com/wubugui/Aether, fixed migration commit `98486d31c6769b2a572e5d9f4a7a6754922b0e46`.
- Independent branch: `development/feiting-cloud-20260930`. No push performed.
- Sparse selection contains the complete active candidate, editable candidate source assets, protected cliff kit, 20 references and original reference. `inventory.json`: 3,105 selected tracked files, none missing. The ongoing full historical migration is separate and not complete here.
- Game42c SHA256: `06f86e4bc73ed2d28a4eb6d76e89e3946cb6b6c6e7e72b9b36f55ed972880c91`.
- Protected cliff master SHA256: `abb66e414168cbd24e2495b64c27714759c844ff75582b0f71d5384d8f760dd7`.
- No AGENTS.md or repository SKILL.md was present in this migration tree. Read GOAL.md, MIGRATION_HANDOFF.md, relevant current builders/scripts and the retained Hub guide.

## Actual verification

Official Godot `4.5.1.stable.official.f62fdbde1` installed separately in `/workspace/shared/feiting-tools`. Clean headless import exit 0 with empty stderr. This is import evidence only.

A non-headless cloud desktop launch with the Compatibility renderer reached WORLD READY (208 authored terrain tiles, 54,797 scatter instances, 169 scene landmarks, 6 ports). Startup completed 120 frames and exited 0. The native window was directly inspected: airship, terrain, snowy mountain, water, port and giant low cloud underside were visible. Logs name Mesa llvmpipe (LLVM 19.1.7, 256 bits), a software renderer. **This is not hardware-GPU acceptance.** Startup also had unsupported VSync and missing ALSA audio-device messages; later tooling explicitly uses the Dummy audio driver.

Cloud shell does not have direct display access. Normal cloud desktop terminal launch provides its existing display environment. No device permissions, network settings or security controls were changed.

## Remaining gates

All 20 reference views and original opening remain visually unaccepted. Real hardware-GPU validation remains unavailable in the inspected cloud desktop. Functional tests and software-rendered pixels do not fulfill that gate.

The LAN Hub health request returned HTTP 502 with connection refused. User subsequently explicitly permitted using cloud Blender (2026-09-30 19:06 UTC); existing native files are preserved and any new modeling must remain an independent editable asset, without replacing the protected cliff master.

## New defect found

Rain and Snow MultiMeshes in both saved Game42b and Game42c contain flags/count/mesh but no serialized buffer or transform/custom arrays. In actual non-headless 4.5.1 Compatibility tests, both payloads read as zero. This is evidence for missing saved particle instance state, not proof of every prior visual symptom's cause. New 42d work must reconstruct original deterministic instance data and require save/reload validation before being accepted even as a functional candidate.

Official Blender 4.5.14 LTS was downloaded with a matching published SHA256. Both upper43 and the protected cliff master reopened successfully; exit 0 and empty stderr. `native-assets.json` records their editable object counts and unchanged source hashes.
