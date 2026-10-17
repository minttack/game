// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "IRLGameMode.generated.h"

/**
 *  Simple GameMode for a third person game
 */
UCLASS(abstract)
class AIRLGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	
	/** Constructor */
	AIRLGameMode();

protected:
	virtual void BeginPlay() override;

	/** Spawns the first evidence-led objective near the level's PlayerStart. */
	UPROPERTY(EditDefaultsOnly, Category = "IRL|Experience")
	bool bSpawnFirstSignal = true;

	UPROPERTY(EditDefaultsOnly, Category = "IRL|Experience")
	TSubclassOf<class AIRLExperienceBeacon> ExperienceBeaconClass;
};



