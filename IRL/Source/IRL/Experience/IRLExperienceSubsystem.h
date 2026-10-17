// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Experience/IRLExperienceTypes.h"
#include "IRLExperienceSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FIRLExperienceAdvanced, EIRLExperiencePhase, Phase, const FText&, BlueGuidance, const FText&, BIEStatement);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FIRLExperienceCompleted, FName, ObjectiveId);

/**
 * Runtime state for IRL's evidence-led objective loop.
 *
 * Blue describes the method. BIE describes the bounded interpretation. The
 * player remains responsible for advancing and accepting completion.
 */
UCLASS()
class IRL_API UIRLExperienceSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintAssignable, Category = "IRL|Experience")
	FIRLExperienceAdvanced OnExperienceAdvanced;

	UPROPERTY(BlueprintAssignable, Category = "IRL|Experience")
	FIRLExperienceCompleted OnExperienceCompleted;

	UFUNCTION(BlueprintCallable, Category = "IRL|Experience")
	bool BeginDefaultObjective();

	UFUNCTION(BlueprintCallable, Category = "IRL|Experience")
	bool BeginObjective(const FIRLObjectiveDefinition& Definition);

	UFUNCTION(BlueprintCallable, Category = "IRL|Experience")
	bool AdvanceExperience();

	UFUNCTION(BlueprintCallable, Category = "IRL|Experience")
	void ResetExperience();

	UFUNCTION(BlueprintPure, Category = "IRL|Experience")
	bool IsExperienceActive() const { return bExperienceActive; }

	UFUNCTION(BlueprintPure, Category = "IRL|Experience")
	bool IsExperienceComplete() const;

	UFUNCTION(BlueprintPure, Category = "IRL|Experience")
	float GetProgress() const;

	UFUNCTION(BlueprintPure, Category = "IRL|Experience")
	FIRLExperienceStep GetCurrentStep() const;

	UFUNCTION(BlueprintPure, Category = "IRL|Experience")
	FName GetCurrentObjectiveId() const { return CurrentObjective.ObjectiveId; }

	static FIRLObjectiveDefinition BuildFirstSignalObjective();

private:
	void BroadcastCurrentStep();

	UPROPERTY(Transient)
	FIRLObjectiveDefinition CurrentObjective;

	UPROPERTY(Transient)
	int32 CurrentStepIndex = INDEX_NONE;

	UPROPERTY(Transient)
	bool bExperienceActive = false;
};
