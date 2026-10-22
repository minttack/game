# IRL_MASTER_STATE — candidate shared state (2026-10-22)

**One authoritative game**: `https://github.com/minttack/game`, Unreal Engine 5.8 project `IRL/IRL.uproject`. Verified main SHA `261cbbbb8264dfde6943cd0fa304029d4867dd3e` (2026-10-22 audit). This document is in a draft branch and does **not** replace main until reviewed/merged.

**Main-branch implementation**: third-person UE template plus IRL-specific First Signal, Motion Bloom and Resonance Garden objectives, six guided Experience phases with Blue/BIE fixed strings and an in-engine lifecycle automation test. Main's default map is `ThirdPerson/Lvl_ThirdPerson`; default Blueprint GameMode parent linkage to `AIRLGameMode` needs verified editor inspection. No verified public GitHub Release APK; source directory alone is not evidence of Android build.

**Parallel unmerged draft workers**:
- PR #1 `workers/irl-mobile-duo-foundation-20261021`: 2-human admission/spawn and preliminary Android config, not UE-verified.
- PR #2 `workers/irl-life-evolution-lab-20261022`: non-LLM native learner and generational prior, host-tested only.
- PR #3 `workers/irl-ecology-grounded-20261022`: bounded ecology and Unreal habitat actor, UE test outstanding, stacked on #2.
- PR #4 `workers/irl-duo-ecology-replication-20261022`: candidate source for replication of bounded visual frames, stacked on #3, Android/network verification pending.
- This candidate `workers/irl-experience-evidence-gate-20261022`: extends **main** Experience subsystem with source-reported outcome ledger and opt-in Test gate. Native evidence tests passed; UE build pending.

**Remaining blockers**: compile UE 5.8 and run all original/new Unreal tests; verify default Blueprint GameMode; real NPC perception/action outcome bindings; authenticated server-world evidence provenance; persistent per-entity learning history; validated physics/planet visual fidelity; actual Android build; two phone network synchronization, persistence and profiling. Do not call IRL finished, photorealistic, generally intelligent, or trillion-agent simulated.

**Next merge discipline**: Refresh main, resolve the two independent feature chains, test combined code in Unreal, verify preserved earlier controls before merge. No branch was merged by this record.
