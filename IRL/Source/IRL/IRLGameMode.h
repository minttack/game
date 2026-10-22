// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "IRLGameMode.generated.h"

class AIRLExperienceBeacon;
class AController;

/** Server-authoritative game rules for one shared IRL planet. */
UCLASS(abstract)
class AIRLGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AIRLGameMode();

	virtual void PreLogin(const FString& Options, const FString& Address,
		const FUniqueNetIdRepl& UniqueId, FString& ErrorMessage) override;
	virtual AActor* ChoosePlayerStart_Implementation(AController* Player) override;
	virtual void Logout(AController* Exiting) override;

protected:
	virtual void BeginPlay() override;

	/** Original First Signal gameplay stays intact. */
	UPROPERTY(EditDefaultsOnly, Category = "IRL|Experience")
	bool bSpawnFirstSignal = true;

	UPROPERTY(EditDefaultsOnly, Category = "IRL|Experience")
	TSubclassOf<AIRLExperienceBeacon> ExperienceBeaconClass;

	/** When on, two humans may join. Non-human world NPCs do not consume human slots. */
	UPROPERTY(EditDefaultsOnly, Category = "IRL|Duo")
	bool bUseDuoSpawning = true;

	/** Preferred separation of two human starting territories on the same level. */
	UPROPERTY(EditDefaultsOnly, Category = "IRL|Duo", meta = (ClampMin = "1200.0", UIMin = "1200.0"))
	float PreferredDuoSeparationCm = 50000.0f;

private:
	AActor* FindGroundedSecondaryStart(const FVector& FirstLocation);

	/** Server-only controller-to-start assignments, cleared on logout. */
	UPROPERTY(Transient)
	TMap<TObjectPtr<AController>, TObjectPtr<AActor>> DuoAssignedStarts;
};
