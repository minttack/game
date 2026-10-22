#!/usr/bin/env python3
"""IRL/BIE: fail-closed native Unreal 5.8 forest build and real editor audit.

Use ONLY with the existing minttack/game/IRL project on Windows.
Does not merge branches, overwrite levels, install Unreal or claim Android FPS.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone, timedelta

EXPECTED_MAP = "/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation"

def utc_now():
    return datetime.now(timezone.utc)

def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def source_commit(root):
    try:
        p = subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],
                           capture_output=True,text=True,timeout=8,check=False)
        sha = p.stdout.strip()
        return sha if p.returncode == 0 and len(sha) == 40 else None
    except (OSError,subprocess.TimeoutExpired):
        return None

def validate_irl_project(root):
    root = Path(root).resolve()
    project = root/"IRL.uproject"
    target = root/"Source"/"IRLEditor.Target.cs"
    visual = root/"Tools"/"Visual"
    script = visual/"run_irl_forest_validation.py"
    generator = visual/"generate_irl_showcase.py"
    scorer = visual/"forest_world_evidence.py"
    if not all(p.is_file() for p in (project,target,script,generator,scorer)):
        raise RuntimeError("Not the original IRL source tree (missing project, Editor Target, forest scripts)")
    try:
        desc = json.loads(project.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise RuntimeError("IRL.uproject is not readable JSON") from exc
    if (str(desc.get("EngineAssociation")) != "5.8" or
        "IRL" not in [m.get("Name") for m in desc.get("Modules",[]) if isinstance(m,dict)]):
        raise RuntimeError("Incorrect Unreal 5.8 association or IRL game module")
    return {"root":root,"project":project,"editor_script":script,
            "generator":generator,"scorer":scorer}

def find_unreal_engine(explicit=None):
    paths = []
    if explicit:
        paths.append(Path(explicit))
    else:
        for name in ("IRL_UE_ROOT","UE5_ROOT","UE_ROOT"):
            if os.environ.get(name):
                paths.append(Path(os.environ[name]))
        if os.name == "nt":
            paths.append(Path(os.environ.get("ProgramFiles","C:/Program Files"))/"Epic Games"/"UE_5.8")
    for root in paths:
        root = root.expanduser().resolve()
        build = root/"Engine"/"Build"/"BatchFiles"/"Build.bat"
        editor = root/"Engine"/"Binaries"/"Win64"/"UnrealEditor-Cmd.exe"
        if build.is_file() and editor.is_file():
            return {"root":root,"build":build,"editor":editor}
    raise RuntimeError(
        "Unreal Engine 5.8 not found. Supply --engine-root <UE_5.8 path>. "
        "Requires Build.bat and UnrealEditor-Cmd.exe")

def verify_generated_art(root, generator, python=sys.executable):
    art = root/"Tools"/"Visual"/"Generated"
    manifest = art/"IRL_Original_PBR_Manifest.json"
    if not art.exists():
        # Original generated source only; never install software or download art.
        p = subprocess.run(
            [python,str(generator),"--out",str(art),"--size","512","--seed","20261022"],
            cwd=str(root),capture_output=True,text=True,timeout=180,check=False)
        if p.returncode != 0:
            raise RuntimeError("Original material generation failed: "+(p.stderr[-1200:] or p.stdout[-1200:]))
    elif not manifest.is_file():
        raise RuntimeError("Existing Generated folder lacks manifest; refusing to overwrite unknown user assets")
    sys.path.insert(0,str(root/"Tools"/"Visual"))
    from forest_collision_gate import verify_source_manifest
    count = verify_source_manifest(art)
    if count != 16:
        raise RuntimeError("Incorrect original PBR source-file count")
    return {"path":str(art),"source_files":count,"manifest_sha256":sha256_file(manifest)}

def verify_fresh_editor_report(saved_dir, launched_at, scorer_root):
    candidates = sorted(Path(saved_dir).glob("forest_editor_audit_*.json"),
                        key=lambda p: p.stat().st_mtime,reverse=True)
    if not candidates:
        raise RuntimeError("Unreal emitted NO forest_editor_audit_*.json report")
    reports = []
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            observed = datetime.fromisoformat(data["observed_utc"])
            if (observed.tzinfo is None or observed < launched_at or
                observed > utc_now()+timedelta(minutes=1) or
                path.stat().st_mtime < launched_at.timestamp()-1):
                continue
            reports.append((path,data))
        except (OSError,ValueError,TypeError,KeyError):
            continue
    if not reports:
        raise RuntimeError("No NEW timestamped Unreal forest report; stale results do not count")
    path,report = reports[0]
    if (report.get("source") != "unreal_editor_line_trace" or
        report.get("map_path") != EXPECTED_MAP):
        raise RuntimeError("Unreal report provenance/map does not match the original IRL validation level")
    sys.path.insert(0,str(Path(scorer_root).resolve()))
    from forest_world_evidence import assess_scene_report
    checked = assess_scene_report(report)
    if (checked["status"] != "EDITOR_REVIEW_ELIGIBLE" or
        report.get("assessment",{}).get("status") != "EDITOR_REVIEW_ELIGIBLE"):
        raise RuntimeError("Forest scene editor assessment failed: "+str(checked["errors"]))
    return {"source_path":str(path),"sha256":sha256_file(path),"observations":checked["tests"],
            "disposition":"EDITOR_REVIEW_ELIGIBLE_NOT_PLAYABLE_OR_ANDROID"}

def run_logged(command, logfile, cwd, timeout):
    with Path(logfile).open("wb") as handle:
        try:
            p = subprocess.run(
                [str(part) for part in command],cwd=str(cwd),stdout=handle,
                stderr=subprocess.STDOUT,check=False,timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Native Unreal command TIMED OUT; see "+str(logfile)) from exc
        except OSError as exc:
            raise RuntimeError("Native Unreal command could not launch: "+str(exc)) from exc
    if p.returncode != 0:
        raise RuntimeError("Native command exited "+str(p.returncode)+"; see "+str(logfile))
    return {"exit_code":p.returncode,"log":str(logfile),"sha256":sha256_file(logfile)}

def execute(project_root, engine_root=None, mode="build-and-audit", timeout=3600):
    project = validate_irl_project(project_root)
    saved = project["root"]/"Saved"/"IRL"
    saved.mkdir(parents=True,exist_ok=True)
    beginning = utc_now()
    label = beginning.strftime("%Y%m%dT%H%M%S%fZ")
    result_path = saved/("native_forest_run_"+label+".json")
    record = {
        "source":"IRL_NATIVE_RUNNER","started_utc":beginning.isoformat(),
        "project":str(project["project"]),"source_commit":source_commit(project["root"]),
        "mode":mode,"status":"NOT_ESTABLISHED",
        "not_verified":["Unreal PIE movement","Android performance",
                        "two-player synchronization","AAA photorealism"]}
    try:
        if mode not in ("preflight","build-and-audit","audit-only"):
            raise RuntimeError("Unsupported execution mode")
        engine = find_unreal_engine(engine_root)
        record["engine_root"] = str(engine["root"])
        record["source_art"] = verify_generated_art(project["root"],project["generator"])
        if mode == "preflight":
            record["status"] = "ENVIRONMENT_READY_NOT_ENGINE_TESTED"
        else:
            if mode == "build-and-audit":
                command = [engine["build"],"IRLEditor","Win64","Development",
                           project["project"],"-WaitMutex","-NoHotReload"]
                record["build_command"] = [str(part) for part in command]
                record["build"] = run_logged(
                    command,saved/("unreal_build_"+label+".log"),project["root"],timeout)
            command = [engine["editor"],project["project"],
                       "-ExecutePythonScript="+str(project["editor_script"]),
                       "-nop4","-unattended"]
            record["editor_command"] = [str(part) for part in command]
            launched_at = utc_now()
            record["editor"] = run_logged(
                command,saved/("unreal_editor_"+label+".log"),project["root"],timeout)
            record["editor_evidence"] = verify_fresh_editor_report(
                saved,launched_at,project["scorer"].parent)
            record["status"] = "EDITOR_REVIEW_ELIGIBLE_NOT_PLAYABLE_OR_ANDROID"
    except Exception as exc:
        record["error"] = str(exc)
        record["status"] = "NOT_ESTABLISHED"
    finally:
        record["completed_utc"] = utc_now().isoformat()
        result_path.write_text(json.dumps(record,indent=2,allow_nan=False),encoding="utf-8")
    return result_path,record

def main(argv=None):
    p=argparse.ArgumentParser(description="One IRL Unreal project: native Windows build and forest audit")
    p.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument("--engine-root",type=Path,default=None)
    p.add_argument("--mode",choices=("preflight","build-and-audit","audit-only"),default="build-and-audit")
    p.add_argument("--timeout-seconds",type=int,default=3600)
    args=p.parse_args(argv)
    result,record=execute(args.project_root,args.engine_root,args.mode,args.timeout_seconds)
    print("IRL native check:",record["status"],"\nEvidence:",result)
    if record.get("error"):print("BLOCKER:",record["error"])
    return 0 if record["status"] in (
        "ENVIRONMENT_READY_NOT_ENGINE_TESTED",
        "EDITOR_REVIEW_ELIGIBLE_NOT_PLAYABLE_OR_ANDROID") else 1

if __name__=="__main__":
    sys.exit(main())
