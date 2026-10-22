#include "Visual/IRLAdaptiveMobileFidelityComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameUserSettings.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Visual/IRLLivingBiomeDetailActor.h"

UIRLAdaptiveMobileFidelityComponent::UIRLAdaptiveMobileFidelityComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UIRLAdaptiveMobileFidelityComponent::BeginPlay()
{
    Super::BeginPlay();
#if PLATFORM_ANDROID
    const APlayerController* Controller = Cast<APlayerController>(GetOwner());
    if (!Controller || !Controller->IsLocalController())
    {
        SetComponentTickEnabled(false);
        return;
    }
    // Do not replace the hardware device profile on boot. Give it warmup time.
    Budget.Reset(IRLVisual::Tier::Balanced, 30.0);
#else
    SetComponentTickEnabled(false); // preserve desktop, editor and server fidelity
#endif
}

void UIRLAdaptiveMobileFidelityComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
#if PLATFORM_ANDROID
    if (!bAdaptiveQualityEnabled) { return; }
    IRLVisual::Decision Decision;
    if (Budget.Observe(static_cast<double>(DeltaTime), Decision) && Decision.Changed)
    {
        ApplyTier(Decision.Selected);
        UE_LOG(LogTemp, Display, TEXT("IRL BIE graphics evidence: frame=%.1f ms samples=%u window=%llu tier=%d reason=%d"),
            Decision.MeanFrameMs, Decision.ValidFrames,
            static_cast<unsigned long long>(Decision.ObservationWindow),
            static_cast<int32>(Decision.Selected), static_cast<int32>(Decision.Cause));
    }
#endif
}

void UIRLAdaptiveMobileFidelityComponent::ApplyTier(IRLVisual::Tier Tier)
{
#if PLATFORM_ANDROID
    // Local rendering only: never changes the server world or other player's quality.
    UGameUserSettings* Settings = UGameUserSettings::GetGameUserSettings();
    if (!Settings) { return; }
    const int32 Q = static_cast<int32>(Tier);
    Settings->SetViewDistanceQuality(Q);
    Settings->SetAntiAliasingQuality(Q);
    Settings->SetShadowQuality(Tier == IRLVisual::Tier::Detail ? 2 : Q);
    Settings->SetPostProcessingQuality(Q);
    Settings->SetTextureQuality(Q);
    Settings->SetEffectsQuality(Q);
    Settings->SetFoliageQuality(Q);
    Settings->ApplyNonResolutionSettings();
    if (UWorld* World = GetWorld())
    {
        // Decorative instances are strictly local; neither player changes authoritative life.
        for (TActorIterator<AIRLLivingBiomeDetailActor> It(World); It; ++It)
        {
            It->ApplyVisualTier(Q);
        }
    }
#else
    (void)Tier;
#endif
}
