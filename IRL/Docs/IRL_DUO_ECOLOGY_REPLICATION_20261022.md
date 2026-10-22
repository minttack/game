# IRL — Duo Ecology Visual Replication (candidate, 2026-10-22)

## Continuity
Same authoritative Unreal Engine 5.8 game: \`minttack/game/IRL\`. Parent branch is the unmerged grounded-ecology PR #3 at commit \`68c275bfd66e1cbe2171ed55865f882ef8a99941\`. Duo human spawning is separate unmerged PR #1; native BIE life learning is PR #2. This branch must be integrated after verifying those dependencies, not used as a replacement game.

## Actual change
The ecology habitat actor previously set \`bReplicates = false\`. The simulation ran only on the authority and clients had no state to render. In this candidate:
- Only the server executes each BIE cycle and physical ecology step.
- A **single RepNotify frame** advertises the same tick sequence, habitat dimensions, centimeter cell spacing, finite-food cells, surviving creature cells with stable IDs, actual food consumed, and witnessed Experience-cycle count to both clients.
- Client OnRep validates cell bounds, maximum counts, nonzero IDs, duplicate food/IDs, finite cell size, estimated payload budget, and strictly increasing sequence before rebuilding local instanced visuals. Clients never invent food, agent learning outcomes or local AI updates.
- The actor is globally relevant for **one small pilot habitat**, not a scalable setting for trillions of planetary inhabitants. It replicates snapshots at the simulation's 1Hz cadence with an actor update rate of 2Hz to permit network scheduling. Estimated maximum content is 2,544 bytes per snapshot **before Unreal headers, protocol overhead and retransmissions**.
- Actor getter methods now return the replicated frame's observed metrics, so both clients can inspect the same server-derived counts. Dedicated servers skip mesh refresh.
- No new language model dependency. Learning remains the independent non-LLM BIE-style engine.

## Evidence and scope
\`IRL/Tests/host_habitat_snapshot_test.cpp\`: **10/10** native C++17 policy groups passed locally on GCC 14.2 under \`-O2 -Wall -Wextra -Werror -pedantic\`; same **10/10** passed with AddressSanitizer and UBSan. Tests include 32×32 maximum cells, 40 stable creature IDs, mixed duplicates/malformed cells, bad dimensions/sizes, late and duplicate sequences, and payload estimate. The corrected uploaded native header has Git blob SHA-1 `26b8951d255bd8fe4b0cad538f69e6474693a680`, matching the exact locally compiled header (not merely a similar implementation). These are **codec tests only**.

Unreal Engine 5.8 compilation, new `IRL.Experience.HabitatSnapshotCodec` engine test, property serialization, actual network packet measurements, Listen Server + 2 clients, late joining, physics/visual behavior, frame-rate, Moto G devices and Android APK packaging remain **NOT TESTED** in this environment. The underlying proxy actor must still be placed in the level; no binary \`.umap\` edit was made.

## Next integration gates
1. Compile UE 5.8, run original \`IRL.Experience.FirstSignalLifecycle\`, \`IRL.Experience.GroundedEcology\`, and all new native snapshot tests. Correct any UnrealHeaderTool constraints.
2. Place \`AIRLEcologyHabitatActor\` into the original IRL shared-world level; PIE/Listen Server + 2 clients. Both must see the exact same stable IDs, surviving creature cells, depleted food, and verified-cycle counts. Join after simulation has already advanced to verify initial state replication.
3. Confirm the human-duo GameMode from PR #1 is active and the two humans start separately, same server and same planet.
4. Profile actual replicated wire bytes, jitter, CPU, memory and thermal draw on two Android devices; optimize relevancy and interest management instead of \`bAlwaysRelevant\` before increasing population.
5. Add durable server-world save/reload and per-creature experience ledger receipts. Current snapshot updates are not persistent history.
6. Do not merge while 2-client and Unreal test gates are missing.

**Disposition:** source implementation staged for review; native snapshot codec verified; engine/network integration not yet verified.
