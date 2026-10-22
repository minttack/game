# IRL — Android Runtime Joystick Control: Next Verified Gate
**October 22, 2026 — ONE original IRL Unreal Engine 5.8 game**

## Continuity
Source of truth remains `minttack/game/IRL` on `main` (at inspection `261cbbbb8264dfde6943cd0fa304029d4867dd3e`). This candidate is a **stacked draft on Android-first PR #11**, which itself depends on the unmerged graphics/forest/native UE PRs #6–#10. The separate two-human, BIE Experience/learning, ecology, replication and evidence PRs #1–#5 were not merged, overwritten or falsely promoted. Preserve creator Decisions 026, 029 and 030, and keep BIE THRIVES independent from any LLM runtime.

## Real blocker found
PR #11 enabled the engine dual virtual joysticks in `DefaultInput.ini` and created a native Jump/Experience action overlay, but **no verified mapping** connected their `Gamepad_LeftX/LeftY/RightX/RightY` events to the C++ `AIRLCharacter::DoMove/DoLook` pathways. Default `IMC_Default.uasset` bindings are binary and not inspected. A phone could show a joystick while its character fails to move.

Even an excellent APK packager cannot solve this missing runtime input linkage.

## Implemented
- Extends the **existing** `AIRLPlayerController` on the Android development branch with four native `EKeys` mappings (LeftX, LeftY, RightX, RightY), owned as transient UPROPERTY objects; installs a local-player `UInputMappingContext` at priority 20 only for touch use. The higher-priority actions consume lower-priority joystick mappings, helping avoid double movement from Blueprint input assets; desktop keyboard/mouse contexts remain untouched.
- Both `UInputAction` inputs have `Axis2D` value type and **Cumulative** accumulation; otherwise Enhanced Input's default TakeHighestAbsoluteValue policy discards the weaker joystick axis. Both Y mappings use `UInputModifierSwizzleAxis::Order=EInputAxisSwizzle::YXZ` to turn 1D Y into second component. Unreal's published Enhanced Input docs support these APIs: https://dev.epicgames.com/documentation/unreal-engine/enhanced-input-in-unreal-engine
- Callbacks `HandleMobileMove`/`HandleMobileLook` require local controller, get the actual possessed `AIRLCharacter`, apply bounded non-LLM radial deadzone/normalization via `IRLMobileJoystickCore.h`, then call **existing** `DoMove`/`DoLook`. When the control returns to center, stale input is not intentionally carried forward.
- Android `ShouldUseTouchControls` is explicitly true via compile-time platform guard, so the native touch UI isn't accidentally skipped due a delayed virtual-joystick Slate initialization; desktop may still opt into touch via existing `bForceTouchControls`.
- No changes to network authority, BIE game objectives, two-person spawn, actual world physics, skin/UI art or original level.
- Added Unreal C++ automation-source check `IRL.Mobile.JoystickMath`; portable C++17 test runner, Python source-contract tests, and read-only Unreal **Blueprint class parentage audit**. The editor audit inspects the **actual binary** GameMode CDO and default PlayerController/Pawn class. If the Blueprint doesn't inherit `AIRLGameMode`, `AIRLPlayerController`, and `AIRLCharacter`, it fails closed and records `Project/Saved/IRL/android_blueprint_class_audit.json` instead of claiming touch bindings are active. It does NOT modify binary Blueprint files.
- CI extended to compile and run the actual native C++17 joystick math in Linux and UBSan, while source tests assert all four axes, modifiers, BIE action retention and priority. The mocked editor class audit is separate from a real UE Editor read.

## Truthful test categories
- Python source tests verify written code and configuration, not that UE built it or processed a real finger touch.
- Portable C++17 tests prove radial deadzone, diagonal normalization, invalid input rejection. They do not compile UHT-generated mobile UI or native Unreal input APIs.
- Editor mock inheritance tests prove fail-closed control flow. **Only a real Unreal Editor run can prove the bundled BP uses the correct native class chain.**
- **Actual UE 5.8 compile, Android cook, real APK file, Moto G joystick movement, physical FPS/thermal/battery, multiplayer and BIE creature behavior remain UNTESTED** until specific future evidence exists.

## Actual mobile validation now
1. In the **one original project**, check out this stacked graphics/mobile worker version, compile in UE 5.8 (with Editor + Android SDK 35/NDK r27c). Keep main unchanged.
2. Run Unreal Editor `Tools → Execute Python Script` for `IRL/Tools/Visual/audit_android_class_chain.py`. Require `EDITOR_CLASS_CHAIN_REVIEW_ELIGIBLE`; if it fails, change the correct existing Blueprint parent class only after inspecting the actual asset, not by silently replacing the entire game.
3. Run `IRL_BUILD_ANDROID_APK_WINDOWS.bat` from full IRL source to cook Development Android/ASTC. Require an actual APK, not the CI fake UAT output, plus authenticated package install into the physical Moto G via authorized device workflow.
4. Run mobile locomotion matrix: left X/right, left Y/forward/back, diagonals, right yaw/pitch, stop/recenter/deadzone, JUMP press/release, EXPERIENCE when in range, app pause/resume and OS rotation. Log any input failures from UE device logs.
5. Record real 30 FPS target comparison including p95/p99 CPU and GPU frame time, streaming texture budget, thermals and sustained battery impact. Then bring the original forest into the Android level and integrate independent BIE ecological life and second player after verified networking.

**Disposition:** candidate code implementation, host tests pending exact CI, UE compile/phone test not performed.
