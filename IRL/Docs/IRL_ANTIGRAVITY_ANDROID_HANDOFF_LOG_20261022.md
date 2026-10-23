# IRL candidate development log — Unreal MCP/Antigravity Android handoff (2026-10-22)

## Source of truth and integration
- One Unreal Engine 5.8 project: \`minttack/game/IRL/IRL.uproject\`.
- Inspected authoritative \`main\`: \`261cbbbb8264dfde6943cd0fa304029d4867dd3e\`. This Antigravity worker branch is **stacked on draft Android PR #15** at commit \`56bd98f5612adcfa520a04b40c5f6797a2cc81ff\`. It does NOT merge or replace any game version.
- Other unmerged workers: human-duo PR #1, BIE-independent life/ecology/evidence PRs #2–#5, separate forest assembly PR #14. None merged/overwritten here.
- Creator's 026/029/030 rules still apply. BIE runtime remains **non-LLM**. Antigravity can externally type source code and interact with Unreal MCP, never become BIE's internal cognition.

## Actual work
1. \`AGENTS.md\` at repository root — always-on authoritative one-game development, mobile-first priorities, safe editing and evidence rules. Google Antigravity officially recognizes this file.
2. \`IRL/Tools/Antigravity/README.md\` — official Google Unreal Engine 5.8 MCP / Antigravity setup, no unauthorized remote exposure, license/source restrictions, first real native Editor and ASTC Android build action.
3. \`mcp_config.EXAMPLE.json\` — non-active local \`127.0.0.1:[YOUR_PORT]\` endpoint template; actual port and permissions require user-side setup.
4. \`FIRST_ANDROID_BUILD_TASK.md\` — exact next single-game agent instruction: verify original Blueprint ancestry, compile UE \`IRLEditor\`, fix the first actual native failure, run real Android \`BuildCookRun\`, verify APK fingerprint, then request creator approval before phone installation.
5. \`irl_antigravity_preflight.py\` — read-only identity/source/toolchain diagnostic and explicit \`NOT_RUN\` device/build labels. Not a substitute for Unreal compilation.
6. \`test_antigravity_preflight.py\` and extended source GitHub CI.

## Verified evidence
- Official Google documentation: https://developer.android.com/games/engines/unreal/unreal-mcp-antigravity documents enabling Unreal MCP + All Toolsets and local Antigravity IDE MCP connection beginning UE 5.8. https://www.antigravity.google/pricing confirms a $0 Individual option with limits; https://www.antigravity.google/docs/rules documents \`AGENTS.md\`.
- GitHub Actions source CI **run 39876927718** on tested code commit \`69afabe4d404fb65c6bfe6079a2b722d49ef7d79\` completed **SUCCESS**. \`11/11\` read-only Antigravity project/toolchain checks passed. Inherited Android source-safety \`17\` cases, fake UAT \`12\` cases, mobile joystick C++17/UBSan \`13/13\` each, fake ADB \`14\` cases, PIE evidence \`21\` policy cases and original PBR source tests passed. See https://github.com/minttack/game/actions/runs/39876927718.
- An initial run failed due to a **case-sensitive test assertion** for the capitalization of the project's always-on rule text. That test was corrected to assert actual \`AGENTS.md\` content; rerun succeeded. No engine/runtime failure is implied.

## Strictly not verified
- Antigravity installation/sign-in, MCP local port, live UE Editor connection, UE5.8 native compilation, actual \`.umap\` generation, PIE screenshot/movement, Android ASTC \`.apk\`, physical Moto G installation, real FPS/thermal/memory, multiplayer and autonomous creature behavior. These did **not** occur inside this ChatGPT session.

## Next highest-priority experimental move (on actual Windows UE workstation)
Open this **exact existing** IRL checkout in Antigravity + UE5.8; run \`py -3 IRL\Tools\Antigravity\irl_antigravity_preflight.py --strict-toolchain\`, enable Unreal MCP on \`127.0.0.1\` with Ask-only mutation permissions, then paste \`FIRST_ANDROID_BUILD_TASK.md\` to obtain the first **real C++ compiler/error log** and correct it, followed by a **genuine** Android ASTC development APK. No auto-install/release/merge.

**Evidence stage: source-implemented and host-CI-tested, NOT UE-compiled or Android-tested.** This is a candidate-only log because the master state/decision ledger on the separate unmerged evidence PR #5 is not accessible as an established shared integrated ledger; do not imply a master record update or main merge.
