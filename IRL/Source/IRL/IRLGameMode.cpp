// Copyright Epic Games, Inc. All Rights Reserved.

#include "IRLGameMode.h"

#include "Engine/World.h"
#include "EngineUtils.h"
#include "Experience/IRLExperienceBeacon.h"
#include "GameFramework/PlayerStart.h"

AIRLGameMode::AIRLGameMode()
{
	ExperienceBeaconClass = AIRLExperienceBeacon::StaticClass();
}

void AIRLGameMode::BeginPlay()
{
	Super::BeginPlay();

	if (!bSpawnFirstSignal || !ExperienceBeaconClass || !GetWorld())
	{
		return;
	}

	FTransform SpawnTransform(FRotator::ZeroRotator, FVector(550.0f, 0.0f, 120.0f));
	for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It)
	{
		const FVector ForwardOffset = It->GetActorForwardVector() * 550.0f;
		SpawnTransform = FTransform(It->GetActorRotation(), It->GetActorLocation() + ForwardOffset + FVector(0.0f, 0.0f, 90.0f));
		break;
	}

	GetWorld()->SpawnActor<AIRLExperienceBeacon>(ExperienceBeaconClass, SpawnTransform);
}
