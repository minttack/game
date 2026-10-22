# IRL_DEVELOPMENT_LOG — verified candidate session 2026-10-22

**Base**: GitHub `minttack/game` main `261cbbbb8264dfde6943cd0fa304029d4867dd3e`.

**Inspected**: Existing `IRLExperienceSubsystem.cpp/.h`, `IRLExperienceTypes.h`, `IRLExperienceBeacon.cpp/.h`, original automation, `DefaultEngine.ini`, repo release status, and draft PRs #1–#4.

**Finding**: all 3 playable research-inspired sequences advance via manual keypress. Fixed text narrates observations/tests with no prediction/outcome receipt or independent learned model. The staged BIE learning/duo experiments from PR #1–#4 are not in main.

**Implemented in isolated candidate branch**:
- A portable C++17 BIE evidence ledger: predictions before outcomes, matched source tags, single-use receipts, finite [-1,1] normalized values, MSE, 1,024 recorded-outcome cap and reset without reusable IDs.
- Actual `UIRLExperienceSubsystem` APIs to submit predicted and source-reported observed outcomes. New `FIRLObjectiveDefinition::bRequireSourceReportedOutcomeAtTest` blocks transition from Test to Resolve unless a reported trial is recorded. Existing tutorials default to false, preserving prior controls.
- Unreal automation code for both the old tutorial progression and new opt-in research gate, plus native host regression harness.
- Audit, master state, decision excerpt and roadmap records added on the **feature branch**, not merged into main.

**Verification**: exact local C++17 core compiled with GCC 14.2 `-std=c++17 -O2 -Wall -Wextra -Werror -pedantic`; native host harness PASS and repeat PASS with `-fsanitize=address,undefined`. Git blob SHA-1 for the tested header is `910c6b1039de70dcf0e49828bd38e6f5a2c2d507` (confirmed readback). UE 5.8 build, new and inherited editor automation, mobile packaging and 2-device tests **NOT RUN**.

**Critical limitations**: an API caller can report invented outcomes. Source tags are not trusted world-event witnesses, and the ledger is only runtime memory; no persistent autonomous learner is established by this branch. The added gate is optional and does not itself improve creature decisions.
