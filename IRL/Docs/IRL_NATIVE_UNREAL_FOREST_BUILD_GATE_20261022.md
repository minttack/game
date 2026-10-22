# IRL — Native Unreal 5.8 Windows Forest Build Gate
**2026-10-22 — ONE original minttack/game IRL project — draft continuation of PR #9**

## Highest-impact verified next step
The existing source has original material generators, a scene builder, forest ground-collision auditing, first PIE movement code and a real PNG capture automation script. All prior GitHub tests were **Python logic and mocks**: none compiled Unreal, placed a real forest map, checked actual player physics or measured Android FPS. This branch closes the operator/execution gap, not the renderer-art gap.

## Implemented in this candidate
- \`IRL/IRL.uproject\`: enables four **Editor-only** plugin dependencies: \`PythonScriptPlugin\`, \`EditorScriptingUtilities\`, \`PythonAutomationTest\` and \`FunctionalTestingEditor\`. No runtime LLM, no Android dependency, original Maps/Gameplay untouched. Plugin resolution and compilation still require UE 5.8.
- \`IRL/Tools/Visual/IRL_BUILD_AND_VERIFY_FOREST_WINDOWS.bat\`: start native validation by double-click from a **full IRL source checkout** on Windows; forwards optional \`--engine-root\` to Python runner, displays failure/success with accurate wording.
- \`irl_native_forest_runner.py\`: verifies genuine \`IRL.uproject\` engine association and native Editor target, discovers native UE 5.8 installation or accepts \`--engine-root\`, generates original non-downloaded PBR art if absent (will not overwrite an unfamiliar existing Generated folder), verifies the 16 source files against original SHA-256 manifest, compiles **IRLEditor Win64 Development** via UE \`Build.bat\`, invokes actual \`UnrealEditor-Cmd.exe\` **full editor** with Epic-documented \`-ExecutePythonScript\`, then **recomputes** source-observation assessment against a **freshly emitted report** from \`probe_unreal_forest.py\`. Records exact native command, exit statuses, SHA-256 logs, failure reason, source git commit and verdict to \`Project/Saved/IRL/native_forest_run_*.json\`.
- A clean exit alone **cannot pass**. Reject if the editor didn't write a NEW valid report after launch, if report source/map wrong, if tested observations fail, if native build fails, if engine wasn't found or assets are malformed.
- \`--mode preflight\` checks prerequisites without calling engine, with explicit \`ENVIRONMENT_READY_NOT_ENGINE_TESTED\`. \`--mode audit-only\` is for a manually precompiled exact source tree. Both modes preserve the original map and all other IRL worker branches. Never auto-merge/checkout.
- \`test_native_forest_runner.py\`: ten cross-platform mocked command invocations including build/editor exit failure, missing/stale/wrong-map/insufficient reports, wrong UE version and missing engine. **Mocks do not prove native Unreal compilation.**

## Native execution steps on the user's Windows computer
1. Ensure that this **exact feature branch stack** and its parents PRs #6, #7, #8, #9 are checked out in the **same repository** \`minttack/game\`; the branch includes their code. Do not replace/overwrite \`main\`.
2. Have a properly installed **Unreal Engine 5.8** with Windows C++ toolchain, a current Python 3.11+ launcher (\`py -3\`), and \`numpy pillow\` Python packages (\`py -3 -m pip install numpy pillow\`). No external game art license is downloaded; generated original source is included or created.
3. **Double-click** \`IRL/Tools/Visual/IRL_BUILD_AND_VERIFY_FOREST_WINDOWS.bat\`. If UE is not under the usual location, run from PowerShell or CMD:
   \`\`\`bat
   IRL\Tools\Visual\IRL_BUILD_AND_VERIFY_FOREST_WINDOWS.bat --engine-root "D:\Epic\UE_5.8"
   \`\`\`
   The batch file detects project root via its location and never switches branches.
4. Read the generated \`IRL/Saved/IRL/native_forest_run_*.json\`, \`unreal_build_*.log\`, and \`unreal_editor_*.log\`. The editor audit itself writes \`forest_editor_audit_*.json\`. \`NOT_ESTABLISHED\` means **inspect the actual named failure**, do not claim success.
5. Only if \`EDITOR_REVIEW_ELIGIBLE_NOT_PLAYABLE_OR_ANDROID\` appears **from an actual Windows run** should the human operator use Unreal Editor's Tools → Test Automation for \`test_irl_forest_pie\` and \`test_irl_forest_screenshot\`. These are **not executed by this runner**. They remain independently unverified, and real Android packaged-device tests come afterward.

## Local and CI verification
- Local Python \`compileall\` for comparable runner source and standalone **10/10 mock process-control groups** passed. This test uses fake Build.bat/UnrealEditor-Cmd.exe files and a deliberately trivial fake source scorer to exercise orchestration, not Unreal.
- Repository CI includes this test, the existing 21 PIE-policy checks, 8 PNG integrity checks, 18 scene evidence policy groups and original art topology/checksum tests. **A new GitHub Actions run is required before calling the actual committed source CI-passed.**
- Official command line use is documented by Epic at https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python and automation report syntax at https://dev.epicgames.com/documentation/unreal-engine/run-automation-tests-in-unreal-engine.
- **No UE 5.8 installation was available inside this ChatGPT runtime**, so no actual native build, Editor world, PNG screenshot, Android APK or FPS result has been claimed.

## BIE THRIVES honest limitation
The runner is external development tooling implementing the BIE sequence Memory → Observation → Prediction → Action → Evidence → Correction. It is **not the independent BIE THRIVES Experience runtime**. It doesn't invent creature intelligence, life evolution or arbitrary performance results. Preserve decisions 026 (autonomy+guidance), 029 (minimal restrictions/security), 030 (highest demonstrable capabilities). Proceed next to native engine test, real screenshot and device measurements.
