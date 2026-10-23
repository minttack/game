#!/usr/bin/env python3
"""IRL Antigravity/UE 5.8: truthful read-only local workstation preflight.

Checks the source tree and AVAILABLE local toolchain without installing,
running, editing, connecting, or enabling an MCP server. Intended as the first
native Windows diagnostic, not a claim that an APK exists.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

EXPECTED_VERSION="5.8"
EXPECTED_PACKAGE="com.bieexperience.irl"
REQUIRED_SOURCE=(
    "IRL.uproject",
    "Source/IRL/IRLPlayerController.cpp",
    "Source/IRL/Mobile/IRLMobileTouchHUD.cpp",
    "Config/Android/AndroidEngine.ini",
    "Config/DefaultEngine.ini",
    "Tools/Visual/irl_android_apk_runner.py",
    "Tools/Visual/IRL_BUILD_ANDROID_APK_WINDOWS.bat",
    "Tools/Visual/audit_android_class_chain.py",
)

def check_source(project):
    project=Path(project).resolve()
    missing=[rel for rel in REQUIRED_SOURCE if not (project/rel).is_file()]
    if missing:
        raise ValueError("Not the current IRL Android source checkout: "+", ".join(missing))
    try:
        data=json.loads((project/"IRL.uproject").read_text(encoding="utf8"))
    except (OSError,ValueError) as exc:
        raise ValueError("IRL.uproject invalid") from exc
    if str(data.get("EngineAssociation"))!=EXPECTED_VERSION or not any(
        x.get("Name")=="IRL" and x.get("Type")=="Runtime"
        for x in data.get("Modules",[]) if isinstance(x,dict)):
        raise ValueError("Only the original Unreal Engine 5.8 IRL game module is supported")
    config=(project/"Config"/"DefaultEngine.ini").read_text(encoding="utf8")
    renderer=(project/"Config"/"Android"/"AndroidEngine.ini").read_text(encoding="utf8")
    if "PackageName="+EXPECTED_PACKAGE not in config:
        raise ValueError("IRL Android package identity absent")
    if "r.Mobile.ShadingPath=0" not in renderer or "r.DynamicGlobalIlluminationMethod=0" not in renderer:
        raise ValueError("IRL Android-specific forward-renderer source settings absent")
    return project

def _git_text(repo, *args):
    try:
        r=subprocess.run(["git","-C",str(repo),*args],capture_output=True,
                         text=True,check=False,timeout=6)
        if r.returncode==0:
            return r.stdout.strip()
    except (OSError,subprocess.TimeoutExpired):
        pass
    return None

def check_toolchain(engine_root=None, env=None):
    env=env if env is not None else os.environ
    possible=[]
    if engine_root is not None:
        possible=[Path(engine_root)]
    else:
        for name in ("IRL_UE_ROOT","UE5_ROOT","UE_ROOT"):
            if env.get(name):possible.append(Path(env[name]))
        if os.name=="nt":
            possible.append(Path(env.get("ProgramFiles","C:/Program Files"))/"Epic Games"/"UE_5.8")
    installed=None
    for root in possible:
        root=root.expanduser().resolve()
        uat=root/"Engine"/"Build"/"BatchFiles"/"RunUAT.bat"
        editor=root/"Engine"/"Binaries"/"Win64"/"UnrealEditor-Cmd.exe"
        if uat.is_file() and editor.is_file():
            installed={"root":str(root),"uat":str(uat),"editor":str(editor)}
            break
    android_sdk=env.get("ANDROID_HOME") or env.get("ANDROID_SDK_ROOT")
    return {
        "unreal_5_8_executables_found":installed is not None,
        "engine":installed,
        "android_sdk_dir_found":bool(android_sdk and Path(android_sdk).is_dir()),
        "jdk_dir_found":bool(env.get("JAVA_HOME") and Path(env["JAVA_HOME"]).is_dir()),
        "adb_in_path":bool(shutil.which("adb")),
        "python_version":str(sys.version_info.major)+"."+str(sys.version_info.minor),
        "note":"Environment presence is NOT verification of Android licenses, NDK, UAT cook, or UE compilation.",
    }

def preflight(project,engine_root=None):
    root=check_source(project)
    branch=_git_text(root.parent, "branch","--show-current")
    commit=_git_text(root.parent, "rev-parse","HEAD")
    changes=_git_text(root.parent,"status","--porcelain")
    toolchain=check_toolchain(engine_root)
    return {
        "project":"IRL",
        "source":"IRL_ANTIGRAVITY_LOCAL_READ_ONLY_PREFLIGHT",
        "engine_association":EXPECTED_VERSION,
        "unreal_project":str(root/"IRL.uproject"),
        "package":EXPECTED_PACKAGE,
        "branch":branch,
        "commit":commit,
        "git_worktree_clean":changes=="" if changes is not None else None,
        "device_or_apk_test":"NOT_RUN",
        "mcp_editor_connection":"NOT_TESTED",
        "native_unreal_build":"NOT_RUN",
        "toolchain":toolchain,
        "recommended_action":(
            "Verify exact branch and game ancestry, use UE 5.8 Unreal MCP in "
            "Antigravity with local consent, run native compile and ASTC BuildCookRun "
            "on this original IRL project, then inspect real APK and phone evidence."
        ),
    }

def main(argv=None):
    parser=argparse.ArgumentParser(description="Read-only IRL Antigravity workspace diagnostic")
    parser.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument("--engine-root",type=Path)
    parser.add_argument("--strict-toolchain",action="store_true",
                        help="Exit nonzero if native UE 5.8 tool binaries absent")
    args=parser.parse_args(argv)
    try:
        report=preflight(args.project_root,args.engine_root)
        print(json.dumps(report,indent=2,ensure_ascii=False))
        if args.strict_toolchain and not report["toolchain"]["unreal_5_8_executables_found"]:
            return 2
        return 0
    except ValueError as exc:
        print(json.dumps({"status":"INVALID_IRL_SOURCE","error":str(exc)},indent=2))
        return 1

if __name__=="__main__":
    sys.exit(main())
