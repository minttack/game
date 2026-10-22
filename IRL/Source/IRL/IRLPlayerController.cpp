// Copyright Epic Games, Inc. All Rights Reserved.


#include "IRLPlayerController.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/GameInstance.h"
#include "Engine/LocalPlayer.h"
#include "InputMappingContext.h"
#include "Blueprint/UserWidget.h"
#include "Experience/IRLExperienceSubsystem.h"
#include "IRL.h"
#include "Visual/IRLAdaptiveMobileFidelityComponent.h"
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

	// only spawn touch controls on local player controllers
	if (IsLocalPlayerController() && ShouldUseTouchControls())
	{
		// spawn the mobile controls widget
		MobileControlsWidget = CreateWidget<UUserWidget>(this, MobileControlsWidgetClass);

		if (MobileControlsWidget)
		{
			// add the controls to the player screen
			MobileControlsWidget->AddToPlayerScreen(0);

		} else {

			UE_LOG(LogIRL, Error, TEXT("Could not spawn mobile controls widget."));

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

bool AIRLPlayerController::ShouldUseTouchControls() const
{
	// are we on a mobile platform? Should we force touch?
	return SVirtualJoystick::ShouldDisplayTouchInterface() || bForceTouchControls;
}
