// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Experience/IRLExperienceTypes.h"
#include "GameFramework/PlayerController.h"
#include "IRLPlayerController.generated.h"

class UInputMappingContext;
class UInputAction;
struct FInputActionValue;
class UEnhancedInputLocalPlayerSubsystem;
class UEnhancedInputComponent;
class UUserWidget;
class UIRLAdaptiveMobileFidelityComponent;

/**
 *  Basic PlayerController class for a third person game
 *  Manages input mappings
 */
UCLASS(abstract)
class AIRLPlayerController : public APlayerController
{
	GENERATED_BODY()
	
public:
    AIRLPlayerController();
    /** Mobile action entrypoint: respects existing objective gates and local ownership. */
    UFUNCTION(BlueprintCallable, Category="IRL|Experience")
    void AdvanceIRLExperience();

protected:
    /** Mobile-only: observes frame times and revises LOCAL visual quality. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="IRL|Mobile Fidelity")
    TObjectPtr<UIRLAdaptiveMobileFidelityComponent> MobileFidelity;


	UFUNCTION()
	void HandleExperienceAdvanced(EIRLExperiencePhase Phase, const FText& BlueGuidance, const FText& BIEStatement);

	UFUNCTION()
	void HandleExperienceCompleted(FName ObjectiveId);

	/** Input Mapping Contexts */
	UPROPERTY(EditAnywhere, Category ="Input|Input Mappings")
	TArray<UInputMappingContext*> DefaultMappingContexts;

	/** Input Mapping Contexts */
	UPROPERTY(EditAnywhere, Category="Input|Input Mappings")
	TArray<UInputMappingContext*> MobileExcludedMappingContexts;

	/** Mobile controls widget to spawn */
	UPROPERTY(EditAnywhere, Category="Input|Touch Controls")
	TSubclassOf<UUserWidget> MobileControlsWidgetClass;

	/** Pointer to the mobile controls widget */
	UPROPERTY()
	TObjectPtr<UUserWidget> MobileControlsWidget;

    /** Runtime-native joystick mapping uses axis keys from Unreal's built-in
     * two-stick touch interface. This owns and retains its input assets.
     * Avoids dependence on uninspected IMC_Default.uasset gamepad mappings.
     */
    UPROPERTY(Transient)
    TObjectPtr<UInputMappingContext> NativeMobileInputContext;

    UPROPERTY(Transient)
    TObjectPtr<UInputAction> NativeMobileMoveAction;

    UPROPERTY(Transient)
    TObjectPtr<UInputAction> NativeMobileLookAction;

    void InstallNativeMobileJoystick(UEnhancedInputLocalPlayerSubsystem* Subsystem);
    void HandleMobileMove(const FInputActionValue& Value);
    void HandleMobileLook(const FInputActionValue& Value);

	/** If true, the player will use UMG touch controls even if not playing on mobile platforms */
	UPROPERTY(EditAnywhere, Config, Category = "Input|Touch Controls")
	bool bForceTouchControls = false;

	/** Gameplay initialization */
	virtual void BeginPlay() override;

	/** Input mapping context setup */
	virtual void SetupInputComponent() override;

	/** Returns true if the player should use UMG touch controls */
	bool ShouldUseTouchControls() const;

};
