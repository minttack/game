// BIE Experience embodied agent adapter. Add to an existing or new NPC Blueprint.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Experience/IRLLifeLearningCore.h"
#include "IRLLifeExperienceComponent.generated.h"

UENUM(BlueprintType)
enum class EIRLLifeAction : uint8
{
    Forage UMETA(DisplayName="Forage"),
    Shelter UMETA(DisplayName="Take shelter"),
    Explore UMETA(DisplayName="Explore")
};

UCLASS(ClassGroup=(IRL), meta=(BlueprintSpawnableComponent))
class IRL_API UIRLLifeExperienceComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UIRLLifeExperienceComponent();

    /** Observe a real state, commit a prediction, then execute OutAction in gameplay. */
    UFUNCTION(BlueprintCallable, Category="IRL|BIE Life")
    bool ProposeAction(bool bFoodNearby, bool bThreatNearby,
        EIRLLifeAction& OutAction, float& OutPredictedReward);

    /** Feedback must come from witnessed gameplay; normalized reward is [-1,1].
     * A false survival result ends this individual's future action cycles.
     */
    UFUNCTION(BlueprintCallable, Category="IRL|BIE Life")
    bool RecordActionOutcome(float NormalizedReward, bool bSurvived);

    /** Reproduce a provisional behavioral bias while resetting all observation counts. */
    UFUNCTION(BlueprintCallable, Category="IRL|BIE Life")
    bool BeginInheritedLife(const UIRLLifeExperienceComponent* Parent, float Retention);

    UFUNCTION(BlueprintPure, Category="IRL|BIE Life")
    int32 ObservedExperienceCycles() const;

    UFUNCTION(BlueprintPure, Category="IRL|BIE Life")
    int32 LifeGeneration() const;

    UFUNCTION(BlueprintPure, Category="IRL|BIE Life")
    bool IsLiving() const;

    UFUNCTION(BlueprintPure, Category="IRL|BIE Life")
    float ObservedTrainingPredictionError() const;

private:
    // Not yet serialized or network-replicated. Server owns learned world state.
    IRLLife::ExperienceLearner Kernel;
    IRLLife::PredictionReceipt Pending;
};
