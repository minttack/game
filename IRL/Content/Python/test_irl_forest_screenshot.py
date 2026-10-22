"""Take the FIRST GENUINE IRL Unreal Editor screenshot after physical audit.

Requires Unreal Engine 5.8 + PythonAutomationTest plugin; runs through
Session Frontend > Automation > Editor > Python > IRL, not the phone.
Does not create, replace or save gameplay levels or add fake CGI imagery.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import time
import unreal

TOOLS = Path(__file__).resolve().parents[2] / "Tools" / "Visual"
sys.path.insert(0, str(TOOLS))
from forest_world_evidence import EXPECTED_MAP
from probe_unreal_forest import main as audit
from forest_screenshot_evidence import verify_capture_png

NAME = "IRL_First_Actual_Unreal_Forest_1280x720"
state = {}
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def _matching_pngs(saved_dir, started_at):
    # UE screenshots may live inside Saved/Screenshots or Automation subfolders.
    folder=Path(saved_dir)
    if not folder.is_dir(): return []
    return sorted(
        [p for p in folder.rglob("*.png") if NAME in p.stem and
         p.stat().st_mtime >= started_at-3],
        key=lambda p:p.stat().st_mtime,reverse=True)


@unreal.AutomationScheduler.add_latent_command
def load_real_original_irl_visual_map():
    if level.is_in_play_in_editor():
        raise RuntimeError("IRL screenshot must run in Editor, not during PIE")
    if not unreal.EditorAssetLibrary.does_asset_exist(EXPECTED_MAP):
        raise RuntimeError("First build IRL forest map using the original project scripts")
    if not level.load_level(EXPECTED_MAP):
        raise RuntimeError("Cannot open authentic IRL forest test map")


@unreal.AutomationScheduler.add_latent_command
def physically_validate_scene_before_rendering():
    state["audit"]=str(audit(unreal))  # throws for any collision/foliage failure
    editor.set_level_viewport_camera_info(
        unreal.Vector(14800.0,-4600.0,2500.0),
        unreal.Rotator(pitch=-15.0,yaw=36.0,roll=0.0))
    level.editor_set_viewport_realtime(True)
    level.editor_set_game_view(True)


@unreal.AutomationScheduler.add_latent_command
def capture_real_unreal_pixels():
    now=datetime.now(timezone.utc)
    started=time.time()
    task=unreal.AutomationLibrary.take_high_res_screenshot(
        1280,720,NAME,camera=None)
    if task is None or not task.is_valid_task():
        raise RuntimeError("Unreal screenshot task was never accepted")

    for _ in range(300):
        if task.is_task_done(): break
        yield  # allow actual editor frames and rendering to complete
    if not task.is_task_done():
        raise RuntimeError("Unreal screenshot did not complete within 300 editor frames")
    # Screenshots are evidence only when an actual PNG can be found and read.
    # The automation task itself being done is not sufficient.
    files=_matching_pngs(unreal.Paths.project_saved_dir(),started)
    if not files:
        raise RuntimeError(
            "Screenshot task completed but no matching PNG is readable in Project/Saved; "
            "check Unreal Automation screenshot storage; do not claim success")
    filepath=files[0]
    verified=verify_capture_png(filepath,expected=(1280,720))
    evidence={
        "source":"actual_unreal_editor_image_file",
        "project":"ONE IRL Unreal Engine 5.8 game",
        "map":EXPECTED_MAP,
        "captured_utc":now.isoformat(),
        "file":str(filepath),
        "sha256":verified["sha256"],
        "size_bytes":verified["bytes"],
        "width":verified["width"],
        "height":verified["height"],
        "file_format_check":verified["verified_format"],
        "physics_preflight":state["audit"],
        "device":"DESKTOP_UNREAL_EDITOR_NOT_ANDROID",
        "disposition":"SCREENSHOT_FILE_VERIFIED_NOT_AAA_OR_GAMEPLAY_PROOF",
    }
    target=Path(unreal.Paths.project_saved_dir())/"IRL"/"forest_genuine_screenshot_evidence.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(evidence,indent=2),encoding="utf8")
    unreal.log("IRL captured real screenshot with SHA-256: "+str(filepath))
