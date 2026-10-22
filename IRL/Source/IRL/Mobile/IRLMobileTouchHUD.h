// IRL Android: no-blueprint-dependency touch action overlay.
// Movement/look are provided by Unreal's two built-in virtual joysticks.
#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "IRLMobileTouchHUD.generated.h"

class UButton;
class UWidgetTree;

UCLASS()
class IRL_API UIRLMobileTouchHUD : public UUserWidget
{
    GENERATED_BODY()
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    virtual void NativeConstruct() override;
    UFUNCTION()
    void OnJumpPressed();
    UFUNCTION()
    void OnJumpReleased();
    UFUNCTION()
    void OnExperiencePressed();
private:
    UPROPERTY(Transient)
    TObjectPtr<UButton> JumpButton;
    UPROPERTY(Transient)
    TObjectPtr<UButton> ExperienceButton;
    void BuildRoot();
};
