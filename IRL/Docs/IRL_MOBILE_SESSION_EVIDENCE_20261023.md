# IRL — Android On-Device Frame & Touch Evidence (2026-10-23)
**One game:** \`minttack/game/IRL\`, Unreal Engine 5.8. **One development history.**

## Parent and existing capability
This feature branch is stacked on unmerged Android graphics/security PR #15, which descends from touch controls PR #12, development APK PR #11, native/editor verification PR #10 and their upstream graphics/forest source PRs. Authoritative \`main\` remained at commit \`261cbbbb8264dfde6943cd0fa304029d4867dd3e\` when checked. Current original two-human, creature/biome, life and evidence workers are separate unmerged work and MUST NOT be overwritten. Creator decisions 026/029/030 and standalone non-LLM BIE THRIVES remain unchanged.

## Gap addressed
IRL previously adapted the local graphics tier using **mean frame delta** and logged only occasional tier switches. The Moto G has not been connected and there are no real device frame traces; the code couldn't distinguish gameplay input callbacks from assumed touchscreen behavior, or provide a stable p95/p99 frame-pacing record on an actual Android session.

## Implemented actual IRL code
- \`Source/IRL/Mobile/IRLMobileEvidenceCore.h\`: **independent C++17, non-LLM kernel**: bounded 1024 frame intervals (no heap allocations per frame), 10-second steady-state windows, nearest-rank p50/p95/p99, max and mean frame delta, rejected invalid/paused/loading samples, counters for move/look **axis callbacks** and Jump/Experience **press callbacks**. Reset each window. Does NOT measure GPU frame time or read private user input.
- The **existing** \`UIRLAdaptiveMobileFidelityComponent\` now logs one local-only Android \`IRL_MOBILE_EVIDENCE_V1\` structured UE log line each window, including a generated per-process-session identifier, monotonic sequence, valid/rejected samples, frame time percentiles, tier and input callback counts. Adaptive tier decisions still use existing unmodified BIE-oriented frame budget. Desktop and remote controllers are unaffected.
- The **existing** \`AIRLPlayerController\` records meaningful nonzero movement/look axis callbacks; the existing native Jump and Experience button handlers record presses. No new UI, networking, file storage permission or language-model runtime is introduced. No personal coordinates or raw touch trajectory are recorded. Counts do NOT prove physical finger touch or movement succeeded.
- \`Tools/Visual/irl_mobile_evidence_report.py\`: parses **only** the tagged IRL UE log lines from an optionally provided log file (not authenticated) or an explicitly authorized ADB logcat read (\`--adb\`). Enforces session grouping, unique monotonic sequence, finite percentile ordering, plausible frame counts/duration and at least two windows. Aggregates **frame-count-weighted mean**, median of per-window p95 and worst per-window p99 (never falsely labels these as global frame percentiles). Does not save raw unrelated phone logs or expose raw ADB serial. Output under \`IRL/Saved/IRL/irl_mobile_evidence_*.json\`.
- \`Tests/host_irl_mobile_evidence.cpp\`, \`Tools/Visual/test_irl_mobile_evidence_report.py\`, and GitHub CI compile + UBSan for pure C++ core, Python ingestion tests including rejecting malformed/double-counted sessions and filtering unrelated Android log content.

## Actual Android workflow (requires a REAL compiled APK)
1. Checkout this exact stacked branch of **the same IRL project** on Windows and build in Unreal Engine 5.8 with SDK/NDK installed. Compiling source is a prerequisite, not something this ChatGPT execution has achieved.
2. Run the original \`IRL_BUILD_ANDROID_APK_WINDOWS.bat\`; require real UAT cook and valid \`.apk\`, not GitHub fake build tools. Install the real package in an authorized Moto G via Unreal/ADB only with creator action.
3. Launch the installed IRL game and leave it running for **at least 30 seconds**. During the measurement, actually use left joystick movement, right joystick camera, Jump and Experience. Use the prior optional ADB smoke script to verify package foreground, but never infer gameplay from it.
4. From the original \`IRL\` folder execute:
   \`\`\`powershell
   py -3 Tools/Visual/irl_mobile_evidence_report.py --adb --project-root .
   \`\`\`
   Alternatively capture logcat yourself to text, then use \`--file path_to_logcat.txt\`, explicitly labelled **EXTERNAL_LOG_FILE_NOT_AUTHENTICATED**.
5. Inspect \`Saved/IRL/irl_mobile_evidence_*.json\` for observation counts, weighted mean frame ms, mean-derived FPS, per-window p95 and p99, and input callback counts. If no valid markers appear: Unreal Android build might not have enabled IRL's native controller, logcat may not retain the window, or the app failed to run; do NOT invent a performance record.
6. Later, pair these measurements with UE/Android native GPU profiling, actual texture quality, thermals/battery and a repeatable camera/locomotion path. The first results may expose missing joysticks, unsustainable settings, or shader stalls—then choose the next BIE improvement using evidence.

## Explicit evidence boundaries
- Host CI pass means portable C++ quantiles, parser and source wiring were tested, **NOT** UE C++/UHT compilation, physical Android app, finger responsiveness, GPU p95 or persistent BIE autonomous life.
- Values parsed from a file, even if they use the correct marker, **are not cryptographically authenticated**. ADB capture is source-context evidence, not independent engine instrumentation.
- An adaptive graphics tier can fluctuate with CPU-limited performance; changed graphics level is not a demonstrated visual-quality or GPU speed gain.
- APK build and actual Moto G performance remain unverified until reported from physical tooling. No fictional data or screenshots may be presented as actual.
