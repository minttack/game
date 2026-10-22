"""Static contract of IRL Android native joystick input wiring.

Checks exact source / no binary Unreal asset dependency. NOT runtime validation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
controller=(ROOT/"Source/IRL/IRLPlayerController.cpp").read_text(encoding="utf8")
header=(ROOT/"Source/IRL/IRLPlayerController.h").read_text(encoding="utf8")
touch=(ROOT/"Config/DefaultInput.ini").read_text(encoding="utf8")
char=(ROOT/"Source/IRL/IRLCharacter.cpp").read_text(encoding="utf8")
tests={
"Android virtual joysticks enabled":"DefaultVirtualJoysticks" in touch,
"four independent joystick axes":all("EKeys::Gamepad_"+axis in controller for axis in ("LeftX","LeftY","RightX","RightY")),
"X and Y accumulated":controller.count("EInputActionAccumulationBehavior::Cumulative")==2,
"two actions are axis2d":controller.count("EInputActionValueType::Axis2D")==2,
"two Y axes swizzled":controller.count("EInputAxisSwizzle::YXZ")==2,
"mapping priority above blueprint":"AddMappingContext(NativeMobileInputContext, 20)" in controller,
"native move calls existing character":"Character->DoMove(Clean.X,Clean.Y)" in controller,
"native look calls existing character":"Character->DoLook(Clean.X,Clean.Y)" in controller,
"character movement already exists":"void AIRLCharacter::DoMove" in char,
"character look already exists":"void AIRLCharacter::DoLook" in char,
"local controller guarded":controller.count("IsLocalPlayerController()")>=2,
"touch HUD Android forced":"#if PLATFORM_ANDROID\n    return true" in controller,
"joystick jitter filtered":"IRLMobile::FilterJoystick" in controller,
"runtime context retained by GC":"UPROPERTY(Transient)\n    TObjectPtr<UInputMappingContext> NativeMobileInputContext" in header,
"both actions GC retained":header.count("TObjectPtr<UInputAction> NativeMobile")==2,
"original BIE button preserved":"void AIRLPlayerController::AdvanceIRLExperience()" in controller,
"no unverified screenshot code": "Screenshot" not in controller,
}
for name,ok in tests.items():
    assert ok,name
print("PASS",len(tests),"Android runtime-mapped joystick source checks (UE compile still required)")
