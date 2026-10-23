"""BIE evidence tests for real-UI log parser; data below are SYNTHETIC."""
import math
import tempfile
from pathlib import Path
from irl_mobile_evidence_report import (
    parse_line, summarize_log, InvalidMobileEvidence, fetch_device_lines
)
from types import SimpleNamespace

A="0123456789abcdef0123456789abcdef"
B="fedcba9876543210fedcba9876543210"
def line(session=A,seq=1,frames=300,mean=33.333,duration=10.0,
         p50=33.0,p95=38.0,p99=44.0,max_ms=66.0,
         move=100,look=80,jumps=1,experiences=1,rejected=2,tier=1):
    return (
        f"10-23 00:40:00.123 D/UE: LogTemp: Display: IRL_MOBILE_EVIDENCE_V1 "
        f"session={session} seq={seq} frames={frames} rejected={rejected} "
        f"duration_s={duration:.3f} mean_ms={mean:.3f} p50_ms={p50:.3f} "
        f"p95_ms={p95:.3f} p99_ms={p99:.3f} max_ms={max_ms:.3f} "
        f"move_axes={move} look_axes={look} jumps={jumps} experiences={experiences} tier={tier}"
    )

checks=0
x=parse_line(line())
assert x["frames"]==300 and x["p99_ms"]==44.0
checks+=1
observed=summarize_log(["other apps logged","irrelevant IRL text",
                         line(seq=1),line(seq=2,p95=42,p99=50,look=40)])
assert observed["status"].startswith("SOURCE_REPORTED")
assert observed["windows"]==2 and observed["frames"]==600
assert observed["axis_move_callbacks"]==200 and observed["axis_look_callbacks"]==120
assert observed["median_window_p95_ms"]==40 and observed["worst_window_p99_ms"]==50
assert observed["rejected_frame_samples"]==4
assert observed["mean_based_estimated_fps"]>29
checks+=1
def fail(lines,reason):
    global checks
    try:summarize_log(lines)
    except InvalidMobileEvidence:pass
    else:raise AssertionError("Accepted invalid mobile telemetry: "+reason)
    checks+=1

fail([],"no evidence")
fail([line()],"only one window")
fail([line(seq=1),line(seq=1)],"duplicate sequence")
fail([line(seq=4),line(seq=3)],"reversed sequence")
fail([line(session=A),line(session=B)],"mixed sessions not enough")
fail([line(seq=1),line(seq=2,frames=30)],"too few valid frames")
fail([line(seq=1),line(seq=2,mean=8)],"duration inconsistent")
fail([line(seq=1),line(seq=2,p95=30)],"percentile ordering")
fail([line(seq=1),line(seq=2,p99=float('nan'))],"nan")
fail([line(seq=1),line(seq=2,tier=4)],"invalid graphics tier")
fail([line(seq=1),line(seq=2).replace("look_axes=80","look_axes=-100")],"negative events")
fail([line(seq=1),line(seq=2).replace("frames=300","frames=not_a_number")],"wrong frame format")
fail([line(seq=1),line(seq=2).replace("tier=1","tier=1 extra=1")],"extra unexpected values")
fail([line(seq=1),line(seq=2).replace("tier=1","tier=1 tier=1")],"duplicate keys")
assert parse_line("tag: unrelated") is None
checks+=1
report=summarize_log([line(session=A,seq=1),line(session=A,seq=2),
                      line(session=B,seq=1),line(session=B,seq=2)],session=A)
assert report["session"]==A and report["windows"]==2
checks+=1
report=summarize_log([line(session=A,seq=1),line(session=A,seq=2),
                      line(session=B,seq=1),line(session=B,seq=2)])
assert report["session"]==B
checks+=1
# A fake ADB process is used only to verify log filtering, never a phone.
class Mock:
    def __call__(self,args,**kwargs):
        if args[-4:]==["logcat","-d","-t","6000"]:
            raise AssertionError("Version should always be explicitly specified")
        if "devices" in args:
            return SimpleNamespace(returncode=0,stdout="List of devices attached\nA\tdevice\n",stderr="")
        if "logcat" in args:
            return SimpleNamespace(returncode=0,stdout="PERSONAL LOG DO NOT SAVE\n"+line()+"\nother data\n",stderr="")
        raise AssertionError(args)
logs=fetch_device_lines(adb="fake-adb",run=Mock())
assert len(logs)==1 and "PERSONAL LOG" not in logs[0]
checks+=1
print("PASS",checks,"mobile evidence parser scenarios, all synthetic; no phone FPS asserted")
