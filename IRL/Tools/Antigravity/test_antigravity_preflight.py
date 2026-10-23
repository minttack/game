"""Source-only tests for Antigravity IRL preflight, no Unreal or APK built."""
from pathlib import Path
import json
import shutil
import tempfile
import irl_antigravity_preflight as pre

project=Path(__file__).resolve().parents[2]
checks=0
good=pre.check_source(project)
assert good==project.resolve()
checks+=1
report=pre.preflight(project)
assert report["project"]=="IRL" and report["device_or_apk_test"]=="NOT_RUN"
assert report["native_unreal_build"]=="NOT_RUN"
assert report["package"]=="com.bieexperience.irl"
checks+=1
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)/"IRL"
    for rel in pre.REQUIRED_SOURCE:
        target=root/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(project/rel,target)
    assert pre.check_source(root)==root.resolve()
    checks+=1
    up=root/"IRL.uproject"
    real=up.read_text()
    up.write_text(real.replace('"EngineAssociation": "5.8"','"EngineAssociation": "5.4"'))
    try:pre.check_source(root)
    except ValueError:pass
    else:raise AssertionError("wrong engine version accepted")
    up.write_text(real)
    checks+=1
    up.write_text(real.replace('"Name": "IRL"', '"Name": "OtherGame"'))
    try:pre.check_source(root)
    except ValueError:pass
    else:raise AssertionError("different Unreal game accepted")
    up.write_text(real)
    checks+=1
    android=root/"Config"/"Android"/"AndroidEngine.ini"
    original=android.read_text()
    android.write_text(original.replace("r.Mobile.ShadingPath=0","r.Mobile.ShadingPath=1"))
    try:pre.check_source(root)
    except ValueError:pass
    else:raise AssertionError("desktop path presented as Android-safe")
    android.write_text(original)
    checks+=1
    cpp=root/"Source"/"IRL"/"Mobile"/"IRLMobileTouchHUD.cpp"
    cpp.unlink()
    try:pre.check_source(root)
    except ValueError:pass
    else:raise AssertionError("IRL native touch source missing but accepted")
    checks+=1

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)/"UE_5.8"
    for path in ("Engine/Build/BatchFiles/RunUAT.bat",
                 "Engine/Binaries/Win64/UnrealEditor-Cmd.exe"):
        dest=root/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text("mock marker, never execute")
    a=pre.check_toolchain(engine_root=root,env={})
    assert a["unreal_5_8_executables_found"] is True
    checks+=1
    (root/"Engine/Binaries/Win64/UnrealEditor-Cmd.exe").unlink()
    b=pre.check_toolchain(engine_root=root,env={})
    assert b["unreal_5_8_executables_found"] is False
    checks+=1
    assert b["adb_in_path"] in (True,False)
    checks+=1
# Antigravity MCP instructions must never publish a remote tool server.
mcp=json.loads((Path(__file__).with_name("mcp_config.EXAMPLE.json")).read_text())
assert set(mcp["mcpServers"])=={"unreal-mcp"}
assert mcp["mcpServers"]["unreal-mcp"]["serverUrl"]=="http://127.0.0.1:[YOUR_PORT]/mcp"
assert "ONE" in (project.parent/"AGENTS.md").read_text()
checks+=1
print("PASS",checks,"read-only Antigravity workspace preflight tests; no Unreal invocation")
