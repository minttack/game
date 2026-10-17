// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "IRLExperienceTypes.generated.h"

UENUM(BlueprintType)
enum class EIRLExperiencePhase : uint8
{
	Objective UMETA(DisplayName = "Objective"),
	Observe UMETA(DisplayName = "Observe"),
	Bloom UMETA(DisplayName = "Bloom"),
	Test UMETA(DisplayName = "Test"),
	Resolve UMETA(DisplayName = "Resolve"),
	Complete UMETA(DisplayName = "Complete")
};

USTRUCT(BlueprintType)
struct FIRLExperienceStep
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IRL|Experience")
	EIRLExperiencePhase Phase = EIRLExperiencePhase::Objective;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IRL|Experience")
	FText Title;

	/** Blue provides method only: what kind of thinking or evidence belongs here. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IRL|Experience", meta = (MultiLine = true))
	FText BlueGuidance;

	/** BIE reports the current, bounded interpretation without inventing certainty. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IRL|Experience", meta = (MultiLine = true))
	FText BIEStatement;
};

USTRUCT(BlueprintType)
struct FIRLObjectiveDefinition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IRL|Experience")
	FName ObjectiveId = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IRL|Experience")
	FText Title;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IRL|Experience")
	TArray<FIRLExperienceStep> Steps;
};
