#!/usr/bin/env python3
"""IRL mobile log evidence: parse *only* tagged in-game measurements.

--file accepts an externally supplied Unreal Android log (provenance not
authenticated). --adb explicitly reads a connected authorized device's local
logcat; it never installs, launches, clears logs or changes device settings.
No network, language model, personal or raw log export. Never invent FPS/GPU.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
from statistics import median

MARKER = "IRL_MOBILE_EVIDENCE_V1"
REQUIRED = (
    "session","seq","frames","rejected","duration_s","mean_ms",
    "p50_ms","p95_ms","p99_ms","max_ms","move_axes","look_axes",
    "jumps","experiences","tier"
)
HEX32=re.compile(r"^[0-9a-fA-F]{32}$")
INT_FIELDS = ("seq","frames","rejected","move_axes","look_axes","jumps","experiences","tier")
FLOAT_FIELDS = ("duration_s","mean_ms","p50_ms","p95_ms","p99_ms","max_ms")

class InvalidMobileEvidence(ValueError):
    pass

def parse_line(line):
    # UE may prepend thread id and LogTemp severity; require exact marker token.
    marker=re.search(r"\bIRL_MOBILE_EVIDENCE_V1\s+(.+)$",line)
    if not marker:return None
    fields=re.findall(r"([a-z][a-z0-9_]*)=([^\s]+)",marker.group(1))
    if len(fields)!=len(REQUIRED) or set(k for k,_ in fields)!=set(REQUIRED):
        raise InvalidMobileEvidence("Missing, duplicated or extra IRL mobile fields")
    d=dict(fields)
    if not HEX32.fullmatch(d["session"]):
        raise InvalidMobileEvidence("Invalid session fingerprint")
    try:
        for name in INT_FIELDS:
            if not re.fullmatch(r"[0-9]+",d[name]):
                raise InvalidMobileEvidence("Noninteger field "+name)
            d[name]=int(d[name])
        for name in FLOAT_FIELDS:
            d[name]=float(d[name])
    except (ValueError,OverflowError) as exc:
        raise InvalidMobileEvidence("Invalid mobile numeric measurement") from exc
    if not all(math.isfinite(d[k]) for k in FLOAT_FIELDS):
        raise InvalidMobileEvidence("Nonfinite frame-time measurement")
    if not (1<=d["seq"]<=1000000 and 60<=d["frames"]<=1024 and
            0<=d["rejected"]<=1000000 and d["tier"] in (0,1,2)):
        raise InvalidMobileEvidence("Out-of-range sample count, sequence or tier")
    if any(d[k]<0 or d[k]>10000000 for k in ("move_axes","look_axes","jumps","experiences")):
        raise InvalidMobileEvidence("Invalid input callback counts")
    if not (0.5<=d["duration_s"]<=10.5 and
            0.01<=d["p50_ms"]<=d["p95_ms"]<=d["p99_ms"]<=d["max_ms"]<=200.0 and
            0.01<=d["mean_ms"]<=200.0):
        raise InvalidMobileEvidence("Inconsistent frame percentiles")
    if abs(d["duration_s"]-(d["mean_ms"]*d["frames"]/1000.0))>0.15:
        raise InvalidMobileEvidence("Duration disagrees with actual frame mean and count")
    return d

def summarize_log(lines, *, session=None, min_windows=2):
    if min_windows<2:raise InvalidMobileEvidence("Need at least two windows")
    groups={}
    last_session=None
    invalid=0
    for line in lines:
        if MARKER not in line:continue
        try:entry=parse_line(line)
        except InvalidMobileEvidence:
            invalid+=1
            continue
        if entry is None:continue
        key=entry["session"]
        groups.setdefault(key,[]).append(entry)
        last_session=key
    if not groups:
        raise InvalidMobileEvidence("No valid IRL-specific evidence in provided log")
    chosen=session or last_session
    if chosen not in groups:
        raise InvalidMobileEvidence("Requested IRL session is not present")
    rows=groups[chosen]
    if len(rows)<min_windows or len(rows)>256:
        raise InvalidMobileEvidence("Insufficient or excessive tagged performance windows")
    seqs=[r["seq"] for r in rows]
    if len(seqs)!=len(set(seqs)) or any(b<=a for a,b in zip(seqs,seqs[1:])):
        raise InvalidMobileEvidence("Duplicate or out-of-order IRL evidence windows")
    frames=sum(r["frames"] for r in rows)
    duration=sum(r["duration_s"] for r in rows)
    if duration<=0:raise InvalidMobileEvidence("Empty measurement period")
    observed_frames=sum(r["frames"] for r in rows)
    weighted_mean=sum(r["frames"]*r["mean_ms"] for r in rows)/observed_frames
    # Do NOT label this as a globally pooled frame p95: only window summaries
    # were logged, so a pooled p95 cannot be reconstructed accurately.
    return {
        "status":"SOURCE_REPORTED_FRAME_AND_INPUT_EVIDENCE_NOT_GAMEPLAY_VERIFIED",
        "source_marker":MARKER,"session":chosen,"windows":len(rows),
        "frames":frames,"duration_s":round(duration,3),
        "weighted_mean_frame_ms":round(weighted_mean,3),
        "mean_based_estimated_fps":round(1000.0/weighted_mean,2),
        "median_window_p95_ms":round(median(r["p95_ms"] for r in rows),3),
        "worst_window_p99_ms":round(max(r["p99_ms"] for r in rows),3),
        "rejected_frame_samples":sum(r["rejected"] for r in rows),
        "axis_move_callbacks":sum(r["move_axes"] for r in rows),
        "axis_look_callbacks":sum(r["look_axes"] for r in rows),
        "jump_press_callbacks":sum(r["jumps"] for r in rows),
        "experience_press_callbacks":sum(r["experiences"] for r in rows),
        "tiers_observed":[r["tier"] for r in rows],
        "malformed_tagged_lines_ignored":invalid,
        "limitations":[
            "Game-thread frame deltas are not GPU frame times or GPU utilization.",
            "Joystick axis callback counts do not prove touch contact or world movement.",
            "Session and marker are asserted by local Unreal logs, not cryptographically authenticated.",
            "No cumulative global p95/p99 or device temperature is reconstructed from window summaries.",
            "No two-human or autonomous BIE life capability is established."
        ]
    }

def fetch_device_lines(adb=None,serial=None,run=subprocess.run):
    exe=adb or shutil.which("adb")
    if not exe:raise InvalidMobileEvidence("ADB platform-tools not found")
    try:
        from irl_android_device_smoke import pick_device
        chosen=pick_device(exe,serial=serial,run=run)
        result=run([str(exe),"-s",chosen,"logcat","-d","-t","6000","-v","brief"],
                   capture_output=True,text=True,timeout=30,check=False)
        if result.returncode!=0:
            raise InvalidMobileEvidence("ADB logcat command failed; device or permission unavailable")
        # Keep only our exact marker text. Never persist other app/user log lines.
        return [line for line in result.stdout.splitlines() if MARKER in line]
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise InvalidMobileEvidence("ADB logcat unavailable") from exc

def main(argv=None):
    parser=argparse.ArgumentParser(description="Summarize actual IRL Android log observations")
    sel=parser.add_mutually_exclusive_group(required=True)
    sel.add_argument("--file",type=Path,help="Existing Android logcat text file")
    sel.add_argument("--adb",action="store_true",help="Read logs from connected authorized phone")
    parser.add_argument("--serial",help="Only with --adb")
    parser.add_argument("--session",help="Select recorded IRL session ID")
    parser.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args(argv)
    if args.serial and not args.adb:
        parser.error("--serial is only valid with --adb")
    root=args.project_root.resolve()
    if not (root/"IRL.uproject").is_file():
        parser.error("Must run against the original IRL game project")
    lines=fetch_device_lines(serial=args.serial) if args.adb else args.file.read_text(encoding="utf8").splitlines()
    result=summarize_log(lines,session=args.session)
    result["input_origin"]="CONNECTED_ADB_LOGCAT" if args.adb else "EXTERNAL_LOG_FILE_NOT_AUTHENTICATED"
    folder=root/"Saved"/"IRL"
    folder.mkdir(parents=True,exist_ok=True)
    name=datetime.now(timezone.utc).strftime("irl_mobile_evidence_%Y%m%dT%H%M%S%fZ.json")
    saved=folder/name
    saved.write_text(json.dumps(result,indent=2),encoding="utf8")
    print(json.dumps({"status":result["status"],"report":str(saved),
                      "windows":result["windows"],"mean_fps":result["mean_based_estimated_fps"]},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
