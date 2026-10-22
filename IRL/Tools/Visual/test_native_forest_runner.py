"""FAKE executable contract tests, not a real Unreal build or forest.

Run against the actual IRL native runner; tests process launch/exit, fresh evidence,
correct project identity, failures, and report dispositions in isolation.
"""
import tempfile
from pathlib import Path
import json
import sys
import irl_native_forest_runner as runner

def make_executable(path, source):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("#!/usr/bin/env python3\n"+source,encoding="utf-8")
    path.chmod(0o755)

def fixture(where, report="good", build_exit=0, editor_exit=0):
    root=Path(where)/"IRL"
    (root/"Source").mkdir(parents=True)
    (root/"Source"/"IRLEditor.Target.cs").write_text("class IRLEditorTarget {}")
    (root/"IRL.uproject").write_text(json.dumps({"EngineAssociation":"5.8",
                                                "Modules":[{"Name":"IRL"}]}))
    visual=root/"Tools"/"Visual"
    visual.mkdir(parents=True)
    for name in ("run_irl_forest_validation.py","generate_irl_showcase.py"):
        (visual/name).write_text("# mocked supporting source")
    # The real policy has its own independent full regression suite.
    (visual/"forest_world_evidence.py").write_text('''def assess_scene_report(r):
    ok = (r.get("source")=="unreal_editor_line_trace" and
          r.get("map_path")=="/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation" and
          len(r.get("ground_probes",[]))==14)
    return {"status":"EDITOR_REVIEW_ELIGIBLE" if ok else "NOT_ESTABLISHED",
            "tests":len(r.get("ground_probes",[])),
            "errors":[] if ok else ["invalid evidence"]}
''')
    engine=Path(where)/"UE_5.8"
    make_executable(engine/"Engine"/"Build"/"BatchFiles"/"Build.bat",
                    "import sys\nprint('FAKE BUILD')\nsys.exit("+str(build_exit)+")\n")
    fake_editor=f'''import json,sys
from pathlib import Path
from datetime import datetime,timezone
project=Path(sys.argv[1])
saved=project.parent/"Saved"/"IRL"
saved.mkdir(parents=True,exist_ok=True)
kind={report!r}
if kind!="missing":
    obs=("2000-01-01T00:00:00+00:00" if kind=="stale"
         else datetime.now(timezone.utc).isoformat())
    value={{"source":"unreal_editor_line_trace",
           "map_path":"/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation",
           "observed_utc":obs,
           "ground_probes":[{{"name":i}} for i in range(14)],
           "assessment":{{"status":"EDITOR_REVIEW_ELIGIBLE"}}}}
    if kind=="wrong_map":value["map_path"]="/Game/Wrong"
    if kind=="bad_count":value["ground_probes"]=[]
    (saved/"forest_editor_audit_fake.json").write_text(json.dumps(value))
print("FAKE EDITOR")
sys.exit({editor_exit})
'''
    make_executable(engine/"Engine"/"Binaries"/"Win64"/"UnrealEditor-Cmd.exe",fake_editor)
    return root,engine

# A fixture avoids generating costly art; the real art-integrity checks run
# separately in this SAME repository's original mobile graphics CI.
old=runner.verify_generated_art
runner.verify_generated_art=lambda root,generator,python=sys.executable:{"source_files":16}
cases=0
with tempfile.TemporaryDirectory() as folder:
    root,engine=fixture(folder)
    path,result=runner.execute(root,engine,"preflight")
    assert result["status"]=="ENVIRONMENT_READY_NOT_ENGINE_TESTED" and "editor" not in result
    assert json.loads(path.read_text())["status"]==result["status"]
    cases+=1
    path,result=runner.execute(root,engine,"build-and-audit")
    assert result["status"]=="EDITOR_REVIEW_ELIGIBLE_NOT_PLAYABLE_OR_ANDROID",result
    assert result["build"]["exit_code"]==result["editor"]["exit_code"]==0
    assert result["editor_evidence"]["observations"]==14
    cases+=1
with tempfile.TemporaryDirectory() as folder:
    root,engine=fixture(folder,build_exit=7)
    _,result=runner.execute(root,engine,"build-and-audit")
    assert result["status"]=="NOT_ESTABLISHED" and "exited 7" in result["error"]
    assert "editor" not in result
    cases+=1
with tempfile.TemporaryDirectory() as folder:
    root,engine=fixture(folder,editor_exit=4)
    _,result=runner.execute(root,engine,"audit-only")
    assert result["status"]=="NOT_ESTABLISHED" and "exited 4" in result["error"]
    cases+=1
for condition in ("missing","stale","wrong_map","bad_count"):
    with tempfile.TemporaryDirectory() as folder:
        root,engine=fixture(folder,report=condition)
        _,result=runner.execute(root,engine,"audit-only")
        assert result["status"]=="NOT_ESTABLISHED",(condition,result)
        cases+=1
with tempfile.TemporaryDirectory() as folder:
    root,engine=fixture(folder)
    _,result=runner.execute(root,Path(folder)/"MissingEngine","build-and-audit")
    assert result["status"]=="NOT_ESTABLISHED" and "Unreal Engine 5.8" in result["error"]
    cases+=1
with tempfile.TemporaryDirectory() as folder:
    root,engine=fixture(folder)
    desc=json.loads((root/"IRL.uproject").read_text())
    desc["EngineAssociation"]="5.6"
    (root/"IRL.uproject").write_text(json.dumps(desc))
    try:runner.validate_irl_project(root)
    except RuntimeError as exc:assert "association" in str(exc)
    else:raise AssertionError("Wrong UE version accepted")
    cases+=1
runner.verify_generated_art=old
print(f"PASS {cases} native runner process-control cases with fake executables; no UE invoked")
