"""IRL Android renderer and development deployment safety — config-only gate.

Reads the same authoritative IRL project as Unreal; independent of Unreal SDK.
This validates literal source settings, NOT cooked renderer state, device GPU
support, real phone FPS, binary config resolution, or Android signing.
"""
from pathlib import Path
import argparse
import configparser
import json

class AndroidConfigError(ValueError):
    pass

ANDROID_REQUIRED = {
    "r.Mobile.ShadingPath": "0",              # mobile forward
    "r.DynamicGlobalIlluminationMethod": "0", # no Lumen on budget phone
    "r.ReflectionMethod": "0",                # no desktop reflections
    "r.Shadow.Virtual.Enable": "0",           # no virtual shadow map
    "r.RayTracing": "False",
    "r.GenerateMeshDistanceFields": "False",
    "r.Substrate": "False",
}
POST_REQUIRED = {
    "r.MotionBlurQuality": "0",
    "r.DepthOfFieldQuality": "0",
    "r.BloomQuality": "0",
    "r.VolumetricFog": "0",
}
AFS_REQUIRED = {
    "bEnablePlugin": "False",
    "bAllowNetworkConnection": "False",
    "bIncludeInShipping": "False",
    "bAllowExternalStartInShipping": "False",
    "SecurityToken": "",
}

def parse_ini(path):
    file=Path(path)
    if not file.is_file():
        raise AndroidConfigError("Missing IRL Android source configuration: "+str(file))
    cfg=configparser.ConfigParser(interpolation=None,strict=False,delimiters=("=",),
                                  comment_prefixes=(";","#"))
    cfg.optionxform=str
    try:
        with file.open(encoding="utf8") as fp:
            cfg.read_file(fp)
    except (OSError,configparser.Error) as exc:
        raise AndroidConfigError("Invalid INI: "+str(file)) from exc
    return cfg

def must_equal(cfg,section,key,expected,location):
    found=cfg.get(section,key,fallback=None)
    if found!=expected:
        raise AndroidConfigError(
            location+" has "+section+"/"+key+"="+str(found)+"; expected "+expected)

def validate_android_config(project_dir):
    root=Path(project_dir).resolve()
    project=root/"IRL.uproject"
    if not project.is_file():
        raise AndroidConfigError("Not the same original IRL Unreal game")
    try:
        data=json.loads(project.read_text(encoding="utf8"))
    except (OSError,ValueError) as exc:
        raise AndroidConfigError("Malformed IRL project descriptor") from exc
    if data.get("EngineAssociation")!="5.8" or not any(
        x.get("Name")=="IRL" for x in data.get("Modules",[]) if isinstance(x,dict)):
        raise AndroidConfigError("Wrong Unreal version or different game source")

    general=parse_ini(root/"Config"/"DefaultEngine.ini")
    mobile=parse_ini(root/"Config"/"Android"/"AndroidEngine.ini")
    profiles=parse_ini(root/"Config"/"DefaultDeviceProfiles.ini")
    renderer="/Script/Engine.RendererSettings"
    if not general.has_section(renderer):
        raise AndroidConfigError("Missing desktop renderer source settings")
    # Desktop remains independently configurable. Verify that this platform
    # override does NOT replace the original renderer globally.
    must_equal(general,renderer,"r.RayTracing","True","desktop source")
    must_equal(general,renderer,"r.DynamicGlobalIlluminationMethod","1","desktop source")
    must_equal(general,renderer,"r.Shadow.Virtual.Enable","1","desktop source")
    for k,v in ANDROID_REQUIRED.items():
        must_equal(mobile,renderer,k,v,"Android platform override")
    for k,v in POST_REQUIRED.items():
        must_equal(mobile,"SystemSettings",k,v,"Android runtime")
    must_equal(mobile,renderer,"r.MobileHDR","True","Android material fidelity")

    afs="/Script/AndroidFileServerEditor.AndroidFileServerRuntimeSettings"
    for k,v in AFS_REQUIRED.items():
        must_equal(general,afs,k,v,"Android deployment safety")
    android="/Script/AndroidRuntimeSettings.AndroidRuntimeSettings"
    for k,v in {
        "bBuildForArm64":"True",
        "TargetSDKVersion":"35",
        "bSupportsOpenGLES3":"True",
        "bSupportsVulkan":"False",
    }.items():
        must_equal(general,android,k,v,"Android packaging")
    for tier in ("Android_Low DeviceProfile","Android_Mid DeviceProfile","Android_High DeviceProfile"):
        if not profiles.has_section(tier):
            raise AndroidConfigError("Missing mobile GPU tier "+tier)
        entries=profiles.get(tier,"+CVars",fallback=None)
        # ConfigParser only preserves the last repeated +CVars entry, so parse
        # the actual line-oriented source list separately below.
        if entries is None:raise AndroidConfigError("Mobile GPU tier lacks CVars: "+tier)
    source=(root/"Config"/"DefaultDeviceProfiles.ini").read_text(encoding="utf8")
    for name,raw in (("Android_Low",96),("Android_Mid",160),("Android_High",256)):
        section=source.split("["+name+" DeviceProfile]",1)
        if len(section)<2 or "+CVars=r.Streaming.PoolSize="+str(raw) not in section[1].split("[",1)[0]:
            raise AndroidConfigError(name+" lacks the intended mobile texture pool")

    return {
        "status":"ANDROID_CONFIG_SOURCE_POLICY_PASS_NOT_COMPILED",
        "game":"ONE original IRL Unreal 5.8",
        "renderer":"ANDROID_MOBILE_FORWARD",
        "desktop_source_unchanged_by_platform_override":True,
        "android_file_server":"DISABLED",
        "gpu_tiers":["Android_Low","Android_Mid","Android_High"],
        "limitations":[
            "ConfigParser source validation does not establish Unreal platform merge semantics.",
            "No compilation, actual MobileHDR shading, phone GPU compatibility or FPS was measured.",
            "Earlier committed/publicly shared file-server tokens must not be reused."
        ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",type=Path,default=Path(__file__).resolve().parents[2])
    args=ap.parse_args()
    print(json.dumps(validate_android_config(args.project_root),indent=2))

if __name__=="__main__":main()
