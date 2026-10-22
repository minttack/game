// IRL: small deterministic rules shared by the server and automation tests.
#pragma once

#include "CoreMinimal.h"

namespace IRLDuoSpawnRules
{
	constexpr int32 MaximumHumanPlayers = 2;
	constexpr float MinimumSeparationCm = 1200.0f;

	inline bool HasOpenSlot(int32 ConnectedHumanPlayers)
	{
		return ConnectedHumanPlayers >= 0 && ConnectedHumanPlayers < MaximumHumanPlayers;
	}

	inline bool IsDistinctLocation(const FVector& First, const FVector& Second)
	{
		// Two starts at different altitudes but above the same location are not distinct.
		return FVector::DistSquared2D(First, Second) >= FMath::Square(MinimumSeparationCm);
	}
}
