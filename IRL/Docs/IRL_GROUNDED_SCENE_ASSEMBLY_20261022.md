# IRL — Handoff: grounded Unreal scene assembly (2026-10-22)

**Project:** One authoritative game: `minttack/game`, Unreal 5.8 at `IRL/IRL.uproject`. **Candidate:** `workers/irl-unreal-scene-assembly-20261022`, stacked on PR #7, which is stacked on graphics PR #6, both unmerged at start. This is an editor workflow for the existing IRL map, not a standalone replacement game or final packaged Android build.

## Objective

Bring real, original and reproducible PBR source textures/meshes from PR #7 into an opt-in, grounded visual area of the actual UE game. Advance toward the user-approved concept image without pretending it has been rendered in Unreal. Preserve creator decisions 026 autonomous freedom + guidance, 029 essential security with minimal artificial game limits and 030 maximize demonstrated quality. BIE THRIVES remains a separate, non-LLM runtime; this environment assembly was engineered externally, not authored/executed by a live BIE instance.

## New implementation

- `Tools/Visual/scene_stage_core.py` independently parses the **exact** 65x65 source OBJ terrain mesh. Rejects wrong count, grid layout, nonfinite coordinates and out-of-bounds height queries. Bilinearly interpolates source terrain elevations; deterministically plans one terrain, one optional `AIRLLivingBiomeDetailActor`, and eight visually grounded granite stones. Maximum 20 stones. All positions use **cm**, matching generated Unreal mesh source. Terrain area: 80×80 m.
- `Tools/Visual/assemble_irl_stage.py` runs inside actual Unreal 5.8 Editor with PythonScriptPlugin. It inspects the **currently open existing IRL level**, finds first PlayerStart where available, and stages the patch 140 m to the side to avoid overwriting the tutorial area. Loads six assets and the native C++ biome class; aborts if missing. Duplicates are detected by a stable prefix. It creates one UStaticMeshActor for the patch, one biome actor with grass/stone material bindings, and eight boulder actors. **Default: DRY RUN, no actor modifications**. Operators must set `IRL_STAGE_APPLY=1` to place; `IRL_STAGE_SAVE=1` to save. A failed partial placement rolls back only newly spawned actors. An applied but unsaved placement remains in the editor and can be inspected or discarded. Existing game mode, map defaults, player spawns, tutorial scripts and BIE logic are untouched.
- `IRL.uproject` enables `PythonScriptPlugin` **Editor only**, not shipping Android.
- Existing `Tools/Visual/import_into_unreal.py` now sets **complex-as-simple collision** only for the static 8,192-triangle starter terrain. This allows tracing for grass and stones. **Do not use complex-as-simple for high-triangle mobile environments** without profiling.
- `Source/IRL/Visual/IRLLivingBiomeDetailActor.cpp`: placement cache skips missing mesh channels, avoiding up to **190 unnecessary terrain line traces** for the unassigned leaf-litter channel during this particular visual setup. This is a code-level count of avoided attempts, NOT measured GPU or runtime improvement.
- Tests: `test_scene_stage.py` (10 pure Python checks for real/synthetic heightfield, bounds, grounded transforms, seeds and safety), `test_editor_stage_mock.py` (4 mocked editor checks for zero mutations in dry run, duplicate suppression, rollback of four actors on deliberate failure, and explicit save gate). Tests run in clean checkout using a synthetic fixture if the generated artwork isn't present; also run against the **actual** generated OBJ if present.

## Evidence and verification

- Locally executed **14/14 host Python checks PASS** with original generated terrain, and again 14/14 PASS in clean-checkout fixture mode.
- Source was committed to GitHub; `scene_stage_core.py`, `assemble_irl_stage.py`, `test_scene_stage.py` and `test_editor_stage_mock.py` blob SHAs were independently compared to locally run source and matched exactly.
- Docs for editor actor spawning/queries: [UE 5.8 EditorActorSubsystem](https://dev.epicgames.com/documentation/unreal-engine/API/Editor/UnrealEd/UEditorActorSubsystem), [UE 5.8 collision setup](https://dev.epicgames.com/documentation/unreal-engine/setting-up-collisions-with-static-meshes-in-blueprints-and-python-in-unreal-engine), [UE 5.8 Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/PythonAPI).
- **Not run:** UE 5.8 C++ compiler, real Unreal Python bindings, material shader compile, PlayerStart map navigation, original level preview, on-device Android renderer, physical FPS/memory/temperature, multiple human players, actual BIE cognitive runtime. This change is **implemented in source and host-tested**, **not engine-integrated/verified**, **not merged/released**.

## Reproduce local tests

```sh
# Inside IRL/Tools/Visual:
python -m unittest discover -p "test_*stage*.py" -v
```

For actual Unreal workflow: install UE 5.8 + IRL code and compile graphics PR #6; use `generate_irl_showcase.py` from PR #7 to generate source OBJ/PNG assets; run `import_into_unreal.py` inside Unreal; then `assemble_irl_stage.py` with no flags for inspection. Only with creator/editor approval, set `IRL_STAGE_APPLY=1`; to save as part of the original game set both `IRL_STAGE_APPLY=1` and `IRL_STAGE_SAVE=1`. Save a backup/commit before touching the map. Ensure actor class and six imported assets exist in the **same Unreal project**.

## Next evidence-gated milestone

1. With UE 5.8 available, run real editor import + material compiler checks and set correct terrain collision/mesh orientations. Record screenshot from actual UE game, not generated concept art.
2. Fix any actual editor API failures (unverified Python/editor UProperty bindings); capture a walkthrough clip from the *real* IRL map. Evaluate physically plausible lighting, depth, shadows, vegetation.
3. Collect matching Moto G and higher-end Android GPU/frame-time, 1% low FPS, thermals and memory; compare at the same camera path, with repeated runs. Preserve the 30 FPS initial mobile budget until physical evidence supports higher/lower.
4. Integrate PR #6/#7/#8 through engine tests after refreshing main. Eventually combine ecology, autonomous agents, two-human networking and sourced BIE outcomes; no independent competing prototype.
