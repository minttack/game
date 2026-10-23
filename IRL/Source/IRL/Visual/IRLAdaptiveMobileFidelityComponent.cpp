#include "Visual/IRLAdaptiveMobileFidelityComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameUserSettings.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Misc/Guid.h"
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
    MobileEvidence.Reset();
    MobileEvidenceSessionId = FGuid::NewGuid().ToString(EGuidFormats::Digits);
    MobileEvidenceWindowIndex = 0;
#else
    SetComponentTickEnabled(false); // preserve desktop, editor and server fidelity
#endif
}

void UIRLAdaptiveMobileFidelityComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
#if PLATFORM_ANDROID
    // Source-reported game-frame and joystick evidence, every ~10 seconds.
    // Android logcat can capture this marker. This is NOT a GPU timer.
    IRLMobileEvidence::Window Window;
    if (MobileEvidence.Observe(static_cast<double>(DeltaTime), Window))
    {
        UE_LOG(LogTemp, Display,
            TEXT("IRL_MOBILE_EVIDENCE_V1 session=%s seq=%u frames=%u rejected=%u duration_s=%.3f mean_ms=%.3f p50_ms=%.3f p95_ms=%.3f p99_ms=%.3f max_ms=%.3f move_axes=%u look_axes=%u jumps=%u experiences=%u tier=%d"),
            *MobileEvidenceSessionId, ++MobileEvidenceWindowIndex,
            Window.Frames, Window.Rejected, Window.DurationSeconds, Window.MeanMs,
            Window.P50Ms, Window.P95Ms, Window.P99Ms, Window.MaxMs,
            Window.MoveAxes, Window.LookAxes, Window.Jumps, Window.Experiences,
            static_cast<int32>(Budget.CurrentTier()));
    }
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

void UIRLAdaptiveMobileFidelityComponent::RecordMobileInput(
    IRLMobileEvidence::InputKind Kind)
{
#if PLATFORM_ANDROID
    const APlayerController* Controller = Cast<APlayerController>(GetOwner());
    if (Controller && Controller->IsLocalController())
    {
        MobileEvidence.MarkInput(Kind);
    }
#else
    (void)Kind;
#endif
}
