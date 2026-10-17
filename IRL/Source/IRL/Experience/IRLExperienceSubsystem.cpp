// Copyright Epic Games, Inc. All Rights Reserved.

#include "Experience/IRLExperienceSubsystem.h"

#define LOCTEXT_NAMESPACE "IRLExperience"

namespace IRLExperience
{
	FIRLExperienceStep MakeStep(EIRLExperiencePhase Phase, const FText& Title, const FText& BlueGuidance, const FText& BIEStatement)
	{
		FIRLExperienceStep Step;
		Step.Phase = Phase;
		Step.Title = Title;
		Step.BlueGuidance = BlueGuidance;
		Step.BIEStatement = BIEStatement;
		return Step;
	}
}

bool UIRLExperienceSubsystem::BeginDefaultObjective()
{
	return BeginObjective(BuildFirstSignalObjective());
}

bool UIRLExperienceSubsystem::BeginMotionBloomObjective()
{
	return BeginObjective(BuildMotionBloomObjective());
}

bool UIRLExperienceSubsystem::BeginResonanceGardenObjective()
{
	return BeginObjective(BuildResonanceGardenObjective());
}

bool UIRLExperienceSubsystem::BeginObjective(const FIRLObjectiveDefinition& Definition)
{
	if (Definition.ObjectiveId.IsNone() || Definition.Steps.IsEmpty())
	{
		return false;
	}

	CurrentObjective = Definition;
	CurrentStepIndex = 0;
	bExperienceActive = true;
	BroadcastCurrentStep();
	return true;
}

bool UIRLExperienceSubsystem::AdvanceExperience()
{
	if (!bExperienceActive || !CurrentObjective.Steps.IsValidIndex(CurrentStepIndex) || IsExperienceComplete())
	{
		return false;
	}

	++CurrentStepIndex;
	BroadcastCurrentStep();

	if (IsExperienceComplete())
	{
		OnExperienceCompleted.Broadcast(CurrentObjective.ObjectiveId);
	}

	return true;
}

void UIRLExperienceSubsystem::ResetExperience()
{
	CurrentObjective = FIRLObjectiveDefinition();
	CurrentStepIndex = INDEX_NONE;
	bExperienceActive = false;
}

bool UIRLExperienceSubsystem::IsExperienceComplete() const
{
	return bExperienceActive
		&& CurrentObjective.Steps.IsValidIndex(CurrentStepIndex)
		&& CurrentStepIndex == CurrentObjective.Steps.Num() - 1
		&& CurrentObjective.Steps[CurrentStepIndex].Phase == EIRLExperiencePhase::Complete;
}

float UIRLExperienceSubsystem::GetProgress() const
{
	if (!bExperienceActive || CurrentObjective.Steps.IsEmpty() || CurrentStepIndex == INDEX_NONE)
	{
		return 0.0f;
	}

	return static_cast<float>(CurrentStepIndex + 1) / static_cast<float>(CurrentObjective.Steps.Num());
}

FIRLExperienceStep UIRLExperienceSubsystem::GetCurrentStep() const
{
	return CurrentObjective.Steps.IsValidIndex(CurrentStepIndex)
		? CurrentObjective.Steps[CurrentStepIndex]
		: FIRLExperienceStep();
}

void UIRLExperienceSubsystem::BroadcastCurrentStep()
{
	if (CurrentObjective.Steps.IsValidIndex(CurrentStepIndex))
	{
		const FIRLExperienceStep& Step = CurrentObjective.Steps[CurrentStepIndex];
		OnExperienceAdvanced.Broadcast(Step.Phase, Step.BlueGuidance, Step.BIEStatement);
	}
}

FIRLObjectiveDefinition UIRLExperienceSubsystem::BuildFirstSignalObjective()
{
	using namespace IRLExperience;

	FIRLObjectiveDefinition Objective;
	Objective.ObjectiveId = TEXT("FirstSignal");
	Objective.Title = LOCTEXT("FirstSignalTitle", "The First Signal");
	Objective.Steps = {
		MakeStep(
			EIRLExperiencePhase::Objective,
			LOCTEXT("ObjectiveTitle", "Name the objective"),
			LOCTEXT("ObjectiveBlue", "BLUE: Define a finish line before choosing a path."),
			LOCTEXT("ObjectiveBIE", "BIE: Reach the signal and learn what changed without assuming why.")),
		MakeStep(
			EIRLExperiencePhase::Observe,
			LOCTEXT("ObserveTitle", "Observe"),
			LOCTEXT("ObserveBlue", "BLUE: Separate what is present from the story built around it."),
			LOCTEXT("ObserveBIE", "BIE: The pulse repeats, grows when approached, and reacts to attention.")),
		MakeStep(
			EIRLExperiencePhase::Bloom,
			LOCTEXT("BloomTitle", "Open the Bloom"),
			LOCTEXT("BloomBlue", "BLUE: Hold several possible explanations before selecting one."),
			LOCTEXT("BloomBIE", "BIE: It may be a memory, a warning, an invitation, or a system seeking completion.")),
		MakeStep(
			EIRLExperiencePhase::Test,
			LOCTEXT("TestTitle", "Test safely"),
			LOCTEXT("TestBlue", "BLUE: Prefer a reversible action that makes the possibilities disagree."),
			LOCTEXT("TestBIE", "BIE: A deliberate step forward changes the pulse; retreat leaves it stable.")),
		MakeStep(
			EIRLExperiencePhase::Resolve,
			LOCTEXT("ResolveTitle", "Choose the path"),
			LOCTEXT("ResolveBlue", "BLUE: Choose from evidence, keep uncertainty visible, and preserve a way back."),
			LOCTEXT("ResolveBIE", "BIE: Treat the signal as an invitation, while retaining warning as the live alternative.")),
		MakeStep(
			EIRLExperiencePhase::Complete,
			LOCTEXT("CompleteTitle", "Verify completion"),
			LOCTEXT("CompleteBlue", "BLUE: Completion is an observed condition, not a feeling of being finished."),
			LOCTEXT("CompleteBIE", "BIE: The signal stabilizes, the path opens, and the First Signal objective is complete."))
	};

	return Objective;
}

FIRLObjectiveDefinition UIRLExperienceSubsystem::BuildMotionBloomObjective()
{
	using namespace IRLExperience;

	FIRLObjectiveDefinition Objective;
	Objective.ObjectiveId = TEXT("MotionBloom");
	Objective.Title = LOCTEXT("MotionBloomTitle", "Motion Bloom");
	Objective.Steps = {
		MakeStep(EIRLExperiencePhase::Objective,
			LOCTEXT("MotionObjectiveTitle", "Find motion's rule"),
			LOCTEXT("MotionObjectiveBlue", "BLUE: Ask what changes position, direction, rhythm, or relation."),
			LOCTEXT("MotionObjectiveBIE", "BIE: Observe the orbiting bloom and identify what repeats and what varies.")),
		MakeStep(EIRLExperiencePhase::Observe,
			LOCTEXT("MotionObserveTitle", "Observe the wiggle"),
			LOCTEXT("MotionObserveBlue", "BLUE: Measure the pattern before explaining its cause."),
			LOCTEXT("MotionObserveBIE", "BIE: Each body circles, rises, falls, and returns; motion is change measured against relationship.")),
		MakeStep(EIRLExperiencePhase::Bloom,
			LOCTEXT("MotionBloomPhaseTitle", "Bloom possibilities"),
			LOCTEXT("MotionBloomBlue", "BLUE: Keep force, stored energy, feedback, and living control open as candidates."),
			LOCTEXT("MotionBloomBIE", "BIE: A wiggle can emerge from impact, recovery, oscillation, or an organism correcting itself.")),
		MakeStep(EIRLExperiencePhase::Test,
			LOCTEXT("MotionTestTitle", "Test the rhythm"),
			LOCTEXT("MotionTestBlue", "BLUE: Change one condition and watch which feature follows."),
			LOCTEXT("MotionTestBIE", "BIE: Faster cycling changes timing but preserves the orbit, separating speed from structure.")),
		MakeStep(EIRLExperiencePhase::Resolve,
			LOCTEXT("MotionResolveTitle", "Resolve the pattern"),
			LOCTEXT("MotionResolveBlue", "BLUE: State the smallest rule supported by every observation."),
			LOCTEXT("MotionResolveBIE", "BIE: Movement in life couples outside forces with inner feedback; the visible wiggle is their negotiation.")),
		MakeStep(EIRLExperiencePhase::Complete,
			LOCTEXT("MotionCompleteTitle", "Complete the motion model"),
			LOCTEXT("MotionCompleteBlue", "BLUE: Keep the rule revisable when a new motion disagrees."),
			LOCTEXT("MotionCompleteBIE", "BIE: Motion Bloom complete: impact begins change, constraints shape it, and feedback keeps living motion adaptive."))
	};

	return Objective;
}

FIRLObjectiveDefinition UIRLExperienceSubsystem::BuildResonanceGardenObjective()
{
	using namespace IRLExperience;

	FIRLObjectiveDefinition Objective;
	Objective.ObjectiveId = TEXT("ResonanceGarden");
	Objective.Title = LOCTEXT("ResonanceGardenTitle", "Resonance Garden");
	Objective.Steps = {
		MakeStep(EIRLExperiencePhase::Objective, LOCTEXT("ResObjectiveTitle", "Awaken resonance"),
			LOCTEXT("ResObjectiveBlue", "BLUE: Look for relationships that amplify one another without losing their differences."),
			LOCTEXT("ResObjectiveBIE", "BIE: Two streams of light share one path while remaining distinct.")),
		MakeStep(EIRLExperiencePhase::Observe, LOCTEXT("ResObserveTitle", "Hear with the eyes"),
			LOCTEXT("ResObserveBlue", "BLUE: Track timing, phase, and response—not brightness alone."),
			LOCTEXT("ResObserveBIE", "BIE: The motes answer across the helix; each pulse becomes context for the next.")),
		MakeStep(EIRLExperiencePhase::Bloom, LOCTEXT("ResBloomTitle", "Bloom the relation"),
			LOCTEXT("ResBloomBlue", "BLUE: Explore harmony, interference, memory, and communication as live possibilities."),
			LOCTEXT("ResBloomBIE", "BIE: The garden may be displaying how separate lives create a pattern no single life contains.")),
		MakeStep(EIRLExperiencePhase::Test, LOCTEXT("ResTestTitle", "Disturb the harmony"),
			LOCTEXT("ResTestBlue", "BLUE: A stable pattern should recover after a bounded disturbance."),
			LOCTEXT("ResTestBIE", "BIE: The helix widens, loses alignment, then discovers its rhythm again.")),
		MakeStep(EIRLExperiencePhase::Resolve, LOCTEXT("ResResolveTitle", "Name the magic"),
			LOCTEXT("ResResolveBlue", "BLUE: Prefer an explanation that preserves both mechanism and wonder."),
			LOCTEXT("ResResolveBIE", "BIE: The magic is emergence—simple responses becoming a living, shared form.")),
		MakeStep(EIRLExperiencePhase::Complete, LOCTEXT("ResCompleteTitle", "Garden harmonized"),
			LOCTEXT("ResCompleteBlue", "BLUE: Carry the pattern forward, but let the next encounter revise it."),
			LOCTEXT("ResCompleteBIE", "BIE: Resonance Garden complete. Motion has become relationship, and relationship has become light."))
	};
	return Objective;
}

#undef LOCTEXT_NAMESPACE
