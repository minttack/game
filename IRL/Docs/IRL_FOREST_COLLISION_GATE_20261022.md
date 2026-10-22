# IRL — Forest Collision & Source Integrity Gate (2026-10-22)

## Continuity and goal
ONE original Unreal Engine 5.8 IRL game: \`minttack/game/IRL\`. Parent is PR #7's verified graphics source at commit \`dafbedd3a02257fc8cf8d234cba6e88c04d2587c\`, stacked on graphics PR #6; creator vision and BIE non-LLM architecture unchanged. This worker is an isolated draft candidate. Existing \`main\`, the original third-person level, human-player systems and all unmerged ecology/evidence branches remain untouched.

The earlier visual pipeline could import terrain with no verified physics collision. Mobile BIE foliage raycasts and the player's movement can silently fail or fall through without collision—even when scene textures render.

## Implemented
- \`IRL/Tools/Visual/forest_collision_gate.py\`: original-source PBR provenance/integrity validation verifies the 16 expected texture, mesh and visual preview files byte-for-byte against the generated SHA-256 manifest, exact original source marker and material-pack names. No downloaded/third-party assets are silently substituted.
- Importer checks the entire input before any Unreal \`.uasset\` is created or changed. Bad/missing assets stop the import before mutations.
- Standalone collision preflight **allowlists only** generated mesh \`/Game/IRL/Visual/ProceduralStarter/SM_IRL_TerrainPatch\`. Reads its Unreal BodySetup; configures static \`CTF_USE_COMPLEX_AS_SIMPLE\`; persists it with \`EditorAssetLibrary.save_loaded_asset\` and fails on missing body, failed save or failed readback. This is for one 80m test terrain only; per-triangle collision is *not* a scalable solution for whole planets or dynamic physics actors. Physics plan grounded in Epic UE collision documentation.
- Forest map builder calls preflight **before** cloning the original map, creates the target map directory if needed, then explicitly sets the newly placed terrain actor's component collision profile to \`BlockAll\` and reads it back. It fails closed when no walkable ground configuration is available.
- Existing original scene builder retains no-overwrite checks; changes never reconfigure the default map, desktop renderer or authoritative creature simulation.
- Added \`test_forest_collision_gate.py\` and expanded \`test_editor_scene_builder.py\`, plus GitHub Actions integration.

## Source-backed tests
- Generated PBR data: validates exact 16 files, tampered original normal texture rejected, missing original grass OBJ rejected.
- Editor stub collision: configures only allowlisted terrain, idempotent second configuration, checks failed asset save, rejects missing collision \`BodySetup\` and unrelated assets, verifies actor \`BlockAll\`.
- Map editor stub: verifies valid collision before copying, imported asset only saved once, safely creates the new map directory and new cloned scene, confirms no overwrite on rerun and confirms missing collision prevents any cloned level creation.
- CI workflow \`.github/workflows/irl-original-graphics.yml\` runs these checks plus existing original procedural art and mobile-scoring tests. An actual green workflow result is required for a native/CI verification claim.
- **No UE 5.8 engine build, Editor Python runtime, material import, PIE walk test, actual screenshot, Android GPU/CPU profiling or shipped APK yet.** Python mocks are not Unreal physics tests. They establish correct fail-closed source contracts.

## UE validation gates remaining
1. Build parent PR #6, then this stacked branch in Unreal Engine 5.8.
2. Run original material generator, importer and forest builder in UE Editor; ensure imported terrain \`BodySetup\` changes can be persisted on that exact UE build and \`StaticMeshActor\` blocks Visibility traces and the player capsule.
3. Verify player starts above mesh and lands on the playable terrain; native HISM can raycast and place 4 ground-cover patches; verify the imported terrain's normals/winding and mobile draw costs.
4. Run genuine original First Signal regression, import/render screenshot, package Android testing APK; inspect device p95/p99 GPU and CPU times, thermal state, memory, image fidelity.
5. Merge only through the tested shared game integration branch with human duo, BIE ecology, source evidence and graphics controls.

**Status:** actual source implementation candidate; engine and Android integration **NOT verified**. Original creator's approved image remains aspirational concept art, not present gameplay graphics.
