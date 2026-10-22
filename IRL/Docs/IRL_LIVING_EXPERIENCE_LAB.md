# IRL Living Experience Lab (non-LLM additive implementation candidate)

**Project:** Same authoritative `minttack/game/IRL` Unreal Engine 5.8 source, not a new final game. **Integration gate:** draft PR only until compiled and exercised in Unreal and on Android.

## Vision and truthful engineering boundaries

IRL is a **single shared, physically scaled 3D universe**: two human players spawn in different regions of one planet (duo branch PR #1), encounter autonomous life, watch ecological adaptations and civilizations, and eventually fly between worlds or observe through optional god mode. Player choices and collective behavior may influence, but must not extinguish, individual NPC autonomy (decision 026).

Trillions of virtual inhabitants are an **aspirational population scale**, NOT trillions of active per-agent thinking loops on a phone. A 64-bit exact population ledger can represent 1,000,000,000,000 inhabitants. On-device only a bounded active set can perform individual BIE cycles; remote or offscreen populations are aggregated cohorts with approximate behaviors, and are clearly marked as such. Their distinct personal lived experiences must never be fabricated. Server-side/distributed simulation and out-of-view deterministic catch-up require later implementation.

## Implemented learning kernel

`IRLLifeLearningCore.h` contains a pure C++17 non-LLM contextual learner. There are currently 4 observable contexts (food yes/no, threat yes/no) and 3 possible actions (forage, shelter, explore). Call `Propose` to **commit a predicted normalized reward** before execution; call `RecordObservedOutcome` only after a game event confirms the action's outcome. No feedback = no learning; duplicate, out-of-range, non-finite and mismatched receipts are rejected. Feedback updates a recency-sensitive estimate. Confidence-guided action sampling explores alternatives even after it finds a good behavior. Death stops new actions. `SpawnNextGeneration` passes a discounted **policy prior**, never fictitious observed experiences.

`UIRLLifeExperienceComponent` is a Blueprint-spawnable bridge for server-authoritative non-player characters. It exposes sensing/action/outcome/generational APIs and has **no per-frame tick**. A creature gameplay actor must attach the component, provide real sensory data, physically perform the chosen behavior and report verified feedback. The component alone does not automatically create living AI, nor does it save across server restarts.

**Crucial experimental distinction:** local reward adaptation is algorithmic self-learning within a fixed choice space. It is **not** open-ended general intelligence, true biological evolution, consciousness or a proven improvement over strong reinforcement-learning baselines.

## Reality-like three-dimensional scale

`IRLWorldScale.h` fixes one Unreal world unit to 1 cm, human reference height 1.75 m, and 10 km position sectors for representing physically large worlds using sector + local double-precision coordinates. 3 space axes plus time are modelled. A 6,371-km Earth reference radius is included **only as a physical-scale reference**, not a generated planet. Near-camera rebasing, real orbital dynamics, climate, optical camera exposure, photometric lighting, acoustics, gravity and GPU 3D landscapes are *not yet implemented*. Avoid floating-point precision claims until integrated positions have been tested in engine.

For lifelike appearance on mobile, use physically plausible proportions, PBR materials, sky/sun lighting, correct character/world scale, level-of-detail, culling and device-specific quality profiles. Unreal's high-end desktop effects cannot be assumed to run on low-end Android; assess real on-device visual comparisons against references and performance tests.

## Validation and further integration

- Build `IRL/Tests/host_life_learning_test.cpp` with a C++17 compiler for fast deterministic tests of reward adaptation, change recovery, invalid feedback, generational priors, population counts and sector dimensions.
- In Unreal Engine 5.8, compile the entire game and run `IRL.Experience.LifeLearningEvidence` plus inherited FirstSignalLifecycle tests.
- Attach `UIRLLifeExperienceComponent` to real NPCs. Define real-world food, danger and survival events and test whether BIE-driven agents survive better than non-learning controls under identical seeds and independent holdouts.
- Add persistent Experience memory with journal provenance, prediction timestamps, negative-transfer detection, and promotion gated by actual control comparisons. Local component memory currently lives only as long as the game actor.
- Add multi-resolution simulation with explicit fidelity metadata and CPU/thermal budgets; do **not** count aggregated cohorts as per-individual completed learning cycles.
- Construct real-scale planet terrain, camera, atmospheric lighting, physics and assets before calling the result photorealistic.
- Merge with duo networking branch through current main after review; these new files are deliberately conflict-free with PR #1.

## Source references

- https://dev.epicgames.com/documentation/en-us/unreal-engine/units-of-measurement-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/performance-guidelines-for-mobile-devices-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/android-quick-start
