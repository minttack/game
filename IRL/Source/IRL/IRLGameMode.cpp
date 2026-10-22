// Copyright Epic Games, Inc. All Rights Reserved.

#include "IRLGameMode.h"

#include "Engine/World.h"
#include "EngineUtils.h"
#include "Experience/IRLExperienceBeacon.h"
#include "GameFramework/Controller.h"
#include "GameFramework/PlayerStart.h"
#include "IRL.h"
#include "World/IRLDuoSpawnRules.h"

AIRLGameMode::AIRLGameMode()
{
	ExperienceBeaconClass = AIRLExperienceBeacon::StaticClass();
}

void AIRLGameMode::PreLogin(const FString& Options, const FString& Address,
	const FUniqueNetIdRepl& UniqueId, FString& ErrorMessage)
{
	Super::PreLogin(Options, Address, UniqueId, ErrorMessage);
	if (ErrorMessage.IsEmpty() && bUseDuoSpawning && !IRLDuoSpawnRules::HasOpenSlot(GetNumPlayers()))
	{
		ErrorMessage = TEXT("IRL duo planet is full (2 human players).");
	}
}

AActor* AIRLGameMode::ChoosePlayerStart_Implementation(AController* Player)
{
	if (!bUseDuoSpawning || !Player || !GetWorld())
	{
		return Super::ChoosePlayerStart_Implementation(Player);
	}

	if (TObjectPtr<AActor>* Previous = DuoAssignedStarts.Find(Player))
	{
		if (IsValid(Previous->Get()))
		{
			return Previous->Get();
		}
		DuoAssignedStarts.Remove(Player);
	}

	if (DuoAssignedStarts.IsEmpty())
	{
		AActor* InitialStart = Super::ChoosePlayerStart_Implementation(Player);
		if (IsValid(InitialStart))
		{
			DuoAssignedStarts.Add(Player, InitialStart);
		}
		return InitialStart;
	}

	// The second human must start elsewhere in the same currently loaded level.
	AActor* FirstStart = nullptr;
	for (const auto& Assignment : DuoAssignedStarts)
	{
		if (IsValid(Assignment.Value.Get()))
		{
			FirstStart = Assignment.Value.Get();
			break;
		}
	}
	if (!FirstStart)
	{
		UE_LOG(LogIRL, Warning, TEXT("Duo start assignment lost; using standard player start."));
		return Super::ChoosePlayerStart_Implementation(Player);
	}

	AActor* BestStart = nullptr;
	float BestDistanceSq = 0.0f;
	for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It)
	{
		APlayerStart* Candidate = *It;
		if (!IsValid(Candidate) || !IRLDuoSpawnRules::IsDistinctLocation(
			FirstStart->GetActorLocation(), Candidate->GetActorLocation()))
		{
			continue;
		}
		const float DistanceSq = FVector::DistSquared2D(
			FirstStart->GetActorLocation(), Candidate->GetActorLocation());
		if (DistanceSq > BestDistanceSq)
		{
			BestDistanceSq = DistanceSq;
			BestStart = Candidate;
		}
	}

	if (!BestStart)
	{
		BestStart = FindGroundedSecondaryStart(FirstStart->GetActorLocation());
	}

	if (!BestStart)
	{
		// No claim of separated spawns if terrain cannot support them.
		UE_LOG(LogIRL, Error, TEXT("IRL duo: no safe second territory. Add two separated PlayerStart actors or playable terrain."));
		BestStart = Super::ChoosePlayerStart_Implementation(Player);
	}

	if (IsValid(BestStart))
	{
		DuoAssignedStarts.Add(Player, BestStart);
	}
	return BestStart;
}

AActor* AIRLGameMode::FindGroundedSecondaryStart(const FVector& FirstLocation)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return nullptr;
	}

	// Large planets prefer distant starts; the existing tiny tutorial map can use nearer starts.
	const float Distances[] = {
		FMath::Max(PreferredDuoSeparationCm, 1200.0f),
		FMath::Max(PreferredDuoSeparationCm * 0.5f, 1200.0f),
		10000.0f, 3500.0f, 1800.0f
	};
	const FVector2D Directions[] = {
		FVector2D(1.0f, 0.0f), FVector2D(0.0f, 1.0f),
		FVector2D(-1.0f, 0.0f), FVector2D(0.0f, -1.0f)
	};

	for (float Distance : Distances)
	{
		for (const FVector2D& Direction : Directions)
		{
			const FVector Horizontal(FirstLocation.X + Direction.X * Distance,
				FirstLocation.Y + Direction.Y * Distance, FirstLocation.Z);
			FHitResult Hit;
			if (!World->LineTraceSingleByChannel(Hit, Horizontal + FVector(0, 0, 20000),
				Horizontal - FVector(0, 0, 20000), ECC_Visibility) ||
				!Hit.bBlockingHit || Hit.ImpactNormal.Z < 0.7f)
			{
				continue;
			}

			const FVector CandidateLocation = Hit.ImpactPoint + FVector(0, 0, 100);
			if (!IRLDuoSpawnRules::IsDistinctLocation(FirstLocation, CandidateLocation))
			{
				continue;
			}

			FActorSpawnParameters Parameters;
			Parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
			APlayerStart* NewStart = World->SpawnActor<APlayerStart>(
				APlayerStart::StaticClass(), CandidateLocation, FRotator::ZeroRotator, Parameters);
			if (NewStart)
			{
				UE_LOG(LogIRL, Log, TEXT("Duo: generated grounded secondary spawn %.0f cm away."), Distance);
				return NewStart;
			}
		}
	}
	return nullptr;
}

void AIRLGameMode::Logout(AController* Exiting)
{
	DuoAssignedStarts.Remove(Exiting);
	Super::Logout(Exiting);
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
