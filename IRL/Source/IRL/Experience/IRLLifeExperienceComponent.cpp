#include "Experience/IRLLifeExperienceComponent.h"
#include "GameFramework/Actor.h"

UIRLLifeExperienceComponent::UIRLLifeExperienceComponent()
{
    PrimaryComponentTick.bCanEverTick = false; // Event driven, not per-frame for millions of actors.
}

bool UIRLLifeExperienceComponent::ProposeAction(bool bFoodNearby, bool bThreatNearby,
    EIRLLifeAction& OutAction, float& OutPredictedReward)
{
    if (!GetOwner() || !GetOwner()->HasAuthority())
    {
        return false;
    }

    const IRLLife::Observation Obs{bFoodNearby, bThreatNearby};
    if (!Kernel.Propose(Obs, Pending)) { return false; }
    OutAction = static_cast<EIRLLifeAction>(Pending.ChosenAction);
    OutPredictedReward = static_cast<float>(Pending.PredictedReward);
    return true;
}

bool UIRLLifeExperienceComponent::RecordActionOutcome(float NormalizedReward, bool bSurvived)
{
    if (!GetOwner() || !GetOwner()->HasAuthority() ||
        !FMath::IsFinite(NormalizedReward))
    {
        return false;
    }

    return Kernel.RecordObservedOutcome(Pending, NormalizedReward, bSurvived);
}

bool UIRLLifeExperienceComponent::BeginInheritedLife(
    const UIRLLifeExperienceComponent* Parent, float Retention)
{
    if (!GetOwner() || !GetOwner()->HasAuthority() ||
        !Parent || Parent == this || Kernel.Cycles() > 0 ||
        Kernel.HasPendingOutcome() || !FMath::IsFinite(Retention))
    {
        return false;
    }

    Kernel = Parent->Kernel.SpawnNextGeneration(Retention);
    Pending = IRLLife::PredictionReceipt{};
    return true;
}

int32 UIRLLifeExperienceComponent::ObservedExperienceCycles() const
{
    return static_cast<int32>(FMath::Min<std::uint64_t>(
        Kernel.Cycles(), static_cast<std::uint64_t>(MAX_int32)));
}

int32 UIRLLifeExperienceComponent::LifeGeneration() const
{
    return static_cast<int32>(FMath::Min<std::uint32_t>(
        Kernel.Generation(), static_cast<std::uint32_t>(MAX_int32)));
}

bool UIRLLifeExperienceComponent::IsLiving() const { return Kernel.IsAlive(); }
float UIRLLifeExperienceComponent::ObservedTrainingPredictionError() const
{
    return static_cast<float>(Kernel.TrainingPredictionMSE());
}
