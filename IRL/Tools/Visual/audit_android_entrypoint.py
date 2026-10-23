"""IRL Android: evidence-gated EFFECTIVE startup GameMode/Controller/Pawn.

The Unreal Editor reads the real binary BP assets and the map WorldSettings;
source-only CI never asserts the binary GameMode parentage is correct.

Never edits any Unreal asset. Intended before RunUAT Android packaging.
"""
from datetime import datetime, timezone
from pathlib import Path
import configparser
import json
import sys

DEFAULT_MAP="/Game/ThirdPerson/Lvl_ThirdPerson"
DEFAULT_MODE="/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode.BP_ThirdPersonGameMode_C"
STATUS_OK="EDITOR_EFFECTIVE_IRL_ENTRYPOINT_VERIFIED_NOT_DEVICE_TESTED"

def read_project_defaults(project_root):
    path=Path(project_root)/"Config"/"DefaultEngine.ini"
    ini=configparser.ConfigParser(interpolation=None,strict=False)
    ini.optionxform=str
    with path.open(encoding="utf8") as stream:
        ini.read_file(stream)
    section="/Script/EngineSettings.GameMapsSettings"
    return {
        "map":ini.get(section,"GameDefaultMap",fallback=""),
        "global_mode":ini.get(section,"GlobalDefaultGameMode",fallback=""),
    }

def normalize_class_path(value):
    return str(value).strip()

def effective_mode(global_mode,level_override):
    return normalize_class_path(level_override or global_mode)

def assess_classes(map_path, global_mode_path, override_path, hierarchy):
    errs=[]
    if map_path != DEFAULT_MAP:errs.append("Android cook map is not original IRL level")
    if not global_mode_path:errs.append("No project GameMode configured")
    if not isinstance(hierarchy,dict):hierarchy={}
    for k in ("game_mode","controller","character"):
        if hierarchy.get(k) is not True:
            errs.append("Effective "+k+" does not inherit the original IRL native base")
    if not hierarchy.get("has_blueprint_character"):
        errs.append("No original rendered playable character Blueprint confirmed")
    return {
        "status":STATUS_OK if not errs else "NOT_ESTABLISHED",
        "errors":errs,
        "effective_mode_source":"LEVEL_OVERRIDE" if override_path else "PROJECT_DEFAULT",
        "effective_mode":effective_mode(global_mode_path,override_path),
        "limitations":[
            "This inspects editor Blueprint ancestry, NOT a successful Android cook.",
            "World Settings and original character assets are never modified.",
            "It does not establish touch responsiveness, multiplayer, BIE life or phone FPS.",
        ]
    }

def probe_editor(unreal, project_root):
    settings=read_project_defaults(project_root)
    configured=settings["map"].split(".",1)[0]
    if configured!=DEFAULT_MAP:
        raise RuntimeError("Refusing non-original IRL startup map "+configured)
    editor=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if editor.is_in_play_in_editor():
        raise RuntimeError("Exit Play-In-Editor before reading class chain")
    if not editor.load_level(DEFAULT_MAP):
        raise RuntimeError("Original IRL starter level could not be loaded")
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None:
        raise RuntimeError("Unreal editor World is missing")
    settings_actor=world.get_world_settings()
    if settings_actor is None:
        raise RuntimeError("Cannot inspect actual level WorldSettings")
    override=settings_actor.get_editor_property("default_game_mode")
    override_path=normalize_class_path(override.get_path_name()) if override else ""
    global_path=settings["global_mode"]
    effective_class=override if override else unreal.load_class(None,global_path)
    if effective_class is None:
        raise RuntimeError("Effective GameMode class could not be loaded")
    game_cdo=unreal.get_default_object(effective_class)
    controller_class=game_cdo.get_editor_property("player_controller_class")
    pawn_class=game_cdo.get_editor_property("default_pawn_class")
    if controller_class is None or pawn_class is None:
        raise RuntimeError("Actual GameMode has no controller/pawn Blueprint")
    controller=unreal.get_default_object(controller_class)
    character=unreal.get_default_object(pawn_class)
    hierarchy={
        "game_mode":isinstance(game_cdo,unreal.IRLGameMode),
        "controller":isinstance(controller,unreal.IRLPlayerController),
        "character":isinstance(character,unreal.IRLCharacter),
        # Both native IRLCharacter and IRLPlayerController are ABSTRACT:
        # only a non-abstract Blueprint-derived playable character is valid.
        "has_blueprint_character":normalize_class_path(pawn_class.get_path_name()).startswith(
            "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter."),
    }
    assessment=assess_classes(configured,global_path,override_path,hierarchy)
    return {
        "source":"REAL_UNREAL_EDITOR_BINARY_CLASS_INSPECTION",
        "observed_utc":datetime.now(timezone.utc).isoformat(),
        "map_path":configured,
        "global_default_mode":global_path,
        "map_mode_override":override_path,
        "effective_mode":effective_class.get_path_name(),
        "player_controller_class":controller_class.get_path_name(),
        "default_pawn_class":pawn_class.get_path_name(),
        "hierarchy":hierarchy,
        "assessment":assessment,
    }

def main(unreal,root=None):
    root=Path(root) if root else Path(unreal.Paths.project_dir())
    target=Path(unreal.Paths.project_saved_dir())/"IRL"/"android_effective_entrypoint.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        report=probe_editor(unreal,root)
    except Exception as exc:
        report={
            "source":"REAL_UNREAL_EDITOR_BINARY_CLASS_INSPECTION",
            "observed_utc":datetime.now(timezone.utc).isoformat(),
            "assessment":{"status":"NOT_ESTABLISHED","errors":[str(exc)]},
        }
    target.write_text(json.dumps(report,indent=2),encoding="utf8")
    if report["assessment"]["status"]!=STATUS_OK:
        raise RuntimeError("IRL Android effective GameMode check FAILED; see "+str(target))
    unreal.log("IRL real Android class chain passed: "+str(target))
    return target

if __name__=="__main__":
    import unreal
    main(unreal)
