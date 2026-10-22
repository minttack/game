# IRL — Grounded Ecology & Experience Laboratory (worker candidate)

**2026-10-22** · Existing authoritative game: \`minttack/game\`, Unreal Engine 5.8. Parent for this stacked work: BIE learning draft PR #2 at \`b2ecd52361cf7f0ee6c22f3f217d7f6c5df44bd4\`. Separate human-duo/mobile branch: draft PR #1. **No existing main-branch game files were overwritten.**

## Implemented in the branch

1. \`IRL/Source/IRL/Experience/IRLEcologyCore.h\`: deterministic, non-LLM, C++17 life-and-environment simulator using the existing BIE Experience learner. The world contains finite food, actual consumption, timed regrowth, shelter locations, danger, movement constrained by grid edges, energy metabolism, deaths and eligible offspring inheriting provisional behaviors. **Creature movement now searches only observable locations within two tiles**, not through an omniscient global map. BIE predictions are locked before each observed physical update. A step receipt reports coordinates, food counts, energy changes, observed reward, survival and learning cycles. No event without an outcome counts as lived experience.
2. \`AIRLEcologyHabitatActor\`: editor-placeable in the **existing** IRL game. Creates a small deterministic habitat on the authoritative server and visualizes a bounded number of creatures and finite food instances using Unreal's built-in static sphere mesh, in centimeter-scaled spatial positions. It takes one observation/action/outcome step per second and can create limited descendants by deducting parent energy. Its habitat world state is currently transient and is NOT replicated to the second player's phone.
3. Host test and benchmark C++17 files plus \`IRL.Experience.GroundedEcology\` Unreal automation test source.
4. Runtime limits: world side length at most 32 for the editor actor and 40 active in-habitat creatures; the standalone core defaults to max 1,000 active. Population *representation* of a trillion from PR #2 is explicitly separate from individual cycles. No trillion bots have been run or given imaginary experiences.

## Verification: what was actually exercised

The exact committed \`IRLEcologyCore.h\` was verified by matching its Git blob ID to the tested local file: \`d9a7986ad3e2e8f1b1f68aebd5bc096d847bd492\`.

Native Linux g++ 14.2 C++17:
- 10/10 host ecology checks PASS at \`-O2 -Wall -Wextra -Werror -pedantic\` for actual depletion, no phantom food, shelter protection, lethal hazard, descendant inheritance, no life after death, bounded population, world validity and timed regrowth.
- 10/10 tests PASS again under AddressSanitizer + UBSan. A stale-pointer read in the host **test harness** after vector growth was detected by ASan and corrected before the final PASS. Production core had no matching read in this test.
- Controlled 250-step scenarios, local physics + feedback (NOT real ecological science):
  - Safe replenishing food: BIE survived 250 steps; always-forage survived 250; always-shelter 24; seeded random 83.
  - Dangerous replenishing food: BIE survived 11; always-forage 6; always-shelter 24; seeded random 10. **BIE loses to always-shelter on survival here.**
  - Food regrows every third step: BIE 250, always-forage 250, always-shelter 24, seeded random 71.
  These results are *not* statistically robust: one map/seed each. No proven superiority over standard contextual-bandit/RL baselines, nor biological realism, yet.
- Unreal 5.8 compile, original First Signal tests, new in-engine \`IRL.Experience.GroundedEcology\`, Android profiling, network synchronization, persistent saves, advanced biology and photorealism: **NOT RUN.**

## Reproduce standalone tests after checkout

From repo root on a C++17 host:
\`\`\`sh
g++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  -I IRL/Source/IRL IRL/Tests/host_ecology_test.cpp -o /tmp/irl-ecology-test
/tmp/irl-ecology-test
g++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  -I IRL/Source/IRL IRL/Tests/host_ecology_benchmark.cpp -o /tmp/irl-ecology-benchmark
/tmp/irl-ecology-benchmark
\`\`\`

## Unreal integration steps and gates

- Compile module against Unreal Engine 5.8 on a development machine. \`AIRLEcologyHabitatActor\` is added as a new actor class; drag it into \`ThirdPerson/Lvl_ThirdPerson\` or an IRL biome world and place it above terrain. When placed, it renders moving proxy spheres for creatures and food and advances the small simulation on the server.
- Run \`IRL.Experience.GroundedEcology\` plus inherited FirstSignal tests from Unreal Automation. Fix any Unreal compiler/packaging errors before merging. Verify collision/navmesh and actual survival interaction.
- Prototype server-authoritative world replication, versioned persistence of each individual's **actual** Experience receipts, deterministic replay, undo/correction and negative transfer gates. Current actor displays proxies, not real UE AICharacter navigation, physics animals or replicated creature views.
- Connect the visible habitats to **same** planet as duo/mobile PR #1 after that branch is tested; then test both Android devices seeing identical instances, with per-device FPS/thermal measurements.
- Compare BIE against stronger heuristic and standard reinforcement-learning baselines across many unseen seeds, report confidence intervals, and only promote changes showing measurable generalization.
- Scale *honestly*: near-player embodied individuals; distant simulated cohorts; distinguish represented population, actually updated agents, and receipt-verified learning cycles.

**Status**: standalone native ecology **implemented and tested**; Unreal visual adapter **source implemented, not engine-verified**; duo/mobile ecosystem **not integrated, not released**.
