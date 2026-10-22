# IRL — Original mobile PBR showcase asset pipeline (2026-10-22)

**ONE intended game:** `minttack/game/IRL` Unreal Engine 5.8. Independent candidate branch `workers/irl-original-pbr-showcase-20261022` is based on mobile graphics PR #6 (`17fa03680a9e86dec66d44e898f8ab2333454434`). **Do not replace or overwrite the game**. The parent PR #6 is still a draft; other unmerged workers #1–#5 address human duo, BIE experience, ecology, replication, and evidence.

## Creator direction

The earlier large IRL collage is **concept art**, not a screenshot. Target aesthetic: realistic planetary scale, dense nature, atmospheric lighting, lifelike evolving creatures, two human players in the shared starting world, autonomously learning BIE life, eventual orbit/space and god-mode observer functions. Decisions 026/029/030 remain authoritative. BIE runtime must remain independent and non-LLM.

## Actual new implementation

- `IRL/Tools/Visual/generate_irl_showcase.py` deterministically generates **3 procedural starter surface material sets** for forest soil, granite, green foliage. Each has 512² PNG `BaseColor`, `Normal`, `Roughness` and `Height` source maps by default, with a manifest containing SHA-256 per generated file. One source seed, no external/downstream game textures, no proprietary AAA copying.
- Creates native OBJ source meshes in **Unreal centimeters**: an 80 m square undulating terrain patch (4,225 vertices, 8,192 triangles), granite boulder (216 vertices, 360 triangles), grass clump (36 vertices, 12 triangles), plus contact-sheet PNG. These are intentionally modest starter art, not photogrammetric 3D scans or AAA production art.
- `IRL/Tools/Visual/import_into_unreal.py` is an **editor-only** Python script which imports `T_*` and `SM_IRL_*` into `/Game/IRL/Visual/ProceduralStarter`, sets linear roughness/normal channels, builds three basic PBR materials through Unreal's MaterialEditingLibrary, checks compiler errors, and **does not overwrite existing named assets or modify the original level**. Manual Unreal Editor placement and asset assignment to `AIRLLivingBiomeDetailActor` from PR #6 are still necessary. Editor Python plugin required.
- `score_mobile_capture.py` reads raw frame/GPU/thermal/memory CSV and reports average FPS, median/p95/p99 frame ms, 1% low FPS and performance gates. It rejects invalid/nonfinite/missing metadata and returns REVIEW_ELIGIBLE only if all p95/p99, GPU, RAM and temperature comparisons are within budgets. This is **not** automatic promotion: capture provenance, quality screenshots and repeated paired runs are still needed. Context metadata are supplied by the operator, not independently authenticated.

## Verified local results

Source asset generator was run twice at seed 20261022 in separate output directories: **17/17 output-file hashes identical** (16 generated files + manifest), validating determinism. Generated textures all pass dimensional/channel/normal-length and non-flat image checks. Three OBJ meshes passed indexed triangle/UV geometry checks. 15 importable source files are present, plus manifest and texture contact sheet.

Android capture scorer: **4 named test scenarios pass** for passing candidate, regressing candidate, incomplete comparison metadata, and invalid numeric samples. Tests used synthetic capture data and prove **only code validation**, not device FPS.

`import_into_unreal.py` passed local Python syntax compilation. **No Unreal Engine import, shader compilation, actual photoreal scene rendering, 2-player PIE, phone benchmark, Google Play package or Android APK was performed in this environment.** Existing game source was not overwritten or merged.

In this conversation a verified ZIP `IRL_Original_Mobile_PBR_Showcase_v0_1.zip` (23 entries, CRC verified, SHA-256 `87940e2ec173961bd1497ab38074a1cc4bf82cc84cd2512bd17cb04693b56d2c`) contains Python source, synthetic test harnesses, readme, and actual generated OBJ/PNG source art. The conversation attachment ZIP is not a GitHub release. ZIP paths may not persist in future environments. The main long-term authoritative copy is the GitHub **source pipeline**, not a replacement browser game.

## Reproduction

```sh
python -m pip install numpy pillow
python IRL/Tools/Visual/generate_irl_showcase.py --size 512 --seed 20261022
python IRL/Tools/Visual/test_generated_assets.py
python IRL/Tools/Visual/test_mobile_capture.py
```

In the actual Windows Unreal Editor, first enable its Python Editor Script Plugin, build PR #6 C++ scene actor, run `import_into_unreal.py` (with `IRL_PBR_SOURCE_DIR` set to the actual output directory), assign generated `SM_IRL_GrassClump`/ `SM_IRL_GraniteBoulder` and the matching `M_IRL_LeafGreen` / `M_IRL_Granite` to an opt-in biome detail actor inside the **real IRL map**. Assign soil material to terrain and inspect collision/tangents/normals. The script uses documented Unreal AssetImportTask and MaterialEditingLibrary APIs, but remains untested in UE.

## Next highest-impact gates to approach the concept art

1. Bring up Unreal 5.8 local editor, check all PR #6 C++ compile errors/Blueprint inheritance, import this generated asset pack and capture a first genuine *in-engine* screenshot of the existing IRL map.
2. Replace starter textures/mesh assets with original photogrammetry or license-cleared 1–2K PBR scans and properly authored topology/LOD, while retaining source provenance and per-device texture mip budgets. CC0 Poly Haven may be used following its actual license; do not copy proprietary Star Citizen/GTA meshes.
3. Add biome lighting, sky, terrain-grounding, water, atmosphere, weather, physically plausible creature shading/animation, and measured streaming/culling. Use the mobile forward/deferred features supported by **the actual phone**.
4. Profile a fixed walk path for at least repeated matched warmed runs, checking p95/p99 frame time, GPU time, memory, thermals and actual screenshots. Passing the synthetic scorer does not prove any speed improvement.
5. Integrate PRs #1–#5 through conflict-controlled branches after native UE regressions and 2-client Android tests, preserving autonomous BIE agents. Add actual evidence-backed life improvements and persistent memory, not claims of trillion fully simulated minds.

**Disposition:** original source art **generated and locally validated**, GitHub creation pipeline **implemented**, Android quality grader **implemented and locally tested**, Unreal import/runtime/rendering **not verified**, no main-branch merge or mobile release.
