"""IRL visual validation: single explicit Unreal Editor run action.

UE 5.8 Python Editor Script Plugin required.
First run the original PBR generator or obtain the exact CI-generated art.
Execute in Tools > Execute Python Script. Never changes DefaultEngine.ini
or overwrites the original game map.
"""
from pathlib import Path
import os
import sys
import runpy

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from build_irl_forest_validation_level import make as build, NEW_MAP
from probe_unreal_forest import main as audit

def run(unreal):
    if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
        raise RuntimeError("Exit Play-In-Editor before building or auditing IRL forest")
    assets = unreal.EditorAssetLibrary
    if assets.does_asset_exist(NEW_MAP):
        # Never run the editor material importer or builder over an existing map.
        if not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(NEW_MAP):
            raise RuntimeError("Existing IRL forest validation map could not be opened")
    else:
        source = Path(os.environ.get("IRL_PBR_SOURCE_DIR", str(THIS / "Generated")))
        if not source.is_dir():
            raise RuntimeError(
                "Missing original generated graphics folder. Run "
                "generate_irl_showcase.py on your PC, or extract the GitHub "
                "Actions original PBR artifact to IRL/Tools/Visual/Generated.")
        runpy.run_path(str(THIS / "import_into_unreal.py"), run_name="__main__")
        build(unreal)  # Creates a NEW uniquely named map; never replaces default
    # Real editor-world collision evidence, material checks, and instance counts.
    return audit(unreal)


if __name__ == "__main__":
    import unreal
    report = run(unreal)
    unreal.log("IRL candidate forest editor review eligible: " + str(report))
