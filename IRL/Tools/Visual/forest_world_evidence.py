"""BIE Experience — source-reported Unreal forest observation assessment.

Pure Python; no Unreal dependency. Does not confuse a claimed trace with
independently measured device runtime. Fail closed on missing/malformed data.
"""
import math

EXPECTED_MAP = "/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation"
EXPECTED_ACTORS = {"terrain": 1, "biome": 4, "player_start": 1}
PROBE_NAMES = {
    "grid_-1_-1", "grid_-1_0", "grid_-1_1",
    "grid_0_-1", "grid_0_0", "grid_0_1",
    "grid_1_-1", "grid_1_0", "grid_1_1",
    "biome_00", "biome_01", "biome_02", "biome_03",
    "player_start",
}
MAX_VISUAL_INSTANCES_PER_BIOME = 725  # 460 grass + 75 rocks + 190 litter
MIN_GROUND_NORMAL_Z = 0.70


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def assess_scene_report(report):
    """Return bounded, explainable source-reported outcome, never invented."""
    errors = []
    if not isinstance(report, dict):
        return {"status": "NOT_ESTABLISHED", "errors": ["Invalid report"], "source": "unknown"}
    source = report.get("source")
    if source != "unreal_editor_line_trace":
        errors.append("Source is not a declared Unreal editor trace")
    if report.get("map_path") != EXPECTED_MAP:
        errors.append("Not the isolated IRL forest validation map")
    counts = report.get("actor_counts")
    if not isinstance(counts, dict) or any(counts.get(k) != v for k, v in EXPECTED_ACTORS.items()):
        errors.append("Ground, biome or player actor counts incorrect")

    probes = report.get("ground_probes")
    checked = set()
    if not isinstance(probes, list) or len(probes) != len(PROBE_NAMES):
        errors.append("Incomplete or oversized ground-probe set")
        probes = []
    for p in probes:
        if not isinstance(p, dict):
            errors.append("Malformed ground observation")
            continue
        name = p.get("name")
        if name not in PROBE_NAMES or name in checked:
            errors.append("Unknown or repeated ground observation")
        checked.add(name)
        if p.get("hit_actor") != "IRL_OriginalForestTerrain" or p.get("blocking") is not True:
            errors.append("Ground probe does not hit blocking IRL terrain")
        if not _number(p.get("normal_z")) or p["normal_z"] < MIN_GROUND_NORMAL_Z or p["normal_z"] > 1.0001:
            errors.append("Ground is not walkable or normal is invalid")
        if not _number(p.get("ground_z_cm")) or abs(p["ground_z_cm"]) > 600.0:
            errors.append("Ground elevation is invalid")
        if name == "player_start":
            clearance = p.get("spawn_clearance_cm")
            if not _number(clearance) or not 110.0 <= clearance <= 1000.0:
                errors.append("PlayerStart is not safely above traced terrain")
    if checked != PROBE_NAMES:
        errors.append("Missing named ground observations")

    patches = report.get("biome_instances")
    if not isinstance(patches, dict) or set(patches) != {f"IRL_Biome_{i:02d}" for i in range(4)}:
        errors.append("Missing or extra biome instance evidence")
    else:
        for patch in patches.values():
            if (not isinstance(patch, dict) or
                set(patch) != {"grass", "rocks", "litter"} or
                any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in patch.values())):
                errors.append("Malformed biome instance counts")
                continue
            if not 1 <= sum(patch.values()) <= MAX_VISUAL_INSTANCES_PER_BIOME:
                errors.append("Biome is empty or exceeds configured visual budget")

    assets = report.get("assigned_assets")
    if not isinstance(assets, dict) or not all(assets.get(k) is True for k in ("soil", "granite", "foliage")):
        errors.append("Assigned Unreal material/mesh missing")
    # This is only a proposal for a physical Unreal editor probe. It is NOT an
    # actual device performance measurement or independently attested evidence.
    return {
        "status": "EDITOR_REVIEW_ELIGIBLE" if not errors else "NOT_ESTABLISHED",
        "source": source if isinstance(source, str) else "unknown",
        "tests": len(checked),
        "errors": sorted(set(errors)),
        "limitations": [
            "Report values are emitted by the editor probe and are not independently authenticated.",
            "Unreal editor collision is not a packaged-game character movement or Android performance test.",
            "This result never establishes AAA photorealism, persistent BIE intelligence, or multiplayer."
        ]
    }
