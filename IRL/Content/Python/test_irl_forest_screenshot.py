"""Take the FIRST GENUINE IRL Unreal Editor screenshot after physical audit.

Requires Unreal Engine 5.8 + PythonAutomationTest plugin; runs through
Session Frontend > Automation > Editor > Python > IRL, not the phone.
Does not create, replace or save gameplay levels or add fake CGI imagery.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import struct
import sys
import time
import unreal

TOOLS = Path(__file__).resolve().parents[2] / "Tools" / "Visual"
sys.path.insert(0, str(TOOLS))
from forest_world_evidence import EXPECTED_MAP
from probe_unreal_forest import main as audit

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


def _png_dimensions(path):
    with Path(path).open("rb") as f:
        header=f.read(24)
    if len(header)<24 or header[:8]!=b"\x89PNG\r\n\x1a\n" or header[12:16]!=b"IHDR":
        raise RuntimeError("Saved screenshot is not a valid PNG header")
    return struct.unpack(">II",header[16:24])


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
    dimensions=_png_dimensions(filepath)
    if dimensions!=(1280,720):
        raise RuntimeError("Incorrect captured Unreal screenshot size: "+str(dimensions))
    size=filepath.stat().st_size
    if size<10_000:
        raise RuntimeError("Unreal screenshot looks incomplete or too small")
    evidence={
        "source":"actual_unreal_editor_image_file",
        "project":"ONE IRL Unreal Engine 5.8 game",
        "map":EXPECTED_MAP,
        "captured_utc":now.isoformat(),
        "file":str(filepath),
        "sha256":hashlib.sha256(filepath.read_bytes()).hexdigest(),
        "size_bytes":size,
        "width":dimensions[0],
        "height":dimensions[1],
        "physics_preflight":state["audit"],
        "device":"DESKTOP_UNREAL_EDITOR_NOT_ANDROID",
        "disposition":"SCREENSHOT_FILE_VERIFIED_NOT_AAA_OR_GAMEPLAY_PROOF",
    }
    target=Path(unreal.Paths.project_saved_dir())/"IRL"/"forest_genuine_screenshot_evidence.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(evidence,indent=2),encoding="utf8")
    unreal.log("IRL captured real screenshot with SHA-256: "+str(filepath))
