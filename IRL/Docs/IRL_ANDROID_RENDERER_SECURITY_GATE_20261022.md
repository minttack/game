# IRL — Android Forward Renderer and Safe Build Gate
**2026-10-22 · ONE original game minttack/game/IRL · independent draft stacked on PR #13**

## Source and continuity
Authoritative main, as inspected, is \`261cbbbb8264dfde6943cd0fa304029d4867dd3e\`. This candidate builds on the Android launch evidence PR #13 (which builds on Android touch #12 and packaging #11). Graphics, forest, native validation and independent BIE/human-duo life branches remain separate. No new game, no irreversible merge, and no LLM within BIE THRIVES Experience. Preserve creator decisions 026 (autonomy plus guidance), 029 (minimal restrictions consistent with security), 030 (highest demonstrable quality).

## Prior issue and why
\`Config/DefaultEngine.ini\` still declares a desktop \`Maximum\` quality project with Lumen dynamic GI, reflections, virtual shadow maps, mesh distance fields, Substrate and ray tracing enabled. Unreal's documentation says Mobile Forward is the practical renderer and Lumen on Android is experimental, requiring high-end Vulkan SM5 and the desktop renderer. The low-cost Moto G has not been profiled or confirmed to support these desktop effects.

The project also had Android File Server enabled with network connections allowed and a **publicly committed access token**. An access token present in Git history must be assumed exposed and should not be reused. Epic documents AndroidFileServer uses only a basic, unencrypted security token and may be disabled for ADB-based deployment.

## Changes made in source
1. New \`IRL/Config/Android/AndroidEngine.ini\` selects **Android Mobile Forward (\`r.Mobile.ShadingPath=0\`)**, no Lumen GI/reflections, ray tracing, distance fields, virtual shadow maps or Substrate; retains \`r.MobileHDR=True\` for lit material fidelity in a measured pilot; disables costly Android-only motion blur, depth of field, post-process bloom (GPU effect, distinct from BIE BLOOM cognition) and volumetric fog. This is a **platform-specific override**, not a global desktop renderer rewrite.
2. Existing \`DefaultEngine.ini\` AndroidFileServerRuntimeSettings now sets \`bEnablePlugin=False\`, \`bAllowNetworkConnection=False\`, \`bIncludeInShipping=False\`, \`bAllowExternalStartInShipping=False\`, \`SecurityToken=\` (blank) and retains \`ConnectionType=USBOnly\`. Android file-server is NOT required for the existing full APK \`BuildCookRun\` workflow or USB ADB. **Previous published token should be considered compromised and retired everywhere**; merely replacing its current value does not purge prior Git history.
3. \`IRL/Tools/Visual/android_renderer_gate.py\`: pure Python source-check policy verifies that the *original* desktop renderer continues to use its desktop values, while Android platform-specific overrides contain required mobile low-cost options; asserts no AFS deployment exposure, ARM64 SDK35 GLES3.2 packaging, and existing Low/Mid/High phone-specific texture pools 96/160/256MB.
4. \`irl_android_apk_runner.py\` now **refuses** to invoke \`RunUAT BuildCookRun\` if the Android rendering/security source policy fails, with \`NOT_ESTABLISHED\` status and an actionable JSON error.
5. \`test_android_renderer_gate.py\` exercises a clean copy of the actual project configuration and fail-closed cases, including changing renderer to deferred, enabling Lumen, enabling Vulkan unexpectedly, enabling AFS or its network interface, reintroducing an access token, enlarging the low-end texture pool, deleting the Android override, or overwriting the original desktop renderer. \`test_android_apk_runner.py\` imports the REAL source configuration into its fake-UAT fixture and tests preflight rejection before executing a fake UAT.
6. CI runs these tests; no claim of UE/GPU validation from Python tests.

## Actual evidence/status
- Source code and INI changes committed on this isolated draft branch; CI must be checked for green run on exact head before claiming source tests passed.
- **Unreal 5.8 C++ build, Unreal's cooked configuration precedence, an Android APK, real display screenshot, Moto G joystick controls, 30FPS, battery temperature and two-human/BIE life gameplay remain unverified.**
- This is a safer, cheaper renderer **candidate**. No measured FPS gain is claimed.

## Required next gates to finish a mobile release
1. In a Windows Unreal Engine 5.8 editor, check out the exact stacked branch in the **existing IRL project**. Compile the original GameMode/PlayerController and verify Blueprint spawn ancestry; do not overwrite the original Unreal level. Run \`Tools/Visual/audit_android_class_chain.py\`, correct any actual Engine errors.
2. Run \`IRL_BUILD_ANDROID_APK_WINDOWS.bat\` with SDK35, NDK27c, JDK21; require a new full-arm64 Development APK and inspect real UAT logs. Record actual cooked \`Engine.ini\` and Android device profile to verify renderer CVars take effect as intended, not merely present in source.
3. After user-authorized USB installation on Moto G, run \`IRL_TEST_ANDROID_DEVICE_WINDOWS.bat\` with and without explicit \`--run\`. Prove launch and foreground survival; play-test all touch axes and BIE Experience button and verify actual multiplayer after separate integration.
4. Use Unreal Insights + Android native platform tools for repeated matched-path FPS p95/p99, memory, GPU and thermal measurements. Tune mobile HDR, shadows, textures and adaptive graphics tiers based on **real** phone evidence and visual-quality comparison. Avoid untested claims.
5. Reconcile unmerged human duo, grounded ecology, BIE evidence and autonomous life workers through verified feature branches; do not force merge into main.

References:
- Epic UE 5.8 Android renderer: https://dev.epicgames.com/documentation/en-us/unreal-engine/mobile-rendering-and-shading-modes-for-unreal-engine
- Epic UE 5.8 Android device profiles: https://dev.epicgames.com/documentation/unreal-engine/customizing-device-profiles-and-scalability-in-unreal-engine-projects-for-android
- Epic UE 5.8 Android file server and tokens: https://dev.epicgames.com/documentation/unreal-engine/android-file-server-for-unreal-engine
- Epic UE 5.8 profiling mobile: https://dev.epicgames.com/documentation/unreal-engine/profile-android-projects-with-platformnative-tools

**Disposition:** actual source configuration optimized and hardened; engine rendering, performance and APK still gated by real hardware evidence. 
