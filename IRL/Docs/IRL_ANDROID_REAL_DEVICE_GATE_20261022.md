# IRL — First real Android device launch evidence (2026-10-22)

## ONE game, repository and dependency stack
Original Unreal Engine 5.8 game: https://github.com/minttack/game/IRL. Verified main remains \`261cbbbb8264dfde6943cd0fa304029d4867dd3e\`; this independent draft is built on mobile input PR #12 (and mobile packaging #11 / graphics and forest PRs #6–#10). The creator's decisions 026/029/030 remain in force; BIE THRIVES Experience is standalone non-LLM. Other parallel life/ecology/human duo PRs #1–#5 are still pending integration. Do not replace them or call this a separate game.

## Actual blocker
Existing Android work had a Windows UE5.8 Development APK packager with a static APK integrity check and native dual-stick movement source tests. **No tool verified that a real installed app starts and remains alive and foreground on the Moto G**. Passing a fake RunUAT test or merely seeing an APK file must not be promoted to "playable mobile game".

## Implementation
- \`IRL/Tools/Visual/irl_android_device_smoke.py\`: stdlib-only command-line test using an already installed \`adb\` (Android SDK platform-tools) and a connected authorized Android phone. **Read-only by default**: validates the original IRL Unreal project identity, lists devices, handles unauthorized/offline or multiple devices, reads Android model/OS SDK/CPU ABI, and checks the actual \`com.bieexperience.irl\` app is installed. Does not save the phone's serial or install anything.
- Only when the creator explicitly invokes \`--run\`, launches the **already installed** original IRL app using Android's launcher intent and collects multiple distinct \`pidof\` and \`dumpsys activity activities\` foreground observations. Rejects app crashes, other foreground apps, SDK below 26, non-arm64 devices, launcher failure, missing IRL installation and missing authorization. Does not alter device settings or assume a screen tap worked.
- Stores each run as \`IRL/Saved/IRL/android_device_smoke_<timestamp>.json\` with the source, a hash (not raw value) of the device ID, device model/SDK/ABI, observation counts and exact failure reason. A valid result means only \`DEVICE_LAUNCH_AND_FOREGROUND_OBSERVED_NOT_GAMEPLAY_VERIFIED\`. No screenshots or private logcat content are captured automatically. Optional \`--apk-report\` links verified source APK file SHA-256 to the build report, with an explicit note that this doesn't prove the installed app is the same binary.
- \`IRL_TEST_ANDROID_DEVICE_WINDOWS.bat\`: simple Windows launcher. Double-click does read-only preflight; append \`--run\` to explicitly launch.
- \`test_android_device_smoke.py\`: simulated ADB scenarios including success, unauthorized/ambiguous devices, missing package, non-arm64/too-old phone, failed launch, lost process, wrong foreground app, bad source evidence and incorrect game.
- CI executes only the fake-ADB tests; **no real device is accessible to GitHub CI**. If CI is green, that is source validation only, not a claim of a working Android APK or phone runtime.

## Practical phone validation
1. Compile/cook the actual original IRL Android Development APK in Unreal Engine 5.8 with required Android SDK, NDK and JDK. The prior \`IRL_BUILD_ANDROID_APK_WINDOWS.bat\` is the build entry point. No actual APK from these worker sessions has been demonstrated; do not download or install fake test APKs.
2. From Windows on the exact source checkout, install the real APK on an authorized Android development device using Unreal Editor's Android launch/install workflow (the smoke tool itself **never installs**). Connect via USB with USB Debugging enabled, trust the PC's RSA prompt, and ensure \`adb devices -l\` lists exactly one authorized phone.
3. Double-click \`IRL/Tools/Visual/IRL_TEST_ANDROID_DEVICE_WINDOWS.bat\` to check the device and installed package **without launching**.
4. To check actual app start/foreground, run:
   \`\`\`bat
   IRL\Tools\Visual\IRL_TEST_ANDROID_DEVICE_WINDOWS.bat --run
   \`\`\`
   With multiple authorized devices, add \`--serial <chosen_ADB_device_serial>\`. The serial is used only to target the tool call, never copied verbatim into the JSON report. Logs will explain any issue.
5. A successful smoke only says the Android OS reported IRL alive/foreground during several checks. **Human on-device controls remain separate**: move both axes, look on right stick, diagonal motion/recenter, jump press/release, Experience interactions; test pause/resume. Measure Android GPU/CPU frame times, p95/p99 FPS, memory, battery and thermal stability before any graphics upgrade is called efficient or photorealistic.
6. Evaluate first verified in-engine forest artwork, BIE life integration and human-duo multiplayer with the same devices and reproducible performance evidence. Never declare full mobile IRL finished based on partial features.

## Verification labels
- Code authored / on GitHub: **implemented candidate**.
- CI source tests (fake ADB): **must pass exact new run** before declaring them verified.
- Unreal Engine 5.8 compilation, actual Android APK and connected Moto G smoke: **NOT performed in this session**.
- Real finger controls, phone graphics/thermals, fully autonomous life, cross-phone multiplayer: **NOT verified**.

**BIE correction rule:** Promote a new capability only after observing the relevant independent external evidence. Startup is not gameplay and gameplay is not device thermal performance.
