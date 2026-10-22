"""Read-only audit of the ACTUAL binary Unreal GameMode/Controller/Pawn chain.

Run inside Unreal Editor 5.8 Tools > Execute Python Script.
Never edits .uasset files or silently replaces the original BP game.
"""
from pathlib import Path
from datetime import datetime,timezone
import json

GAME_MODE_CLASS="/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode.BP_ThirdPersonGameMode_C"
EXPECTED_PROJ="IRL"

def inspect_chain(unreal):
    report={"source":"IRL_UNREAL_EDITOR_BLUEPRINT_CLASS_AUDIT",
            "default_game_mode":GAME_MODE_CLASS,
            "status":"NOT_ESTABLISHED",
            "observed_utc":datetime.now(timezone.utc).isoformat(),
            "checks":{}}
    try:
        game_class=unreal.load_class(None,GAME_MODE_CLASS)
        if game_class is None:
            raise RuntimeError("Original starting GameMode BP class missing")
        obj=unreal.get_default_object(game_class)
        player_class=obj.get_editor_property("player_controller_class")
        pawn_class=obj.get_editor_property("default_pawn_class")
        if player_class is None or pawn_class is None:
            raise RuntimeError("GameMode lacks player controller or default pawn class")
        p=unreal.get_default_object(player_class)
        c=unreal.get_default_object(pawn_class)
        checks={
            "irl_game_mode":isinstance(obj,unreal.IRLGameMode),
            "irl_controller":isinstance(p,unreal.IRLPlayerController),
            "irl_character":isinstance(c,unreal.IRLCharacter),
        }
        report["checks"]=checks
        report["active_classes"]={
            "game_mode":str(game_class.get_path_name()),
            "player_controller":str(player_class.get_path_name()),
            "pawn":str(pawn_class.get_path_name()),
        }
        report["status"]="EDITOR_CLASS_CHAIN_REVIEW_ELIGIBLE" if all(checks.values()) else "NOT_ESTABLISHED"
        if not all(checks.values()):
            report["error"]="Default Blueprint class chain will NOT run one or more IRL native mobile systems"
    except Exception as exc:
        report["error"]=str(exc)
    return report

def main(unreal):
    report=inspect_chain(unreal)
    target=Path(unreal.Paths.project_saved_dir())/"IRL"/"android_blueprint_class_audit.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2),encoding="utf8")
    unreal.log("IRL native mobile class audit: "+report["status"]+" "+str(target))
    if report["status"]!="EDITOR_CLASS_CHAIN_REVIEW_ELIGIBLE":
        raise RuntimeError("IRL phone bindings not proven active: "+str(target))
    return target

if __name__=="__main__":
    import unreal
    main(unreal)
