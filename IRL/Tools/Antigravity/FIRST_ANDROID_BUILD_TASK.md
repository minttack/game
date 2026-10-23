# First Antigravity task — BUILD THE ACTUAL IRL MOBILE GAME

You are a coding assistant **outside** the BIE THRIVES Experience runtime. Continue the ONE original game at \`minttack/game/IRL/IRL.uproject\`. Read the repository root \`AGENTS.md\` and \`IRL/Tools/Antigravity/README.md\` before taking action.

**Objective:** Compile the actual original IRL Unreal Engine 5.8 project, repair the first real blocking native C++/Blueprint or Android build error, then produce an Android **ARM64 Development APK** for my Moto G if the installed Windows toolchain allows it. This is not permission to install an app on my phone, spend money, publish, delete files, merge or force-push.

Work only on the isolated current feature branch/worktree. First report the exact git branch, SHA, status, installed UE version, real original project path, open IRL level and active GameMode/PlayerController/Pawn classes. Inspect these through Unreal MCP if connected. Do not build an unrelated replacement game, fake assets, procedural standalone demo, or synthetic APK.

Run the read-only diagnostic:
\`py -3 IRL\Tools\Antigravity\irl_antigravity_preflight.py --strict-toolchain\`

**If UE 5.8 is available:**
1. Open \`IRL/IRL.uproject\`, inspect C++ build log/UHT, compile \`IRLEditor\` using actual UE tools; show the first actionable failure (file/line/error) and fix that minimum original source error. Rebuild and repeat until compile succeeds or identify a real external blocker.
2. Use Unreal MCP with Ask/approval for any asset writes. Verify default Blueprint GameMode/Controller/Character truly use \`AIRLGameMode\`, \`AIRLPlayerController\`, \`AIRLCharacter\`. Keep user-approved original map and existing project source intact.
3. For Android use the existing \`IRL/Tools/Visual/IRL_BUILD_ANDROID_APK_WINDOWS.bat\` and evaluate its JSON/UAT logs. Preserve arm64 SDK35 mobile forward/profile settings and ADB-only deployment; do not restore insecure Android File Server or desktop ray tracing/Lumen on Moto G.
4. The original forest artwork is **not necessarily a cooked \`.umap\`**. Build original existing IRL playable map first; add actual imported forest only if Unreal can verify it. Do not invent screenshots.
5. Only if REAL RunUAT produces a valid \`.apk\`, report exact saved path, size, SHA-256, original commit, cooked map and UAT exit status. Do not call CI fake APK tests a game. Do not install or launch on device without my explicit authorization.

**If UE/SDK is missing:** Do not create a new Unreal project, install unknown utilities or invent a build result. Report the exact prerequisite and the shortest approved fix. Use tests to verify any code-level changes possible without UE, and request approval for a machine installation.

At completion, provide an evidence ledger:
- Branch/commit and files modified.
- Actual Unreal build/error output and editor/PIE results, or why unavailable.
- Actual APK path/checksum if one exists; otherwise **NO APK BUILT**.
- Phone testing clearly \`NOT_RUN\` until physical authorized Moto G observation.
- Decisions preserved: 026 coexistence of freedom and guidance, 029 minimal restrictions and security, 030 highest demonstrable advancement.
- BIE THRIVES runtime independent and **NO LLM embedded**.
- Next smallest experiment based on observed data.

Never merge main, silently replace assets, or declare IRL finished.
