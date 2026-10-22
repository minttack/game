# IRL — First Real Forest Gameplay & Screenshot Gate
**Worker candidate: 2026-10-22. ONE original IRL Unreal Engine 5.8 project.**

## Continuity
- Source: \`minttack/game/IRL\`, authoritative \`main\` remained \`261cbbbb8264dfde6943cd0fa304029d4867dd3e\` at inspection; this work continues **unmerged** forest validation PR #9 (parents PR #8 collision, #7 original PBR, #6 Android adaptive graphics).
- This is NOT a new game, web demo or replacement for IRL First Signal, Motion Bloom, Resonance Garden, BIE autonomous life, human duo/world networking, or other concurrent workers. BIE THRIVES stays independent from LLM runtimes; decisions 026, 029 and 030 unchanged.
- The game is **not** an Android APK or AAA finished scene yet. No UE runtime execution happened in this session.

## Improvements implemented
1. New \`IRL/Content/Python/test_irl_forest_pie.py\`: Unreal **PythonAutomationTest** plugin script. Loads the actual non-destructive visual test level; first invokes the previously authored editor-world collision audit; requests real Play-In-Editor; waits for a **possessed Character with real capsule**, waits 90 editor frames for grounding, measures 45 frames of passive/no-input drift, then applies actual CharacterMovement input over 75 ticks and checks grounded distance after 12 ticks. Reads physical line-trace hit and impact normals for the character under both controlled and treatment conditions; never teleports the pawn. Saves source-reported results to \`Project/Saved/IRL/forest_pie_player_test_*.json\` and ends PIE, including failure handling. This script is **not tested inside UE** and UE Blueprint inheritance/collision may require correction.
2. New pure non-LLM policy \`forest_pie_evidence.py\`: requires a *real possessed character* and EXACT three named samples (before control, after no-input, after input); authentic terrain hits, walkable slope and capsule-foot clearance; sane position within the bounded forest tile; no-input drift at most 35cm; independent post-input movement at least 50cm and at most 3000cm. A drifting/sliding character does not count as proof of input-based locomotion. Labels result \`PIE_REVIEW_ELIGIBLE\`, never "verified Android gameplay". The source string itself is not authenticated and the value comes from the engine script.
3. \`IRL/Content/Python/test_irl_forest_screenshot.py\`: Unreal AutomationScheduler latent screenshot test. Loads the actual scene, requires the ground/biome editor audit to pass, sets repeatable camera position, requests a 1280×720 *real Unreal viewport screenshot*, waits up to 300 editor ticks, checks a readable PNG exists under the project Saved folder, records filename, dimensions, byte size and SHA-256 to \`Project/Saved/IRL/forest_genuine_screenshot_evidence.json\`. This is source code for capturing a true game-engine screenshot; it **has not generated one** here.
4. \`forest_screenshot_evidence.py\`: standalone PNG magic, IHDR dimensions, chunk CRC, IDAT/IEND and trailing-bytes validator without additional Python dependencies. Prevents treating a copied label or incomplete file as screenshot proof.
5. New Python host tests \`test_forest_pie_evidence.py\` and \`test_forest_screenshot_evidence.py\`, CI Python syntax compilation of automation scripts, and updated \`.github/workflows/irl-original-graphics.yml\`.

## Verified results
- GitHub Actions **run 39838110291**, branch head \`d7fb83cd7b022d27fce3d8e91a8de6330deef82a\`, outcome \`success\`. Native Python test logs show:
  - **21/21** source-assessed PIE-policy scenarios PASS (includes no-input control, drift, wrong maps, unsafe capsule, missing actual motion, NaN, missing possession).
  - **8/8** PNG integrity scenarios PASS.
  - **18/18** editor source-evidence policy groups PASS.
  - **5/5** mocked editor-probe scenarios PASS.
  - PBR generator deterministic **17 matching file hashes**, three valid triangulated OBJ source meshes, validated original 16-source-asset SHA-256 manifest.
  - Workflow generated original source art artifact \`IRL-Original-Mobile-PBR-Source-512\` with Artifact ID \`12452420554\`.
- **NEVER interpret these as a passed Unreal editor, PIE playtest or physical Android/mobile FPS test.** GitHub Actions runner only ran Python logic and mock editor contract. Unreal 5.8 executable and project were not built/run.

## How to run genuinely in Unreal (same original game)
1. Check out or create verified integration of graphics PR #6 → PBR PR #7 → collision PR #8 → forest probe PR #9 on the actual Windows UE5.8 project; keep main and gameplay systems backed up. Build C++ module and confirm IRL native GameMode and PlayerController Blueprint ownership.
2. Run original PBR generator, enable both **Python Editor Script Plugin** and **PythonAutomationTest** editor plugin, restart Unreal, and run \`IRL/Tools/Visual/run_irl_forest_validation.py\` to import original materials and create/verify isolated \`Lvl_IRL_Forest_VisualValidation\`.
3. Go to **Tools → Test Automation**, locate project Python tests \`test_irl_forest_pie\` and \`test_irl_forest_screenshot\`, execute inside the actual Unreal Editor session. Epic's official UE5.8 Python editor testing docs explain \`@unreal.AutomationScheduler.add_latent_command\` and screenshot ticking: https://dev.epicgames.com/documentation/unreal-engine/write-editor-tests-with-python-in-unreal-engine ; test runner: https://dev.epicgames.com/documentation/unreal-engine/run-automation-tests-in-unreal-engine
4. Confirm actual reports exist in \`Saved/IRL\` and screenshot is a real PNG. If no file or a check failed, do NOT report success; use failing evidence to fix Unreal API/world physics/asset import. Never treat source-code images or concept-art previews as a rendering screenshot.
5. Only after a genuine engine playtest is green: package for Moto G, test a scripted walk route and BIE life interactions with CPU/GPU p95/p99 frame times, memory, thermals and battery. Compare against the original phone rendering baseline.

## Immediate next integration blockers
- UE 5.8 compile of graphics C++ and real editor Python API: **unverified**.
- Real visual-test map \`.umap\` source/rendering, valid collision, HISM instances and screenshot: **unverified**.
- Physical Android APK, 2-human networking, persistent learning and animal life: **unverified**.
- Realistic AAA scanned art: still requires licensed original scans and art direction work. Procedural source materials are starters.
- Before merge refresh main, test all concurrent IRL workers, resolve GameMode/PlayerController and level conflicts, and preserve the one-game decision ledger.

**Disposition:** actual host-tested instrumented Unreal automation source committed; Unreal runtime implementation **pending engine execution**, no finished game or released APK.
