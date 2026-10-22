# IRL Experience — source-level evidence audit and candidate improvement

## Main branch, not screenshots

Live GitHub source (2026-10-22): https://github.com/minttack/game/tree/main/IRL/Source/IRL/Experience

Runtime scripted `UIRLExperienceSubsystem` runs three authored objectives: First Signal → Motion Bloom → Resonance Garden. Their six phases are `Objective, Observe, Bloom, Test, Resolve, Complete`. `AdvanceExperience()` on current main increments `CurrentStepIndex`, broadcasts prewritten explanatory `BIEStatement`, and calls a completion delegate. That is a legitimate guided playable experience; the named BIE narration is not an independently run, measurable self-learning engine. The default UE map and Blueprint parent need in-editor validation; source does not verify an APK, physical-device output or photorealism.

## Candidate improvement, intentionally opt-in

Pure portable header `IRLExperienceEvidenceCore.h` enforces `Predict -> ReportOutcome`: a finite normalized scalar prediction is registered before the outcome; a one-time token and matching non-empty tagged source are required; duplicate, malformed, stale and mismatched reports are rejected. The outcome stores predicted and reported values and squared prediction error. The ledger is capped at 1,024 results/objective.

`UIRLExperienceSubsystem` exposes `StartEvidencePrediction(SourceTag, PredictedValue, OutTrialId)`, `ReportEvidenceOutcome(SourceTag, TrialId, ObservedValue)`, `GetSourceReportedOutcomeCount()` and `GetReportedPredictionMSE()` for game systems and Blueprints. On new research objectives, `bRequireSourceReportedOutcomeAtTest=true` blocks the Test -> Resolve transition until an outcome has been source-reported. Existing First Signal, Motion Bloom and Resonance Garden are ungated by default to preserve play.

**No epistemic overclaim**: the source tag is a label and the submitted data may still be false or fabricated. A recorded report is not external verification of the event or demonstration of improving real-world intelligence. Authenticity requires a game-server-owned event subscription and event data produced by physical gameplay; independence requires benchmarks with held-out environments and stronger controls. This branch neither simulates trillions of learning agents nor persists records after restart.

## Measured validation and gates

- Standalone host C++17 harness passes malformed-values, no-outcome/no-learning, one pending prediction, wrong source/token, duplicate feedback, MSE, stale ID after reset, and 1,024-record cap. Repeated with AddressSanitizer + UndefinedBehaviorSanitizer.
- Tested header Git blob `910c6b1039de70dcf0e49828bd38e6f5a2c2d507`.
- Unreal automation code `IRL.Experience.SourceReportedEvidenceGate` authored to verify guided tutorials still complete and opt-in evidence research is gated. **Not executed in Unreal**.
- Must compile full Unreal 5.8 project and run both new and inherited tests before merging; separately integrate trusted world events, persistence, two-phone testing and biology learning.

**Integration status**: draft branch only; no main merge, Unreal engine build, Android build or release.
