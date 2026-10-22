# IRL — First authentic forest editor evidence gate
**2026-10-22 · Isolated worker candidate · ONE game**

## Authoritative continuity
Source: \`minttack/game/IRL\` Unreal Engine 5.8. This change is based on the unmerged grounded-forest PR #8, which is stacked on PBR PR #7 and adaptive Android graphics PR #6. It does NOT create a new game, alter \`main\`, replace the original ThirdPerson map, merge parallel duo/life/evidence workers or embed an LLM in BIE THRIVES Experience. Creator decisions 026, 029 and 030 remain unchanged.

## The actual blocker addressed
Source files and mocked editor tests passed, but the original forest had never been placed or traced in Unreal. The presence of an imported \`BodySetup\` collision flag does NOT prove that real collision queries find the terrain or that the PlayerStart can stand on it.

## New code
- \`forest_world_evidence.py\`: pure offline BIE-style assessor (report → checks → evidence disposition). Requires **14 unique ground probes**: nine grid points, four biome centers and the player start. Each must be a blocking hit on \`IRL_OriginalForestTerrain\`, with finite walkable normal (>=0.70), plausible measured height and spawn clearance within 110–1000cm. Requires exactly one terrain, four biome instances and one PlayerStart, actual named HISM counts (each nonempty and <=725 instances per patch), and assigned soil/rock/foliage material and mesh evidence. Rejects spoofed rock-as-terrain, missing/duplicate/invalid reports.
- \`probe_unreal_forest.py\`: Unreal Editor-only script that checks the **currently opened isolated validation level**, gets the editor World, gathers actual actors and instance counts, issues \`SystemLibrary.line_trace_single\` using \`TRACE_TYPE_QUERY1\` (visibility in standard projects), ignores decorative rocks, and records actual physics hit actor/normal/ground elevation. Writes full observations and assessment as JSON into \`Project/Saved/IRL/forest_editor_audit_<timestamp>.json\`. It **throws an explicit error** when the source-reported engine observations fail; cannot be substituted by pure Python mocks.
- \`run_irl_forest_validation.py\`: single editor entry point; stops during PIE. If target test map exists, LOADS and audits it without overwriting. Otherwise requires the original generated/source-validated art and runs importer and isolated level builder, then the physics audit. The gameplay default map is not modified.
- \`test_forest_world_evidence.py\`: strict scorer tests; \`test_probe_unreal_forest_mock.py\`: source-level editor API stub tests. These are deliberately NOT described as actual Unreal execution.
- Adds CI steps to original visual-source verification workflow. CI success means source and mocks pass; **only a report emitted by UE Editor is candidate real-world editor evidence**. Even then, an actual playable session and Android packaged build require separate tests.

## Running the next actual validation
1. Check out the same single IRL project on the graphics branch stack and compile native Unreal Engine 5.8 game module. Do not merge unverified feature PRs; confirm default Blueprint controller is connected to IRL native C++.
2. Obtain original PBR generator output via \`python IRL/Tools/Visual/generate_irl_showcase.py --size 512 --seed 20261022\`, or the CI workflow artifact placed under \`IRL/Tools/Visual/Generated\`. Enable the Python Editor Script Plugin.
3. In original Unreal Editor, use **Tools → Execute Python Script**, selecting \`IRL/Tools/Visual/run_irl_forest_validation.py\`. This must either safely open an existing isolated map or create the new copy, then run an editor **physics** check.
4. Inspect JSON \`IRL/Saved/IRL/forest_editor_audit_*.json\`; \`EDITOR_REVIEW_ELIGIBLE\` means source-reported editor geometry and asset preflight passed. \`NOT_ESTABLISHED\` means the report says what failed; no invented metric or replay.
5. If editor gate passes, actually press Play and walk/land across terrain, capture a genuine screenshot, and build/profile Android on the Moto G. Record CPU/GPU p95 and p99 frame time, actual textures, memory and thermal behavior. 30 FPS remains a provisional target not a measured achievement.
6. Merge this and the dependent graphical PRs only after real UE and device gates, and separately connect verified BIE-driven creatures and the two-player world.

### Verification limits (retain in all reports)
Offline/mocked CI test success does not mean UE module compiled, editor ran, collision happened, smartphone graphics rendered, AAA art exists or NPCs have biological Experience. The JSON source label is self-reported by a script, not cryptographic proof of running Unreal. No released Android APK or final game exists from this change.

### BIE next decision
Only promote visual improvements on **measured** image-quality and stable frame-time evidence. Keep near-player actors physical and detailed, coarse-scale distant representation separately labeled, and never claim trillions of individuals executed an Experience cycle unless demonstrably measured.
