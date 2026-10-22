"""Android-first IRL BuildCookRun contract checks using FAKE executables.
Not an actual Unreal cook, APK output, or device test.
"""
import tempfile
import json
import os
import zipfile
from pathlib import Path
import irl_android_apk_runner as runner

def fake_tree(folder, behaviour="ok"):
    root=Path(folder)/"IRL"
    (root/"Config").mkdir(parents=True)
    (root/"Source"/"IRL"/"Mobile").mkdir(parents=True)
    (root/"IRL.uproject").write_text('{"EngineAssociation":"5.8","Modules":[{"Name":"IRL"}]}')
    (root/"Config"/"DefaultEngine.ini").write_text(
        "[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]\n"
        "PackageName=com.bieexperience.irl\nMinSDKVersion=26\nTargetSDKVersion=35\n"
        "Orientation=Landscape\nbBuildForArm64=True\n")
    (root/"Config"/"DefaultInput.ini").write_text(
        "DefaultTouchInterface=/Engine/MobileResources/HUD/DefaultVirtualJoysticks.DefaultVirtualJoysticks\n")
    (root/"Source"/"IRL"/"IRLPlayerController.cpp").write_text(
        "UIRLMobileTouchHUD::StaticClass()\n")
    (root/"Source"/"IRL"/"Mobile"/"IRLMobileTouchHUD.cpp").write_text(
        "IRL Touch HUD\n")
    engine=Path(folder)/"UE_5.8"
    uat=engine/"Engine"/"Build"/"BatchFiles"/"RunUAT.bat"
    uat.parent.mkdir(parents=True)
    script=r'''#!/usr/bin/env python3
import sys, pathlib, zipfile
kind=MODE
if kind=="exit":sys.exit(7)
if kind=="missing":sys.exit(0)
path=[x[len("-archivedirectory="):] for x in sys.argv if x.startswith("-archivedirectory=")][0]
archive=pathlib.Path(path)
archive.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive/"IRL-arm64.apk","w") as out:
    out.writestr("AndroidManifest.xml", b"binary-manifest-not-actually-android")
    if kind!="no_dex":out.writestr("classes.dex", b"dex")
    if kind!="no_arm":out.writestr("lib/arm64-v8a/libUnreal.so",b"fake-binary")
    out.writestr("assets/irl.pak",b"z"*6000,compress_type=zipfile.ZIP_STORED)
'''.replace("MODE",repr(behaviour))
    uat.write_text(script)
    uat.chmod(0o755)
    return root,engine

cases=0
with tempfile.TemporaryDirectory() as folder:
    root,engine=fake_tree(folder)
    path,record=runner.execute(root,engine,preflight=True)
    assert record["status"]=="SOURCE_AND_UAT_FOUND_NO_APK" and "apk" not in record
    assert json.loads(path.read_text())["status"]==record["status"]
    cases+=1
with tempfile.TemporaryDirectory() as folder:
    root,engine=fake_tree(folder)
    path,record=runner.execute(root,engine)
    assert record["status"]=="APK_FILE_VERIFIED_NOT_DEVICE_TESTED",record
    assert record["apk"]["bytes"]>4096
    assert len(record["apk"]["sha256"])==64
    assert "Android" in " ".join(record["command"])
    cases+=1
for label in ("exit","missing","no_dex","no_arm"):
    with tempfile.TemporaryDirectory() as folder:
        root,engine=fake_tree(folder,label)
        _,record=runner.execute(root,engine)
        assert record["status"]=="NOT_ESTABLISHED" and record["error"],(label,record)
        cases+=1
with tempfile.TemporaryDirectory() as folder:
    root,engine=fake_tree(folder)
    _,record=runner.execute(root,Path(folder)/"nonexistent")
    assert record["status"]=="NOT_ESTABLISHED" and "RunUAT" in record["error"]
    cases+=1
with tempfile.TemporaryDirectory() as folder:
    root,engine=fake_tree(folder)
    config=root/"Config"/"DefaultInput.ini"
    config.write_text("DefaultTouchInterface=None\n")
    try:runner.validated_project(root)
    except RuntimeError as exc: assert "joystick" in str(exc)
    else:raise AssertionError("Android project without touch allowed")
    cases+=1
with tempfile.TemporaryDirectory() as folder:
    root,engine=fake_tree(folder)
    config=root/"Config"/"DefaultEngine.ini"
    config.write_text(config.read_text().replace("TargetSDKVersion=35","TargetSDKVersion=28"))
    try:runner.validated_project(root)
    except RuntimeError as exc:assert "TargetSDKVersion=35" in str(exc)
    else:raise AssertionError("Incorrect Android target accepted")
    cases+=1
with tempfile.TemporaryDirectory() as folder:
    root,engine=fake_tree(folder)
    (root/"IRL.uproject").write_text('{"EngineAssociation":"5.4","Modules":[]}')
    try:runner.validated_project(root)
    except RuntimeError as exc: assert "Wrong Unreal Engine" in str(exc)
    else:raise AssertionError("Wrong game accepted")
    cases+=1
print("PASS",cases,"Android packaging contract scenarios using fake UAT; NO real APK built")
