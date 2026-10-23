"""Actual IRL Android renderer source-contract tests, no GPU/UE claims."""
from pathlib import Path
import shutil
import tempfile
import json
from android_renderer_gate import validate_android_config, AndroidConfigError

SRC=Path(__file__).resolve().parents[2]
checks=0
with tempfile.TemporaryDirectory() as temp:
    target=Path(temp)/"IRL"
    (target/"Config"/"Android").mkdir(parents=True)
    for file in (
        "IRL.uproject", "Config/DefaultEngine.ini",
        "Config/Android/AndroidEngine.ini", "Config/DefaultDeviceProfiles.ini"):
        (target/file).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(SRC/file,target/file)
    ok=validate_android_config(target)
    assert ok["status"]=="ANDROID_CONFIG_SOURCE_POLICY_PASS_NOT_COMPILED"
    assert ok["desktop_source_unchanged_by_platform_override"]
    checks+=1

    def check_fail(path,old,new,reason):
        global checks
        file=target/path
        original=file.read_text()
        assert old in original,reason
        file.write_text(original.replace(old,new,1),encoding="utf8")
        try:validate_android_config(target)
        except AndroidConfigError:pass
        else:raise AssertionError("Unsafe IRL config accepted: "+reason)
        finally:file.write_text(original,encoding="utf8")
        checks+=1

    mobile=Path("Config/Android/AndroidEngine.ini")
    general=Path("Config/DefaultEngine.ini")
    profile=Path("Config/DefaultDeviceProfiles.ini")
    check_fail(mobile,"r.Mobile.ShadingPath=0","r.Mobile.ShadingPath=1","mobile deferred")
    check_fail(mobile,"r.DynamicGlobalIlluminationMethod=0",
               "r.DynamicGlobalIlluminationMethod=1","desktop Lumen on phone")
    check_fail(mobile,"r.RayTracing=False","r.RayTracing=True","ray tracing enabled")
    check_fail(mobile,"r.Shadow.Virtual.Enable=0","r.Shadow.Virtual.Enable=1","virtual shadows")
    check_fail(mobile,"r.MobileHDR=True","r.MobileHDR=False","unexpected fidelity change")
    check_fail(mobile,"r.BloomQuality=0","r.BloomQuality=5","GPU post-process bloom overhead")
    check_fail(general,"bEnablePlugin=False","bEnablePlugin=True","Android File Server restarted")
    check_fail(general,"bAllowNetworkConnection=False",
               "bAllowNetworkConnection=True","file server network access")
    check_fail(general,"SecurityToken=\n","SecurityToken=published-token\n","exposed access token")
    check_fail(general,"bIncludeInShipping=False",
               "bIncludeInShipping=True","file server shipping exposure")
    check_fail(general,"bSupportsVulkan=False","bSupportsVulkan=True","unexpected renderer switch")
    check_fail(general,"TargetSDKVersion=35","TargetSDKVersion=27","SDK regression")
    check_fail(profile,"+CVars=r.Streaming.PoolSize=96",
               "+CVars=r.Streaming.PoolSize=2048","low-end texture pool explosion")
    check_fail(general,"r.RayTracing=True","r.RayTracing=False",
               "desktop renderer overwritten")
    check_fail(Path("IRL.uproject"),'"EngineAssociation": "5.8"',
               '"EngineAssociation": "5.4"',"wrong engine version")
    (target/"Config"/"Android"/"AndroidEngine.ini").unlink()
    try:validate_android_config(target)
    except AndroidConfigError:pass
    else:raise AssertionError("Missing platform overlay accepted")
    checks+=1
print("PASS",checks,"Android config safety/fidelity source cases; UE/phone untested")
