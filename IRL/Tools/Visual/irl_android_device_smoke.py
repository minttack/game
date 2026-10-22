#!/usr/bin/env python3
"""IRL Android-first: evidence-gated, USB ADB real-device launch smoke.

ONE existing Unreal IRL project. Default is read-only preflight. --run explicitly
starts an ALREADY INSTALLED app; no APK installation, no Android settings edits.
Observed process+foreground never imply gameplay controls, 30FPS or AAA graphics.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

PACKAGE="com.bieexperience.irl"
PASS_STATUS="DEVICE_LAUNCH_AND_FOREGROUND_OBSERVED_NOT_GAMEPLAY_VERIFIED"

class SmokeFailure(RuntimeError):
    pass

def do_call(args, timeout=20, run=subprocess.run):
    try:
        p=run([str(a) for a in args], text=True, capture_output=True,
              timeout=timeout,check=False)
    except (OSError,subprocess.TimeoutExpired) as err:
        raise SmokeFailure("ADB command not available or timed out: "+str(err)) from err
    if p.returncode!=0:
        raise SmokeFailure("ADB command failed (code "+str(p.returncode)+"): "+
                           (p.stderr or p.stdout or "no diagnostics")[-600:])
    return p.stdout.strip()

def pick_device(adb, serial=None, run=subprocess.run):
    output=do_call([adb,"devices","-l"],run=run)
    ready=[]
    unauthorized=[]
    for line in output.splitlines()[1:]:
        parts=line.strip().split()
        if len(parts)<2:continue
        if parts[1]=="device":ready.append(parts[0])
        elif parts[1] in ("unauthorized","offline"):unauthorized.append(parts[0])
    if serial:
        if serial not in ready:raise SmokeFailure(
            "Selected ADB device is not authorized/online: "+serial)
        return serial
    if len(ready)!=1:
        raise SmokeFailure(
            "Expected exactly one authorized USB debugging device (or use --serial). "+
            "Ready="+str(len(ready))+", offline/unauthorized="+str(len(unauthorized)))
    return ready[0]

def foreground_package(dumpsys):
    # Accept only recognized resumed/current app component markers. Merely
    # mentioning IRL in a background task is NOT evidence it is on the screen.
    for line in dumpsys.splitlines():
        if any(key in line for key in ("mResumedActivity", "topResumedActivity",
                                      "mCurrentFocus", "mFocusedApp")):
            match=re.search(r"\b(com\.[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)+)\s*/",line)
            if match:return match.group(1)
    return None

def parse_pid(pid_output):
    pieces=pid_output.strip().split()
    if not pieces or any(not p.isdigit() or int(p)<=0 for p in pieces):
        return None
    return tuple(int(p) for p in pieces)

def apk_evidence_check(path):
    """Optional linkage to a real APK artifact hash; does not prove installation."""
    if not path:return None
    p=Path(path)
    data=json.loads(p.read_text(encoding="utf8"))
    if data.get("status")!="APK_FILE_VERIFIED_NOT_DEVICE_TESTED":
        raise SmokeFailure("Supplied Android build report has no verified APK")
    apk=data.get("apk",{})
    src=Path(apk.get("apk_path",""))
    if not src.is_file():
        raise SmokeFailure("APK referenced by evidence report no longer exists")
    h=hashlib.sha256(src.read_bytes()).hexdigest()
    if h!=apk.get("sha256"):
        raise SmokeFailure("APK's SHA-256 differs from the build report")
    return {"source_build_report":str(p),"apk_sha256":h,
            "limitation":"File integrity alone does not prove this APK is installed"}

def execute(project_root, *, adb_path=None, serial=None, launch=False,
            checks=3, interval=2.0, run=subprocess.run, sleep=time.sleep,
            apk_report=None):
    if not 2<=checks<=12 or not 0.0<=interval<=15.0:
        raise ValueError("Checks must be 2-12 and interval must be 0-15 seconds")
    root=Path(project_root).resolve()
    project=root/"IRL.uproject"
    if not project.is_file():
        raise SmokeFailure("Not the existing Unreal IRL project directory")
    meta=json.loads(project.read_text(encoding="utf8"))
    if meta.get("EngineAssociation")!="5.8" or not any(
        m.get("Name")=="IRL" for m in meta.get("Modules",[]) if isinstance(m,dict)):
        raise SmokeFailure("Not the correct original IRL Unreal 5.8 game")
    saved=root/"Saved"/"IRL"
    saved.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc)
    reportpath=saved/("android_device_smoke_"+started.strftime("%Y%m%dT%H%M%S%fZ")+".json")
    record={"source":"ADB_REAL_DEVICE_SMOKE_SCRIPT","package":PACKAGE,
            "mode":"launch" if launch else "read_only_preflight",
            "started_utc":started.isoformat(),"status":"NOT_ESTABLISHED",
            "limitations":["ADB process and foreground observations are not a gameplay movement test",
                           "No renderer quality or FPS/thermal evidence is inferred",
                           "No installation or app version equality is inferred from package presence",
                           "This run does not demonstrate two human players or BIE life learning"]}
    try:
        adb=str(adb_path) if adb_path else shutil.which("adb")
        if not adb:raise SmokeFailure("Android Platform Tools adb not found. Install platform-tools")
        record["adb_version"]=do_call([adb,"version"],run=run).splitlines()[0]
        chosen=pick_device(adb,serial,run=run)
        record["device_serial_sha256"]=hashlib.sha256(chosen.encode()).hexdigest()
        # Avoid storing real phone identifiers in committed reports.
        base=[adb,"-s",chosen,"shell"]
        model=do_call(base+["getprop","ro.product.model"],run=run)
        sdk=do_call(base+["getprop","ro.build.version.sdk"],run=run)
        abi=do_call(base+["getprop","ro.product.cpu.abi"],run=run)
        record["device"]={"model":model,"sdk":sdk,"abi":abi}
        if not sdk.isdigit() or int(sdk)<26 or not abi.startswith("arm64"):
            raise SmokeFailure("Device doesn't meet the Android ARM64 / SDK26 baseline")
        installed=do_call(base+["pm","path",PACKAGE],run=run)
        if not any(line.startswith("package:") for line in installed.splitlines()):
            raise SmokeFailure("IRL is not installed on this authorized phone")
        record["installed_package_present"]=True
        if apk_report:record["artifact_reference"]=apk_evidence_check(apk_report)
        if not launch:
            record["status"]="AUTHORIZED_DEVICE_AND_PACKAGE_FOUND_NO_LAUNCH"
        else:
            launched=do_call(base+["monkey","-p",PACKAGE,"-c",
                                   "android.intent.category.LAUNCHER","1"],run=run)
            if "Events injected: 1" not in launched:
                raise SmokeFailure("Android did not confirm a launch event was injected")
            samples=[]
            for i in range(checks):
                if i and interval:sleep(interval)
                # Native process and foreground activity are observed separately.
                pid=do_call(base+["pidof",PACKAGE],run=run)
                pids=parse_pid(pid)
                activity=do_call(base+["dumpsys","activity","activities"],run=run)
                fg=foreground_package(activity)
                samples.append({"sample":i+1,"process_running":bool(pids),
                                "foreground_package":fg,
                                "foreground_is_irl":fg==PACKAGE})
            record["samples"]=samples
            if not all(p["process_running"] and p["foreground_is_irl"] for p in samples):
                raise SmokeFailure("IRL wasn't continuously running AND foreground during the device check")
            record["status"]=PASS_STATUS
    except Exception as e:
        record["error"]=str(e)
        record["status"]="NOT_ESTABLISHED"
    finally:
        record["completed_utc"]=datetime.now(timezone.utc).isoformat()
        reportpath.write_text(json.dumps(record,indent=2,allow_nan=False),encoding="utf8")
    return reportpath,record

def main(argv=None):
    p=argparse.ArgumentParser(description="USB phone smoke test for the original IRL game")
    p.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument("--adb",dest="adb_path",help="Path to Android platform-tools/adb")
    p.add_argument("--serial",help="Authorized device serial when multiple devices are connected")
    p.add_argument("--run",action="store_true",help="Explicitly LAUNCH already-installed IRL app")
    p.add_argument("--apk-report",type=Path,help="Optional linked real APK build evidence JSON")
    p.add_argument("--checks",type=int,default=3)
    p.add_argument("--interval",type=float,default=2)
    a=p.parse_args(argv)
    path,result=execute(a.project_root,adb_path=a.adb_path,serial=a.serial,
        launch=a.run,checks=a.checks,interval=a.interval,apk_report=a.apk_report)
    print("IRL Android device evidence:",result["status"],"\nReport:",path)
    if result.get("error"):print("BLOCKER:",result["error"])
    return 0 if result["status"] in (PASS_STATUS,"AUTHORIZED_DEVICE_AND_PACKAGE_FOUND_NO_LAUNCH") else 1

if __name__=="__main__":
    sys.exit(main())
