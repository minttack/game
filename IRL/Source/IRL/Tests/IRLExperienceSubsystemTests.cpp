// Copyright Epic Games, Inc. All Rights Reserved.

#if WITH_DEV_AUTOMATION_TESTS

#include "Experience/IRLExperienceSubsystem.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FIRLExperienceLifecycleTest,
	"IRL.Experience.FirstSignalLifecycle",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FIRLExperienceLifecycleTest::RunTest(const FString& Parameters)
{
	UIRLExperienceSubsystem* Experience = NewObject<UIRLExperienceSubsystem>();
	TestNotNull(TEXT("Experience subsystem can be constructed"), Experience);
	if (!Experience)
	{
		return false;
	}

	TestFalse(TEXT("Experience begins inactive"), Experience->IsExperienceActive());
	TestTrue(TEXT("First Signal begins"), Experience->BeginDefaultObjective());
	TestEqual(TEXT("Objective id is stable"), Experience->GetCurrentObjectiveId(), FName(TEXT("FirstSignal")));
	TestEqual(TEXT("First phase is Objective"), Experience->GetCurrentStep().Phase, EIRLExperiencePhase::Objective);

	for (int32 Step = 0; Step < 5; ++Step)
	{
		TestTrue(FString::Printf(TEXT("Advance step %d"), Step + 1), Experience->AdvanceExperience());
	}

	TestTrue(TEXT("Final phase completes the experience"), Experience->IsExperienceComplete());
	TestEqual(TEXT("Final phase is Complete"), Experience->GetCurrentStep().Phase, EIRLExperiencePhase::Complete);
	TestEqual(TEXT("Completed progress is one"), Experience->GetProgress(), 1.0f);
	TestFalse(TEXT("Cannot advance beyond completion"), Experience->AdvanceExperience());

	Experience->ResetExperience();
	TestFalse(TEXT("Reset makes the experience inactive"), Experience->IsExperienceActive());
	TestEqual(TEXT("Reset progress is zero"), Experience->GetProgress(), 0.0f);
	return true;
}

#endif
