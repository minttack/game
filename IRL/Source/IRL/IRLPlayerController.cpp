// Copyright Epic Games, Inc. All Rights Reserved.


#include "IRLPlayerController.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/GameInstance.h"
#include "Engine/LocalPlayer.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "InputActionValue.h"
#include "InputModifiers.h"
#include "InputCoreTypes.h"
#include "EnhancedInputComponent.h"
#include "IRLCharacter.h"
#include "Mobile/IRLMobileJoystickCore.h"
#include "Blueprint/UserWidget.h"
#include "Experience/IRLExperienceSubsystem.h"
#include "IRL.h"
#include "Visual/IRLAdaptiveMobileFidelityComponent.h"
#include "Mobile/IRLMobileTouchHUD.h"
#include "Widgets/Input/SVirtualJoystick.h"

AIRLPlayerController::AIRLPlayerController()
{
    MobileFidelity = CreateDefaultSubobject<UIRLAdaptiveMobileFidelityComponent>(TEXT("MobileFidelity"));
}

void AIRLPlayerController::BeginPlay()
{
	Super::BeginPlay();

	if (UGameInstance* GameInstance = GetGameInstance())
	{
		if (UIRLExperienceSubsystem* Experience = GameInstance->GetSubsystem<UIRLExperienceSubsystem>())
		{
			Experience->OnExperienceAdvanced.AddUniqueDynamic(this, &AIRLPlayerController::HandleExperienceAdvanced);
			Experience->OnExperienceCompleted.AddUniqueDynamic(this, &AIRLPlayerController::HandleExperienceCompleted);
		}
	}

	// Android-first: Unreal's two native virtual joysticks handle moving and
	// looking; our UMG overlay adds Jump and the BIE experience action.
	// If a creator-supplied Blueprint exists, honor it. Otherwise a compiled
	// widget provides a functional baseline with NO binary UMG asset required.
	if (IsLocalPlayerController() && ShouldUseTouchControls())
	{
		TSubclassOf<UUserWidget> TouchClass=MobileControlsWidgetClass;
		if (!TouchClass)
		{
			TouchClass=UIRLMobileTouchHUD::StaticClass();
		}
		MobileControlsWidget = CreateWidget<UUserWidget>(this, TouchClass);
		if (MobileControlsWidget)
		{
			MobileControlsWidget->AddToPlayerScreen(100);
		}
		else
		{
			UE_LOG(LogIRL, Error, TEXT("IRL touch HUD failed: phone action buttons unavailable."));
		}
	}
}

void AIRLPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();

	// only add IMCs for local player controllers
	if (IsLocalPlayerController())
	{
		// Add Input Mapping Contexts
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
		{
			for (UInputMappingContext* CurrentContext : DefaultMappingContexts)
			{
				Subsystem->AddMappingContext(CurrentContext, 0);
			}

            // Native binding overrides only joystick axes on the local mobile
            // player. Desktop, BIE gameplay and user-supplied keyboard contexts
            // retain their original mappings.
            if (ShouldUseTouchControls())
            {
                InstallNativeMobileJoystick(Subsystem);
            }

			// only add these IMCs if we're not using mobile touch input
			if (!ShouldUseTouchControls())
			{
				for (UInputMappingContext* CurrentContext : MobileExcludedMappingContexts)
				{
					Subsystem->AddMappingContext(CurrentContext, 0);
				}
			}
		}
	}
}

void AIRLPlayerController::AdvanceIRLExperience()
{
	if (UGameInstance* GameInstance = GetGameInstance())
	{
		if (UIRLExperienceSubsystem* Experience = GameInstance->GetSubsystem<UIRLExperienceSubsystem>())
		{
			if (Experience->IsExperienceComplete())
			{
				ClientMessage(TEXT("BIE: The First Signal is already complete."));
				return;
			}

			if (Experience->AdvanceExperience())
			{
				return;
			}
		}
	}

	ClientMessage(TEXT("BIE: Find and approach the First Signal before advancing."));
}

void AIRLPlayerController::HandleExperienceAdvanced(EIRLExperiencePhase Phase, const FText& BlueGuidance,
	const FText& BIEStatement)
{
	const UEnum* PhaseEnum = StaticEnum<EIRLExperiencePhase>();
	const FString PhaseName = PhaseEnum ? PhaseEnum->GetDisplayNameTextByValue(static_cast<int64>(Phase)).ToString() : TEXT("Experience");
	ClientMessage(FString::Printf(TEXT("[%s]"), *PhaseName));
	ClientMessage(BlueGuidance.ToString());
	ClientMessage(BIEStatement.ToString());
}

void AIRLPlayerController::HandleExperienceCompleted(FName ObjectiveId)
{
	ClientMessage(FString::Printf(TEXT("OBJECTIVE COMPLETE: %s"), *ObjectiveId.ToString()));
}

void AIRLPlayerController::InstallNativeMobileJoystick(
    UEnhancedInputLocalPlayerSubsystem* Subsystem)
{
    if (!IsLocalPlayerController() || !Subsystem) { return; }
    UEnhancedInputComponent* Enhanced = Cast<UEnhancedInputComponent>(InputComponent);
    if (!Enhanced)
    {
        UE_LOG(LogIRL, Error, TEXT("IRL Android joystick cannot bind: EnhancedInputComponent missing"));
        return;
    }
    if (NativeMobileInputContext) { return; } // no duplicate mappings on restart

    NativeMobileInputContext = NewObject<UInputMappingContext>(this, TEXT("IRLNativeMobileContext"));
    NativeMobileMoveAction = NewObject<UInputAction>(this, TEXT("IRLNativeMobileMove"));
    NativeMobileLookAction = NewObject<UInputAction>(this, TEXT("IRLNativeMobileLook"));
    if (!NativeMobileInputContext || !NativeMobileMoveAction || !NativeMobileLookAction) { return; }
    NativeMobileMoveAction->ValueType = EInputActionValueType::Axis2D;
    NativeMobileLookAction->ValueType = EInputActionValueType::Axis2D;
    NativeMobileMoveAction->bConsumeInput = true;
    NativeMobileLookAction->bConsumeInput = true;

    // Original virtual joystick asset emits separate analog Gamepad_*X/Y keys.
    // Map Y using Swizzle; otherwise a 1D Y value becomes an X-only 2D action.
    NativeMobileInputContext->MapKey(NativeMobileMoveAction, EKeys::Gamepad_LeftX);
    FEnhancedActionKeyMapping& LeftY = NativeMobileInputContext->MapKey(
        NativeMobileMoveAction, EKeys::Gamepad_LeftY);
    UInputModifierSwizzleAxis* LeftSwizzle = NewObject<UInputModifierSwizzleAxis>(NativeMobileInputContext);
    LeftSwizzle->Order = EInputAxisSwizzle::YXZ;
    LeftY.Modifiers.Add(LeftSwizzle);

    NativeMobileInputContext->MapKey(NativeMobileLookAction, EKeys::Gamepad_RightX);
    FEnhancedActionKeyMapping& RightY = NativeMobileInputContext->MapKey(
        NativeMobileLookAction, EKeys::Gamepad_RightY);
    UInputModifierSwizzleAxis* RightSwizzle = NewObject<UInputModifierSwizzleAxis>(NativeMobileInputContext);
    RightSwizzle->Order = EInputAxisSwizzle::YXZ;
    RightY.Modifiers.Add(RightSwizzle);

    Enhanced->BindAction(NativeMobileMoveAction, ETriggerEvent::Triggered,
                         this, &AIRLPlayerController::HandleMobileMove);
    Enhanced->BindAction(NativeMobileLookAction, ETriggerEvent::Triggered,
                         this, &AIRLPlayerController::HandleMobileLook);
    // Priority above existing Blueprint mappings consumes joystick axis input
    // so movement/look are not accidentally applied twice.
    Subsystem->AddMappingContext(NativeMobileInputContext, 20);
    UE_LOG(LogIRL, Display, TEXT("IRL Android: local native joystick actions mapped"));
}

void AIRLPlayerController::HandleMobileMove(const FInputActionValue& Value)
{
    if (!IsLocalPlayerController()) { return; }
    if (AIRLCharacter* Character = Cast<AIRLCharacter>(GetPawn()))
    {
        const FVector2D Raw = Value.Get<FVector2D>();
        const IRLMobile::Axis2D Clean = IRLMobile::FilterJoystick(
            static_cast<float>(Raw.X), static_cast<float>(Raw.Y));
        Character->DoMove(Clean.X,Clean.Y);
    }
}

void AIRLPlayerController::HandleMobileLook(const FInputActionValue& Value)
{
    if (!IsLocalPlayerController()) { return; }
    if (AIRLCharacter* Character = Cast<AIRLCharacter>(GetPawn()))
    {
        const FVector2D Raw = Value.Get<FVector2D>();
        const IRLMobile::Axis2D Clean = IRLMobile::FilterJoystick(
            static_cast<float>(Raw.X), static_cast<float>(Raw.Y),0.08f);
        Character->DoLook(Clean.X,Clean.Y);
    }
}

bool AIRLPlayerController::ShouldUseTouchControls() const
{
#if PLATFORM_ANDROID
    return true; // Touch HUD always active on an Android phone
#else
    return SVirtualJoystick::ShouldDisplayTouchInterface() || bForceTouchControls;
#endif
}
