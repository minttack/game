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

#undef LOCTEXT_NAMESPACE
