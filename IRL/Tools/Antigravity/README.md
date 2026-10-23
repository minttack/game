# IRL — Google Antigravity + Unreal MCP: First real Android build

**Status (2026-10-22): project integration instructions, not a running external agent.**
**ONE game:** https://github.com/minttack/game -> \`IRL/IRL.uproject\` (UE 5.8).
Android Moto G is the primary device target. Do not create a new game or web prototype.

## Why this is the next practical move

Google's Android Developers documentation (updated 2026-07-27) explicitly supports **Unreal Engine 5.8 Unreal MCP → Antigravity IDE**, allowing the agent to inspect and operate the **real open Unreal Editor**: https://developer.android.com/games/engines/unreal/unreal-mcp-antigravity

Google's official Individual Antigravity offering has a free tier with basic weekly rate limits: https://www.antigravity.google/pricing
Antigravity discovers repo-scoped \`AGENTS.md\` as always-on instructions: https://www.antigravity.google/docs/rules

This external developer assistant does **not** become the BIE THRIVES Experience intelligence runtime. It is allowed to write/test code and inspect the editor from outside BIE.

## Exactly which IRL branch to open

Open an isolated checkout or worktree of the current feature branch:
\`workers/irl-antigravity-unreal-mcp-20261022\`.
It contains the actual Android/graphics source stacked on PRs #15/#13/#12/#11 and forest PRs #10/#9/#8/#7/#6.

The repository's authoritative \`main\` is still a separate protected baseline, and branches for the autonomous-life, human-duo and experience-evidence workers are *not merged*. **Never replace the real game with a template.**

If the branch is not present in the local clone:
\`\`\`powershell
git fetch origin
git switch --track origin/workers/irl-antigravity-unreal-mcp-20261022
\`\`\`
If an existing worktree has uncommitted creator changes, **do not switch it**. Create an isolated worktree in a different folder after reviewing its current Git state. Only run the above in a clean checkout.

## Local prerequisites

- Windows 10/11 x64 with installed **Unreal Engine 5.8** and Visual Studio C++ toolchain.
- Android SDK 35, compatible Unreal 5.8 NDK/JDK (use Unreal's SDK Manager/Turnkey and inspect the actual project build log).
- Python 3.11+; dependencies for original procedural graphics if needed: \`numpy\`, \`pillow\`.
- Antigravity IDE for Windows: https://www.antigravity.google/download ; sign in and choose the $0 individual plan if eligible.
- Use only an authorized Android phone with USB debugging for **later** actual device tests; do not install apps without explicit creator approval.

## Connect Antigravity to Unreal, using Google's exact official workflow

1. Open the existing \`IRL/IRL.uproject\` **in Unreal Engine 5.8**.
2. In the Unreal Editor, **Edit → Plugins**, enable **Unreal MCP** and **All Toolsets**, and restart as prompted. These are editor-side tools, not BIE intelligence components.
3. **Edit → Editor Preferences → General → Model Context Protocol**, enable **Auto Start Server**. Restart Unreal or run \`ModelContextProtocol.StartServer\` in the editor console.
4. Determine the **actual port** from Unreal's MCP preferences / local server log. Never invent or assume a port. Ensure the MCP endpoint is bound only to **127.0.0.1**, not exposed to external addresses.
5. In Antigravity IDE, open the **Agent window → … → MCP Servers → Manage MCP Servers → View raw config**, and copy the \`mcpServers\` object from \`mcp_config.EXAMPLE.json\` into the IDE's own \`mcp_config.json\`, substituting the actual port. The \`_comment\` is informational and should NOT be copied into the actual Antigravity config.
6. Leave MCP execution on **Ask/approval** for scene mutations, terminal commands, source edits and installs. Do not select broad "Turbo" or approve wildcard tools without reviewing them.
7. Confirm connection with a **read-only** inspection of the existing open IRL map, its active GameMode, default PlayerController, pawn class, and Android platform settings. Do not create a sphere or other unrelated test level. **No Antigravity MCP session was executed by ChatGPT here.**

Official Android Developers tutorial:
https://developer.android.com/games/engines/unreal/unreal-mcp-antigravity

## One command to diagnose the real workstation (read only)

From the full repo checkout, in Windows PowerShell:
\`\`\`powershell
py -3 IRL\Tools\Antigravity\irl_antigravity_preflight.py --strict-toolchain
\`\`\`
Use \`--engine-root "C:\Program Files\Epic Games\UE_5.8"\` when needed.

The JSON output reports the branch, SHA, original game identity, UE editor/UAT executables if found, and missing toolchain paths. It **does not** build a game or install software. If the code lacks a local UE installation, Antigravity must report that blocker, not fabricate an APK.

## The actual FIRST build to ask Antigravity to perform

Paste the exact text of \`FIRST_ANDROID_BUILD_TASK.md\` into the Antigravity agent. It must:

1. Read \`AGENTS.md\`, \`git status\`, the real IRL project, and the existing mobile controls/Android build scripts. Inspect open Unreal editor over MCP if available; check actual Blueprint ancestry with \`IRL/Tools/Visual/audit_android_class_chain.py\`.
2. Compile \`IRLEditor\` **against installed Unreal Engine 5.8**, fix the **first real compiler/UHT failure** within an isolated branch, and rerun exact regressions. Do not manufacture a clean build report when UE is unavailable.
3. Invoke the existing \`IRL/Tools/Visual/IRL_BUILD_ANDROID_APK_WINDOWS.bat\` only after compile/source safety gate passes, to build **Android ARM64 Development ASTC**. Preserve exact native UAT logs and output artifact hash; original template map is the only explicitly cookable map until the forest \`.umap\` is genuinely generated and tested.
4. Verify generated APK's \`AndroidManifest.xml\`, \`classes.dex\`, arm64 native library, package identity, source commit SHA and CRC; do not make success claims without an actual Android package.
5. Ask before USB installation and launching on Moto G; only then run read-only \`IRL_TEST_ANDROID_DEVICE_WINDOWS.bat\` and explicit \`--run\` to verify process/foreground. Manual swipe/look/jump, 30 FPS p95/p99, temperatures and BIE interactions require physical measurements.
6. Return changed source files, copied log excerpts, actual APK path/hash (if built), tests with commands and results, and the smallest next blocker. **Never force-merge to main or overwrite creator assets.**

## Design and safety notes

- **Antigravity is an external developer coding agent**, not an add-on to BIE's independent non-LLM runtime.
- Project scope is the existing IRL repository, not unrestricted filesystem; no secrets, tokens or Android IDs in commits.
- Any Unreal MCP actions mutating assets require explicit creator review. Never place a second game in a new Unreal project.
- The approved alien forest/mountains/space artwork remains **concept art**, not a verified UE scene. Art fidelity improvement must follow measured mobile performance and actually imported/licensed assets.
- Source-only GitHub tests and generated fake APKs from fixture scripts **are not authentic Android packaging evidence**.

## Worker's integration status

\`AGENTS.md\`, preflight tests and this Antigravity guide are **source-implemented**. MCP installation/connection, local UE 5.8 compilation, rendered game screenshot, actual Android APK and physical Moto G controls/performance **not executed or confirmed in this conversation**. This branch remains a draft until the workstation tests and multi-branch integration gates are satisfied.
