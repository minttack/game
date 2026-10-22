// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Experience/IRLExperienceTypes.h"
#include "Experience/IRLExperienceEvidenceCore.h"
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
	bool BeginMotionBloomObjective();

	UFUNCTION(BlueprintCallable, Category = "IRL|Experience")
	bool BeginResonanceGardenObjective();

	UFUNCTION(BlueprintCallable, Category = "IRL|Experience")
	bool BeginObjective(const FIRLObjectiveDefinition& Definition);

	UFUNCTION(BlueprintCallable, Category = "IRL|Experience")
	bool AdvanceExperience();

	/** Lock in a testable prediction BEFORE a result is available.
	 * SourceTag identifies who is reporting, not proof the report is correct.
	 */
	UFUNCTION(BlueprintCallable, Category = "IRL|Experience|Evidence")
	bool StartEvidencePrediction(FName SourceTag, float PredictedValue, int32& OutTrialId);

	/** Record an actual result as reported by a game-world event. Do not use
	 * this with invented values or pre-written narration.
	 */
	UFUNCTION(BlueprintCallable, Category = "IRL|Experience|Evidence")
	bool ReportEvidenceOutcome(FName SourceTag, int32 TrialId, float ObservedValue);

	UFUNCTION(BlueprintPure, Category = "IRL|Experience|Evidence")
	int32 GetSourceReportedOutcomeCount() const;

	UFUNCTION(BlueprintPure, Category = "IRL|Experience|Evidence")
	float GetReportedPredictionMSE() const;

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
	static FIRLObjectiveDefinition BuildMotionBloomObjective();
	static FIRLObjectiveDefinition BuildResonanceGardenObjective();

private:
	void BroadcastCurrentStep();

	UPROPERTY(Transient)
	FIRLObjectiveDefinition CurrentObjective;

	UPROPERTY(Transient)
	int32 CurrentStepIndex = INDEX_NONE;

	UPROPERTY(Transient)
	bool bExperienceActive = false;

	// Temporary in-memory reported trial log. A persistent, server-authoritative
	// evidence journal and validated world-event listeners are future work.
	IRLEvidence::Ledger EvidenceLedger;
};
