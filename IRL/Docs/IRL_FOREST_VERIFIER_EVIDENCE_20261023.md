# IRL forest visual verification — candidate development log (2026-10-23)

## Scope and source of truth

One game only: `minttack/game`, Unreal Engine 5.8 project in `IRL/`. The authoritative `main` HEAD was read as `261cbbbb8264dfde6943cd0fa304029d4867dd3e` during this session. This is a **draft candidate** on branch `workers/irl-forest-scene-verifier-20261023`, PR #18, based on **draft** graphics PR #7. No merge, Unreal editor session, Android APK, physical device test, or independent BIE runtime execution is claimed.

## Evidence-led next move

The existing scene builder spawns 1 original terrain mesh, 14 granite actors, 4 native biome detail actors and moves one copied PlayerStart in a new test level. The initial verifier compared `UObject.get_path_name()` (an Unreal full object path `/Game/Folder/Asset.Asset`) against a bare package path `/Game/Folder/Asset`. This would falsely reject correctly imported terrain/rock meshes. It also did not inspect material slots or six biome mesh/material assignments, and accepted a map path with the right prefix but wrong object.

This candidate fixes those gaps:
- Compare against exact Unreal object paths for imported static meshes and materials.
- Require the exact expected loaded world identity.
- Verify every expected terrain, rock and biome actor label and cardinality.
- Check soil/granite material slot 0 on terrain and rocks.
- Check all six biome asset assignments (ground cover, stone, leaf litter meshes and materials).
- Require genuine positive integer generated instance counts for all four biomes; missing/invalid counts fail closed and are JSON-serializable.
- Emit a JSON PASS/FAIL report under `Saved/IRLVisualValidationReport.json`, raising a visible error on a failed scene.
- Add host-side mocked editor contract tests and negative/tampering cases, wired into the existing graphics GitHub Actions workflow.

## Verification levels

- **Implemented in branch:** source changes and regression tests in PR #18.
- **Previous exact-revision CI evidence:** graphics workflow run `40061265945` succeeded for commit `30a71aa988e1ba93987650b8c81a81bb305ec2fb`, including the initial full-scene mock tests.
- **Latest revision:** must check a new exact-commit workflow run after these additional biome/map checks; do not reuse the earlier success as proof.
- **Unverified:** actual Unreal 5.8 Python API behavior, UHT/C++ compilation, scene render, physics/collision, instanced foliage, Android APK, touch controls, frame pacing, networking and BIE life integration.

## Integration dependencies and next actual engine test

PR #18 is based directly on PR #7, not on later collision and runtime evidence drafts (#8, #9, #10). An in-editor instance count of zero may reveal missing terrain collision rather than a verifier defect. Resolve and test the relevant collision changes from those drafts **without silently merging branches**. On an authorized Unreal 5.8 development machine, compile the native IRL project, import the original PBR assets, build the opt-in test map, execute `IRL/Tools/Visual/verify_irl_forest_visual_level.py` inside the editor, preserve the JSON report, and investigate any failing check. Then capture genuine PIE imagery and a packaged Android/device test before promoting visual quality or gameplay readiness.

Preserve creator decisions 026 (collective autonomy with individual freedom), 029 (minimal restrictions with essential safety), 030 (highest demonstrable capability), and standalone non-LLM BIE THRIVES Experience. Do not replace the original game with an unrelated demo.
