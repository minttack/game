# IRL — Android Maximum Fidelity / BIE Visual Evidence (2026-10-22)

## Authoritative continuity and disposition
- **ONE existing IRL game:** `https://github.com/minttack/game`, Unreal Engine 5.8 project `IRL/IRL.uproject`.
- Base verified main: `261cbbbb8264dfde6943cd0fa304029d4867dd3e`. This is an independent, reviewable graphics worker branch, not a replacement game.
- Prior independent unmerged workers #1 (duo mobile), #2 (non-LLM BIE learning), #3 (ecology), #4 (duo ecology replication), #5 (Experience evidence gate). **Do not overwrite or silently merge them.**
- Vision: realistic living 3D worlds, two human players, BIE-guided autonomous inhabitants, strong mobile visuals, truthful measurements. Decisions 026/029/030 remain unchanged.
- This release candidate adds native graphics *infrastructure*. It does **not** ship a photographed/AAA landscape, imported premium art, a polished game scene or Android APK.

## What actually changed
1. `IRL/Source/IRL/Visual/IRLVisualBudgetCore.h`: pure C++17, non-LLM BIE-style observe/measure/revise loop. Samples honest game-thread **frame delta**, not GPU frame times or thermals. Builds 2-second windows with >=15 observations, ignores and counts pauses >200ms, three warmup windows, two sustained slow windows to decrease one tier, six sustained headroom windows to increase one tier, and a three-window cooldown. Bounded tiers Economy/Balanced/Detail. **This policy is not the full user's external BIE THRIVES executable**; no connection to its H116+ memory or general learning has been demonstrated.
2. `UIRLAdaptiveMobileFidelityComponent`, instantiated by the existing `AIRLPlayerController`: on a *local Android player controller only*, watches frame-time windows. It applies Unreal `UGameUserSettings` texture, foliage, shadow, effects, view distance, anti-aliasing and post-processing groups on tier transitions. Editor/desktop/server paths are unchanged. Manual disable via `bAdaptiveQualityEnabled` exposed to Blueprints. Applying scalability groups on live Android hardware still needs verification.
3. `IRL/Config/DefaultDeviceProfiles.ini`: low/mid/high initial quality profiles with 720p-relative mobile content scale factors 0.8, 0.9, 1.0, and conservative texture pool sizes 96/160/256 MB. These are *candidate* budgets, not measured Moto G limits; source profile matching and overrides must be inspected on real device.
4. `AIRLLivingBiomeDetailActor`: native editor-placeable view-only decorator with three `UHierarchicalInstancedStaticMeshComponent` batches (plants, rocks, leaf litter). Uses deterministic seeded placement near actual terrain hits, respects world static collision, restricts placement on slopes, randomizes orientation and scale, switches tier-bounded instance counts, culls distant fragments and disables costly micro-vegetation shadows. Decorative detail NEVER writes to BIE biological or shared physical world state. A player-local visual-quality transition can update placed biome actors without affecting the other player's quality settings.
5. `IRL.Experience` and initial First Signal source are preserved; no new gameplay objective. The biome actor must be placed in a level, and real PBR meshes/materials must be assigned in Unreal before it visibly improves scenery. A component with no assigned mesh renders nothing; do not misrepresent it as photorealistic finished art.

## Evidence: what was tested
Native GCC C++17 on Linux, `-std=c++17 -O2 -Wall -Wextra -Werror -pedantic`, 11/11 host checks **PASS**. Repeated with AddressSanitizer + UBSan: 11/11 **PASS**. Tests cover initial tiers, long-frame/outlier rejection, warmup, slowdown, no downgrade below Economy, promotion after sustained measured headroom, no upgrade above Detail, anti-oscillation, high-refresh target and invalid-target fallback. Exact compiled source Git blob is `772424ee4e238f678f7dc1270cdeace559593d52` and test harness Git blob `f52771522e45fbdbec8875b667003525df6f328e`. Both independently verified from GitHub readback.

Authored Unreal automation source `IRL.Visual.MobileBudgetPolicy` **NOT run**. Unreal Engine 5.8 compile, native visual HISM creation, actual biome art import, 2-phone PIE/network, Android cook/APK, GPU/CPU/thermal measurements, real FPS stability, advanced Android shading mode suitability and original First Signal regression **NOT run**. The fact that algorithm decisions are correct on synthetic deltas is **not** a proof of improved device FPS or fidelity.

## Original/licensed high-quality art pipeline
Use creator-owned scans or license-appropriate scanned assets (e.g. Poly Haven CC0, https://polyhaven.com/license, or Fab under the applicable EULA). **Never copy Star Citizen, GTA or other games' proprietary textures/geometry.** For each PBR material, preserve normal maps, base color (sRGB), roughness/metal/AO (linear), physical scale, provenance and licensing. Start with reusable rock, soil, tree bark and moss; provide quality-switched mobile materials with near-camera height/normal detail and fewer texture reads at medium/far distances.

Caution: importing downloaded PBR/mesh art into binary `.uasset` packages and material editing requires Unreal Editor and target device testing. No external paid/CC0 meshes are currently imported by this code branch. The materials in original IRL main were prototype grids, not production scan-based worlds.

### Mobile render plan, not universal promises
- Android Mobile Forward is broadest compatibility; Mobile Deferred can be superior for outdoor dynamic lighting on supported hardware. Benchmark both in separately cooked Android builds rather than assuming high-end desktop Lumen or Nanite works on a Moto G.
- Prefer normal/roughness/material detail, HDR color discipline, shadow placement and smart foliage instancing over expensive post-process blur/bloom. BIE BLOOM refers to *learning/experience*, not unlimited glow effect.
- Set a **provisional** 30 FPS / 33.3 ms budget on Moto G, quality target in warmed gameplay. Correct hardware-specific limits with device frame-time percentiles, GPU render data, temperature and battery discharge after validation; no results are claimed yet.
- Use Unreal Insights and on-device GPU profiling to distinguish simulation from GPU rendering and memory. Add repeatable screenshots / video comparisons for visual quality.
- Hold graphics improvements to a fair A/B gate: same device, map, camera path, temperature window and duration; accept changes only if visual quality demonstrably improves without sustained regression to FPS, frame-time tails, memory or thermals. Keep unsupported changes behind capability flags.

## Native test reproduction
```bash
g++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
    -I IRL/Source/IRL/Visual IRL/Tests/host_visual_budget_test.cpp -o /tmp/irl-visual-budget
/tmp/irl-visual-budget
```

## Integration gates
1. Compile UE 5.8; run `IRL.Visual.MobileBudgetPolicy` and `IRL.Experience.FirstSignalLifecycle` plus all new tests.
2. Check the current ThirdPerson Blueprint controller really subclasses `AIRLPlayerController`; ensure component ticks on an Android local controller. Review runtime texture group behavior.
3. Place biome actor in the actual original ThirdPerson map; import legitimate PBR assets, assign plant/stone/litter meshes/materials, build, visually inspect spacing/occlusion/material scale.
4. Benchmark low/mid/high device rendering, hardware GPU constraints, movement-heavy ecology, 2-client network, shader warmup, asset streaming and thermal throttling on actual Moto G.
5. Integrate with PRs #1–#5 without overriding their GameMode, Experience or NPC state. Full planet/photorealistic creature art and trillion-individual life cycles remain **not implemented**.

**Conclusion:** BIE-inspired frame-budget code native tested; mobile fidelity and realistic art *integration candidate*, not UE-tested, merged or released.
