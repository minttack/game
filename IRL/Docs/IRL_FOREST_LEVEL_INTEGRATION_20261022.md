# IRL — First playable visual-test map integration (2026-10-22)

## Same game, verified source state
One authoritative Unreal Engine 5.8 game: https://github.com/minttack/game in \`IRL/\`. Main as checked remained \`261cbbbb8264dfde6943cd0fa304029d4867dd3e\`.

This is an extension of existing **draft** PR #7, \`workers/irl-original-pbr-showcase-20261022\`, stacked on **draft** PR #6 (mobile graphics quality and HISM visual decorator). It does NOT replace \`ThirdPerson/Lvl_ThirdPerson\`, change the default startup map, merge any branch, create a separate game, or touch the original IRL Experience and two-human systems.

## What this next move implements
- \`forest_scene_plan.py\`: deterministic pure-Python layout for an 80m terrain tile, 14 boulders, four procedurally decorated patches and one moved player start, all in Unreal centimeter coordinates. Data remains scoped to the existing original UE game.
- \`build_irl_forest_validation_level.py\`: Unreal Editor Python script that **refuses overwrite**; verifies original template map and all imported original soil/stone/leaf assets exist, and confirms the C++ biome class is compiled, before cloning the existing game map to \`/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation\`. It places a mesh/material-bearing terrain and rocks, configures four \`AIRLLivingBiomeDetailActor\` instances with the generated PBR art, moves the copied map's lone PlayerStart, adds missing sun/sky/atmosphere actors, aims the editor camera at the forest and saves the new map. The original template is untouched and remains the default map.
- \`AIRLLivingBiomeDetailActor\` updated to calculate a MAX-Detail terrain-grounded transform cache **once per instance**. Later local Android tier changes reuse those transforms instead of repeating up to 725 line traces per biome patch. Dedicated servers skip decorative instance generation entirely. Cached transforms still have a rebuild of visible HISM instances on quality change; do not claim zero hitch.
- \`.github/workflows/irl-original-graphics.yml\`: validation workflow triggered by visual source PR changes, runs Python syntax/asset/score/layout/editor-stub tests on Ubuntu, generates original 512px PBR assets from the existing generator, validates manifest hashes and attaches artifact \`IRL-Original-Mobile-PBR-Source-512\` for Unreal Editor import.
- Safety regressions: \`test_scene_plan.py\`, \`test_editor_scene_builder.py\`. No separate external life/intelligence model is embedded.

## Actual evidence
- Local \`python -m compileall\` passed for level builder and plan. Pure scene layout PASS (identical plan with same seed, different plan with new seed, counts, unique actor labels, terrain bounds, bad plan rejection).
- Local Unreal *stub* test PASS: clones template into a different map path, configures 4 biome actors, assigns original assets, moves the PlayerStart, adds lighting and saves, then refuses to overwrite when rerun. This is a mocked editor API contract, **not** Unreal compilation.
- Original asset pack: generator verified 17 identical file hashes across independent runs (16 source files + 1 manifest); PBR normal and OBJ topology validation passed. The provenance is generated source, NOT scans, photorealism or original AAA art.
- **GitHub workflow run 39741716988**: conclusion \`success\` on PR #7, head \`1c28884f7a0d22900bff7baa87e939edfcd1822c\`. All steps passed including native Python source validation and upload. Asset \`IRL-Original-Mobile-PBR-Source-512\` was confirmed on the run. Subsequent code updates need their own fresh CI/readback.
- Unreal Editor 5.8 Python calls were checked against Epic's documented \`LevelEditorSubsystem.new_level_from_template\`, \`EditorActorSubsystem.spawn_actor_from_class\` and \`UnrealEditorSubsystem.set_level_viewport_camera_info\` signatures. Script **has not actually run in UE** and the C++ actor change **was not compiled against UE**.
- Actual GPU rendering screenshot, BIE autonomous life integration, material texture quality, Android APK, real device 30FPS target, thermals and two-human play: **not tested and not released**.

## Open the first actual Unreal scene (Windows dev machine)
1. Check out PR #7's HEAD, including graphics PR #6's C++ actor, within the **same** IRL Unreal project. Compile \`IRL/IRL.uproject\` in Unreal Engine 5.8. Fix any Unreal compiler issues before continuing.
2. \`python -m pip install numpy pillow\` in the Python environment used to run the generator. From repo root run:
   \`\`\`sh
   python IRL/Tools/Visual/generate_irl_showcase.py --size 512 --seed 20261022
   \`\`\`
3. Enable Unreal's **Python Editor Script Plugin**, reopen the editor and run \`IRL/Tools/Visual/import_into_unreal.py\` using **Tools → Execute Python Script**. Confirm PBR and mesh assets appear under \`/Game/IRL/Visual/ProceduralStarter\`. This action does not touch the original gameplay map.
4. Run \`IRL/Tools/Visual/build_irl_forest_validation_level.py\` from the same editor. It creates **one new copy** at \`/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation\`. It fails closed if that map already exists; don't delete or overwrite user-made map data.
5. Inspect world scale, mesh collision, material roughness, normals, turf lighting, instanced vegetation density and PlayerStart. The actor's in-editor rendering requires valid collision raycasts against the imported terrain. If green coverage is missing, inspect terrain collision and actor instance counts before believing the script succeeded.
6. Press Play **in that test map** and capture an actual in-engine screenshot. The original map stays the default and is available unchanged. On Android, build a packaged test and record p95/p99 CPU and GPU frame time, memory and temperature with a repeatable camera path; feed authentic CSV into \`score_mobile_capture.py\` for review.

## Limitations and release gates
- Existing procedural textures are a compact starter set, not an artist-finished AAA forest. Real photogrammetry, creature models, water and atmospheric VFX still missing.
- Editor script expects precisely one PlayerStart in the cloned template, correct Unreal Python property exposure for \`AIRLLivingBiomeDetailActor\`, and imported collision-ready static meshes. Each is an engine validation gate.
- An engine compile, PIE screenshot, Android hardware measurements and a real BIE ecology bridge are REQUIRED before merging. Do not call this the approved collage's real screenshot or an Android APK.
- Only one authoritative game, all other PRs remain independent; no claims of trillion individually simulated cycles.

## Next measured BIE step
Run UE compile/visual comparison and save a genuine screenshot, then select between art/lighting and mobile caching improvements based on observed image-quality and frame time results. Avoid fabricated gains.
