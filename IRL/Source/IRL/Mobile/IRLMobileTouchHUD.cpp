#include "Mobile/IRLMobileTouchHUD.h"
#include "IRLCharacter.h"
#include "IRLPlayerController.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"

void UIRLMobileTouchHUD::BuildRoot()
{
    if (!WidgetTree || WidgetTree->RootWidget) { return; }
    UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(
        UCanvasPanel::StaticClass(),TEXT("IRLMobileControlsRoot"));
    Root->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
    WidgetTree->RootWidget = Root;

    auto AddButton = [this, Root](FName Id, const TCHAR* Label,
                                 const FVector2D& Offset, const FVector2D& Size) -> UButton*
    {
        UButton* Button = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(),Id);
        Button->SetBackgroundColor(FLinearColor(0.04f, 0.09f, 0.13f, 0.70f));
        UTextBlock* Caption = WidgetTree->ConstructWidget<UTextBlock>(
            UTextBlock::StaticClass(),FName(*(Id.ToString()+TEXT("_Label"))));
        Caption->SetText(FText::FromString(Label));
        Caption->SetColorAndOpacity(FSlateColor(FLinearColor(1.0f,1.0f,1.0f,1.0f)));
        Caption->SetJustification(ETextJustify::Center);
        Caption->SetVisibility(ESlateVisibility::HitTestInvisible);
        Button->AddChild(Caption);
        UCanvasPanelSlot* Slot=Root->AddChildToCanvas(Button);
        Slot->SetAnchors(FAnchors(1.0f,1.0f));
        Slot->SetAlignment(FVector2D(1.0f,1.0f));
        Slot->SetPosition(Offset);
        Slot->SetSize(Size);
        Slot->SetAutoSize(false);
        return Button;
    };

    // Right-side action buttons live ABOVE the right camera joystick.
    JumpButton = AddButton(TEXT("IRLJumpButton"), TEXT("JUMP"),
                           FVector2D(-22.0f,-290.0f),FVector2D(110.0f,86.0f));
    ExperienceButton = AddButton(TEXT("IRLExperienceButton"),TEXT("EXPERIENCE"),
                                 FVector2D(-144.0f,-300.0f),FVector2D(144.0f,78.0f));
}

TSharedRef<SWidget> UIRLMobileTouchHUD::RebuildWidget()
{
    BuildRoot();
    return Super::RebuildWidget();
}

void UIRLMobileTouchHUD::NativeConstruct()
{
    Super::NativeConstruct();
    if (JumpButton)
    {
        JumpButton->OnPressed.RemoveDynamic(this,&UIRLMobileTouchHUD::OnJumpPressed);
        JumpButton->OnReleased.RemoveDynamic(this,&UIRLMobileTouchHUD::OnJumpReleased);
        JumpButton->OnPressed.AddDynamic(this,&UIRLMobileTouchHUD::OnJumpPressed);
        JumpButton->OnReleased.AddDynamic(this,&UIRLMobileTouchHUD::OnJumpReleased);
    }
    if (ExperienceButton)
    {
        ExperienceButton->OnPressed.RemoveDynamic(this,&UIRLMobileTouchHUD::OnExperiencePressed);
        ExperienceButton->OnPressed.AddDynamic(this,&UIRLMobileTouchHUD::OnExperiencePressed);
    }
}

void UIRLMobileTouchHUD::OnJumpPressed()
{
    APlayerController* Player=GetOwningPlayer();
    if (Player && Player->IsLocalController())
        if (AIRLCharacter* Pawn=Cast<AIRLCharacter>(Player->GetPawn()))
        {
            Pawn->DoJumpStart();
            if (AIRLPlayerController* MobileController = Cast<AIRLPlayerController>(Player))
                MobileController->RecordMobileInput(IRLMobileEvidence::InputKind::JumpPress);
        }
}

void UIRLMobileTouchHUD::OnJumpReleased()
{
    APlayerController* Player=GetOwningPlayer();
    if (Player && Player->IsLocalController())
        if (AIRLCharacter* Pawn=Cast<AIRLCharacter>(Player->GetPawn()))
            Pawn->DoJumpEnd();
}

void UIRLMobileTouchHUD::OnExperiencePressed()
{
    AIRLPlayerController* Player=Cast<AIRLPlayerController>(GetOwningPlayer());
    if (Player && Player->IsLocalController())
    {
        Player->RecordMobileInput(IRLMobileEvidence::InputKind::ExperiencePress);
        Player->AdvanceIRLExperience();
    }
}
