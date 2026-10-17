// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Experience/IRLExperienceTypes.h"
#include "GameFramework/Actor.h"
#include "IRLExperienceBeacon.generated.h"

class UPointLightComponent;
class USphereComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

/** A visible, self-contained entry point into the First Signal experience. */
UCLASS()
class IRL_API AIRLExperienceBeacon : public AActor
{
	GENERATED_BODY()

public:
	AIRLExperienceBeacon();
	virtual void Tick(float DeltaSeconds) override;

protected:
	virtual void BeginPlay() override;

	UFUNCTION()
	void HandleBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComponent, int32 OtherBodyIndex, bool bFromSweep,
		const FHitResult& SweepResult);

	void AdvanceExperience();

	UFUNCTION()
	void HandleExperienceAdvanced(EIRLExperiencePhase Phase, const FText& BlueGuidance, const FText& BIEStatement);

	UFUNCTION()
	void HandleExperienceCompleted(FName ObjectiveId);

private:
	UPROPERTY(VisibleAnywhere, Category = "IRL|Experience")
	TObjectPtr<USphereComponent> TriggerSphere;

	UPROPERTY(VisibleAnywhere, Category = "IRL|Experience")
	TObjectPtr<UStaticMeshComponent> SignalMesh;

	UPROPERTY(VisibleAnywhere, Category = "IRL|Experience")
	TObjectPtr<UPointLightComponent> SignalLight;

	UPROPERTY(VisibleAnywhere, Category = "IRL|Experience")
	TObjectPtr<UTextRenderComponent> InstructionText;

	UPROPERTY(VisibleAnywhere, Category = "IRL|Experience")
	TArray<TObjectPtr<UStaticMeshComponent>> MotionPetals;

	UPROPERTY(VisibleAnywhere, Category = "IRL|Experience")
	TArray<TObjectPtr<UStaticMeshComponent>> MagicMotes;

	UPROPERTY(VisibleAnywhere, Category = "IRL|Experience")
	TArray<TObjectPtr<UPointLightComponent>> MagicLights;

	UPROPERTY(EditAnywhere, Category = "IRL|Experience", meta = (ClampMin = "0.1"))
	float PulseSpeed = 1.35f;

	UPROPERTY(EditAnywhere, Category = "IRL|Experience", meta = (ClampMin = "0.0"))
	float PulseAmplitude = 0.12f;

	float RunningTime = 0.0f;
	bool bObjectiveStarted = false;
	bool bMotionBloomReady = false;
	bool bMotionBloomActive = false;
	bool bResonanceReady = false;
	bool bResonanceActive = false;
	EIRLExperiencePhase CurrentPhase = EIRLExperiencePhase::Objective;
};
