// Native client-side mobile fidelity adaptation for the SAME IRL game.
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Visual/IRLVisualBudgetCore.h"
#include "Mobile/IRLMobileEvidenceCore.h"
#include "IRLAdaptiveMobileFidelityComponent.generated.h"

UCLASS(ClassGroup=(IRL), meta=(BlueprintSpawnableComponent))
class IRL_API UIRLAdaptiveMobileFidelityComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UIRLAdaptiveMobileFidelityComponent();
    /** Count input callbacks on the local Android client, never remote players. */
    void RecordMobileInput(IRLMobileEvidence::InputKind Kind);
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="IRL|Mobile Fidelity")
    bool bAdaptiveQualityEnabled = true;

    UFUNCTION(BlueprintPure, Category="IRL|Mobile Fidelity")
    int32 CurrentVisualTier() const { return static_cast<int32>(Budget.CurrentTier()); }

    UFUNCTION(BlueprintPure, Category="IRL|Mobile Fidelity")
    float LastObservedFrameMs() const { return static_cast<float>(Budget.LastWindowMeanMs()); }

    UFUNCTION(BlueprintPure, Category="IRL|Mobile Fidelity")
    int32 ValidObservationWindows() const { return static_cast<int32>(
        FMath::Min<uint64>(Budget.TotalWindows(),static_cast<uint64>(MAX_int32))); }

    UFUNCTION(BlueprintPure, Category="IRL|Mobile Fidelity")
    int32 ExcludedPauseOrLoadSamples() const { return static_cast<int32>(
        FMath::Min<uint64>(Budget.RejectedSamples(),static_cast<uint64>(MAX_int32))); }
private:
    IRLVisual::BudgetController Budget;
    IRLMobileEvidence::Recorder MobileEvidence;
    FString MobileEvidenceSessionId;
    uint32 MobileEvidenceWindowIndex = 0;
    void ApplyTier(IRLVisual::Tier Tier);
};
