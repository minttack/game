"""12+ honest ADB smoke contracts with a FAKE adb: no actual phone touched."""
from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import irl_android_device_smoke as smoke

def make_project(folder):
    root=Path(folder)/"IRL"
    root.mkdir()
    (root/"IRL.uproject").write_text(json.dumps({
        "EngineAssociation":"5.8", "Modules":[{"Name":"IRL"}]}))
    return root

class FakeADB:
    def __init__(self,mode="success"):
        self.mode=mode
        self.launch_calls=0
        self.queries=[]
    def __call__(self,argv,**kwargs):
        self.queries.append(argv)
        value=""
        rc=0
        if argv[1:]==["version"]:value="Android Debug Bridge version 1.0.41\n"
        elif argv[1:]==["devices","-l"]:
            if self.mode=="two_devices":value="List of devices attached\nA\tdevice\nB\tdevice\n"
            elif self.mode=="unauthorized":value="List of devices attached\nA\tunauthorized\n"
            else:value="List of devices attached\nA\tdevice product:test\n"
        else:
            cmd=argv[4:]
            if cmd==["getprop","ro.product.model"]:value="Moto G Test"
            elif cmd==["getprop","ro.build.version.sdk"]:
                value="25" if self.mode=="sdk_old" else "35"
            elif cmd==["getprop","ro.product.cpu.abi"]:
                value="armeabi-v7a" if self.mode=="not_arm64" else "arm64-v8a"
            elif cmd==["pm","path",smoke.PACKAGE]:
                if self.mode=="missing_package":rc=1;value=""
                else:value="package:/data/app/IRL/base.apk\n"
            elif cmd[:1]==["monkey"]:
                self.launch_calls+=1
                value="Events injected: 0" if self.mode=="launch_failed" else "Events injected: 1"
            elif cmd[:1]==["pidof"]:
                value="" if self.mode=="crashed" else "45321"
                if self.mode=="crashed":rc=1
            elif cmd[:3]==["dumpsys","activity","activities"]:
                pkg="com.other.foreground" if self.mode=="background" else smoke.PACKAGE
                value="mResumedActivity: ActivityRecord{7fb u0 "+pkg+"/.MainActivity t9}\n"
            else: raise AssertionError(f"Unexpected fake ADB invocation: {argv}")
        return SimpleNamespace(returncode=rc,stdout=value,stderr="missing" if rc else "")

checks=0
with tempfile.TemporaryDirectory() as temp:
    root=make_project(temp)
    adb=FakeADB()
    path,r=smoke.execute(root,adb_path="fake-adb",run=adb,sleep=lambda _:None)
    assert r["status"]=="AUTHORIZED_DEVICE_AND_PACKAGE_FOUND_NO_LAUNCH",r
    assert adb.launch_calls==0
    assert r["device"]["model"]=="Moto G Test"
    assert len(r["device_serial_sha256"])==64
    assert "device_serial" not in r and "serial" not in r["device"]
    checks+=1

    adb=FakeADB()
    path,r=smoke.execute(root,adb_path="fake-adb",launch=True,run=adb,sleep=lambda _:None)
    assert r["status"]==smoke.PASS_STATUS,r
    assert adb.launch_calls==1
    assert len(r["samples"])==3
    assert all(row["foreground_is_irl"] for row in r["samples"])
    checks+=1
    for mode in ("two_devices","unauthorized","sdk_old","not_arm64",
                 "missing_package","launch_failed","crashed","background"):
        adb=FakeADB(mode)
        path,r=smoke.execute(root,adb_path="fake-adb",launch=True,run=adb,sleep=lambda _:None)
        assert r["status"]=="NOT_ESTABLISHED" and r["error"],(mode,r)
        assert path.exists()
        checks+=1
    try:
        smoke.execute(root,adb_path="fake-adb",checks=0)
    except ValueError:pass
    else:raise AssertionError("accepted no observations")
    checks+=1
    # Source evidence is optional and must never prove installation by itself.
    bad=Path(temp)/"false-apk.json"
    bad.write_text(json.dumps({"status":"NOT_ESTABLISHED"}))
    path,r=smoke.execute(root,adb_path="fake-adb",apk_report=bad,run=FakeADB())
    assert r["status"]=="NOT_ESTABLISHED"
    checks+=1
    wrong=Path(temp)/"not-irl"
    wrong.mkdir()
    (wrong/"IRL.uproject").write_text('{"EngineAssociation":"5.8","Modules":[]}')
    try:
        smoke.execute(wrong,adb_path="fake-adb",run=FakeADB())
    except smoke.SmokeFailure:pass
    else:raise AssertionError("wrong game was accepted")
    checks+=1
assert smoke.foreground_package("mResumedActivity: ActivityRecord{ u0 com.other/.Main }")=="com.other"
assert smoke.foreground_package("RecentTask com.bieexperience.irl/.Main") is None
assert smoke.parse_pid("12002 12003")==(12002,12003)
assert smoke.parse_pid("NaN") is None
checks+=1
print("PASS",checks,"ADB device evidence cases, all simulated; NOT A REAL PHONE TEST")
