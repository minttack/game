#!/usr/bin/env python3
"""IRL Android-first DEVELOPMENT APK gate for ONE Unreal Engine 5.8 project.

Builds an original IRL Android_ASTC artifact through UE RunUAT on Windows.
Never represents fake, stale or missing APKs as a compiled mobile game.
Never installs to an Android device, signs a Play distribution, or merges PRs.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from android_renderer_gate import validate_android_config, AndroidConfigError

def sha256(path):
    dig = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024), b""):
            dig.update(block)
    return dig.hexdigest()

def validated_project(project_dir):
    root=Path(project_dir).resolve()
    up=root/"IRL.uproject"
    config=root/"Config"/"DefaultEngine.ini"
    input_ini=root/"Config"/"DefaultInput.ini"
    controller=root/"Source"/"IRL"/"IRLPlayerController.cpp"
    hud=root/"Source"/"IRL"/"Mobile"/"IRLMobileTouchHUD.cpp"
    required=(up,config,input_ini,controller,hud)
    if not all(p.is_file() for p in required):
        raise RuntimeError("Missing original IRL Unreal module, Android config, or native mobile touch code")
    try:
        u=json.loads(up.read_text(encoding="utf8"))
    except (OSError,ValueError) as exc:
        raise RuntimeError("IRL.uproject cannot be parsed") from exc
    if u.get("EngineAssociation") != "5.8" or not any(
            x.get("Name")=="IRL" for x in u.get("Modules",[]) if isinstance(x,dict)):
        raise RuntimeError("Wrong Unreal Engine version or missing original IRL module")
    ec=config.read_text(encoding="utf8")
    ic=input_ini.read_text(encoding="utf8")
    cc=controller.read_text(encoding="utf8")
    for needed in (
        "[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]",
        "PackageName=com.bieexperience.irl", "MinSDKVersion=26",
        "TargetSDKVersion=35", "Orientation=Landscape",
        "bBuildForArm64=True",
    ):
        if needed not in ec: raise RuntimeError("Android project setting absent: "+needed)
    if "DefaultTouchInterface=/Engine/MobileResources/HUD/DefaultVirtualJoysticks.DefaultVirtualJoysticks" not in ic:
        raise RuntimeError("Mobile virtual joysticks are not configured")
    if "UIRLMobileTouchHUD::StaticClass()" not in cc:
        raise RuntimeError("The existing IRL player controller has no native touch HUD fallback")
    # Reject insecure Android network file-server settings or desktop
    # Lumen/RT renderer before even attempting Unreal's expensive APK cook.
    try:
        validate_android_config(root)
    except AndroidConfigError as exc:
        raise RuntimeError("Android safety/rendering preflight: "+str(exc)) from exc
    return root, up

def discover_engine(explicit):
    roots=[]
    if explicit:
        roots.append(Path(explicit))
    else:
        for key in ("IRL_UE_ROOT","UE5_ROOT","UE_ROOT"):
            if os.environ.get(key):roots.append(Path(os.environ[key]))
        if os.name=="nt":
            roots.append(Path(os.environ.get("ProgramFiles","C:/Program Files"))/"Epic Games"/"UE_5.8")
    for root in roots:
        candidate=root.expanduser().resolve()/"Engine"/"Build"/"BatchFiles"/"RunUAT.bat"
        if candidate.is_file():
            return candidate
    raise RuntimeError("Unreal 5.8 RunUAT.bat not found; use --engine-root to specify engine")

def toolchain_inventory(env=None):
    env=env if env is not None else os.environ
    result={}
    for variable in ("ANDROID_HOME","ANDROID_SDK_ROOT","NDKROOT","JAVA_HOME"):
        raw=env.get(variable,"")
        result[variable]={"configured":bool(raw),"exists":bool(raw and Path(raw).is_dir())}
    result["status"]="PATHS_PRESENT" if (
        (result["ANDROID_HOME"]["exists"] or result["ANDROID_SDK_ROOT"]["exists"]) and
        result["JAVA_HOME"]["exists"]) else "CHECK_UNREAL_TURNKEY_TOOLCHAIN"
    # Epic's Turnkey toolchain can also be configured in Engine/Android settings;
    # this is only environmental diagnostic, NOT proof SDK licenses are accepted.
    return result

def inspect_apk(apk):
    apk=Path(apk)
    if not apk.is_file() or apk.stat().st_size < 4096:
        raise RuntimeError("Generated APK missing or implausibly small")
    try:
        with zipfile.ZipFile(apk,"r") as z:
            names=set(z.namelist())
            if not {"AndroidManifest.xml","classes.dex"}.issubset(names):
                raise RuntimeError("APK missing AndroidManifest.xml or classes.dex")
            if not any(x.startswith("lib/arm64-v8a/") and x.endswith(".so") for x in names):
                raise RuntimeError("APK contains no arm64-v8a native game library")
            if z.testzip() is not None:
                raise RuntimeError("APK ZIP member fails CRC integrity check")
    except zipfile.BadZipFile as exc:
        raise RuntimeError("Invalid Android APK ZIP structure") from exc
    return {"apk_path":str(apk),"sha256":sha256(apk),
            "bytes":apk.stat().st_size,"verified":"ZIP_CRC_MANIFEST_DEX_ARM64_ONLY"}

def command_for_android(uat,uproject,archive):
    # Cook the EXISTING ThirdPerson playable map. Unmerged artist-side forest
    # level is only imported by the Unreal Editor and may NOT exist as .umap.
    return [str(uat),"BuildCookRun",
            "-project="+str(uproject),"-noP4",
            "-platform=Android","-cookflavor=ASTC","-clientconfig=Development",
            "-build","-cook","-stage","-pak","-package","-archive",
            "-archivedirectory="+str(archive),"-map=/Game/ThirdPerson/Lvl_ThirdPerson",
            "-utf8output"]

def execute(project_dir,engine_root=None,preflight=False,timeout=7200,run=subprocess.run):
    root=Path(project_dir).resolve()
    started=datetime.now(timezone.utc)
    tag=started.strftime("%Y%m%dT%H%M%S%fZ")
    evidence=root/"Saved"/"IRL"
    evidence.mkdir(parents=True,exist_ok=True)
    report_path=evidence/("android_apk_build_"+tag+".json")
    archive=evidence/"AndroidBuilds"/tag
    report={"started_utc":started.isoformat(),"source":"IRL_ANDROID_BUILD_GATE",
            "status":"NOT_ESTABLISHED","development_only":True,
            "does_not_prove":["Moto G playable","30 FPS","BIE autonomous life",
                              "multiplayer","release signing","Google Play acceptance"]}
    try:
        root,uproject=validated_project(root)
        report["project"]=str(uproject)
        uat=discover_engine(engine_root)
        report["unreal_automation_tool"]=str(uat)
        report["android_toolchain_inventory"]=toolchain_inventory()
        if preflight:
            report["status"]="SOURCE_AND_UAT_FOUND_NO_APK"
        else:
            archive.mkdir(parents=True,exist_ok=False)
            cmd=command_for_android(uat,uproject,archive)
            report["command"]=cmd
            logfile=evidence/("android_uat_"+tag+".log")
            try:
                with logfile.open("wb") as stream:
                    result=run(cmd,cwd=root,stdout=stream,stderr=subprocess.STDOUT,
                               timeout=timeout,check=False)
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("Unreal Android BuildCookRun timed out; see "+str(logfile)) from exc
            report["uat_exit_code"]=result.returncode
            report["uat_log"]=str(logfile)
            report["uat_log_sha256"]=sha256(logfile)
            if result.returncode!=0:
                raise RuntimeError("Native Android BuildCookRun failed (exit="+str(result.returncode)+")")
            candidates=list(archive.rglob("*.apk"))
            if len(candidates)!=1:
                raise RuntimeError("Expected exactly one NEW Android APK in isolated archive; found "+str(len(candidates)))
            report["apk"]=inspect_apk(candidates[0])
            report["status"]="APK_FILE_VERIFIED_NOT_DEVICE_TESTED"
    except Exception as exc:
        report["error"]=str(exc)
        report["status"]="NOT_ESTABLISHED"
    finally:
        report["finished_utc"]=datetime.now(timezone.utc).isoformat()
        report_path.write_text(json.dumps(report,indent=2),encoding="utf8")
    return report_path,report

def main(argv=None):
    parser=argparse.ArgumentParser(description="Compile the ONE original IRL game to Android")
    parser.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument("--engine-root",type=Path)
    parser.add_argument("--preflight",action="store_true")
    parser.add_argument("--timeout",type=int,default=7200)
    args=parser.parse_args(argv)
    path,report=execute(args.project_root,args.engine_root,args.preflight,args.timeout)
    print("IRL Android:",report["status"]," | report:",path)
    if report.get("error"):print("BLOCKER:",report["error"])
    if report.get("apk"):print("Actual compiled APK:",report["apk"]["apk_path"])
    return 0 if report["status"] in (
        "SOURCE_AND_UAT_FOUND_NO_APK","APK_FILE_VERIFIED_NOT_DEVICE_TESTED") else 1

if __name__=="__main__":
    sys.exit(main())
