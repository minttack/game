"""Static source-level contract for mobile IRL, no engine runtime assertion."""
from pathlib import Path
import configparser
import json
import re

ROOT=Path(__file__).resolve().parents[2]
project=json.loads((ROOT/"IRL.uproject").read_text(encoding="utf-8"))
assert project["EngineAssociation"]=="5.8"
assert any(p["Name"]=="IRL" for p in project["Modules"])
input_ini=(ROOT/"Config"/"DefaultInput.ini").read_text(encoding="utf8")
engine=(ROOT/"Config"/"DefaultEngine.ini").read_text(encoding="utf8")
game=(ROOT/"Config"/"DefaultGame.ini").read_text(encoding="utf8")
controller_h=(ROOT/"Source"/"IRL"/"IRLPlayerController.h").read_text(encoding="utf8")
controller_cpp=(ROOT/"Source"/"IRL"/"IRLPlayerController.cpp").read_text(encoding="utf8")
hud_h=(ROOT/"Source"/"IRL"/"Mobile"/"IRLMobileTouchHUD.h").read_text(encoding="utf8")
hud_cpp=(ROOT/"Source"/"IRL"/"Mobile"/"IRLMobileTouchHUD.cpp").read_text(encoding="utf8")

checks={
"two touch joysticks": "DefaultTouchInterface=/Engine/MobileResources/HUD/DefaultVirtualJoysticks.DefaultVirtualJoysticks" in input_ini,
"landscape mode": "Orientation=Landscape" in engine,
"ARM64 packaging": "bBuildForArm64=True" in engine,
"Android target 35": "TargetSDKVersion=35" in engine,
"Android min 26": "MinSDKVersion=26" in engine,
"IRL app identity": "ProjectName=IRL" in game,
"gameplay controller preserves BIE": "AdvanceIRLExperience()" in controller_h,
"HUD fallback class": "UIRLMobileTouchHUD::StaticClass()" in controller_cpp,
"HUD only for local player": "IsLocalPlayerController() && ShouldUseTouchControls()" in controller_cpp,
"does not require binary UMG": "if (!TouchClass)" in controller_cpp,
"jump supports press and release": "DoJumpStart()" in hud_cpp and "DoJumpEnd()" in hud_cpp,
"experience action": "Player->AdvanceIRLExperience()" in hud_cpp,
"HUD action overlays": "IRLJumpButton" in hud_cpp and "IRLExperienceButton" in hud_cpp,
"mobile HUD declared native": "class IRL_API UIRLMobileTouchHUD" in hud_h,
"widget uses hit-test transparent canvas": "ESlateVisibility::SelfHitTestInvisible" in hud_cpp,
"no untrusted phone direct install": "adb install" not in (ROOT/"Tools"/"Visual"/"irl_android_apk_runner.py").read_text(),
}
for name,passed in checks.items():
    assert passed, name
print("PASS",len(checks),"Android-first IRL source contracts; Unreal/phone tests still REQUIRED")
