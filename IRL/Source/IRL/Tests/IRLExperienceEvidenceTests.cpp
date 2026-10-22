// IRL: evidence-gated objectives are opt-in; existing tutorials remain playable.
#if WITH_DEV_AUTOMATION_TESTS
#include "Experience/IRLExperienceSubsystem.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FIRLExperienceEvidenceGateTest,
    "IRL.Experience.SourceReportedEvidenceGate",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FIRLExperienceEvidenceGateTest::RunTest(const FString& Parameters)
{
    UIRLExperienceSubsystem* Experience = NewObject<UIRLExperienceSubsystem>();
    TestNotNull(TEXT("Subsystem exists"), Experience);
    if (!Experience) { return false; }

    // Existing tutorial is unchanged. Its prescribed text is NOT counted as data.
    TestTrue(TEXT("Guided First Signal begins"), Experience->BeginDefaultObjective());
    TestEqual(TEXT("Guided objective has zero trial receipts"),
        Experience->GetSourceReportedOutcomeCount(), 0);
    for (int32 I = 0; I < 5; ++I)
    {
        TestTrue(TEXT("Guided phase still advances"), Experience->AdvanceExperience());
    }
    TestTrue(TEXT("Guided completion still possible"), Experience->IsExperienceComplete());

    FIRLObjectiveDefinition Research = UIRLExperienceSubsystem::BuildFirstSignalObjective();
    Research.ObjectiveId = TEXT("EvidenceGateResearchTest");
    Research.bRequireSourceReportedOutcomeAtTest = true;
    TestTrue(TEXT("Evidence-required objective begins"), Experience->BeginObjective(Research));
    TestEqual(TEXT("Old objective evidence not carried"), Experience->GetSourceReportedOutcomeCount(), 0);

    for (int32 I = 0; I < 3; ++I)
    {
        TestTrue(TEXT("Navigate to Test phase"), Experience->AdvanceExperience());
    }
    TestEqual(TEXT("Reached Test phase"), Experience->GetCurrentStep().Phase,
        EIRLExperiencePhase::Test);
    TestFalse(TEXT("Cannot leave Test without reported result"), Experience->AdvanceExperience());

    int32 ReceiptId = 0;
    TestTrue(TEXT("Prediction is committed"), Experience->StartEvidencePrediction(
        FName(TEXT("TrustedWorldProbe")), 0.75f, ReceiptId));
    TestTrue(TEXT("Receipt ID is positive"), ReceiptId > 0);
    TestFalse(TEXT("Prediction alone does not pass gate"), Experience->AdvanceExperience());
    TestFalse(TEXT("Cannot record wrong source"), Experience->ReportEvidenceOutcome(
        FName(TEXT("OtherProbe")), ReceiptId, 0.25f));
    TestFalse(TEXT("Cannot record wrong receipt"), Experience->ReportEvidenceOutcome(
        FName(TEXT("TrustedWorldProbe")), ReceiptId + 1, 0.25f));
    TestTrue(TEXT("Match outcome to prediction"), Experience->ReportEvidenceOutcome(
        FName(TEXT("TrustedWorldProbe")), ReceiptId, 0.25f));
    TestFalse(TEXT("Duplicate outcome is rejected"), Experience->ReportEvidenceOutcome(
        FName(TEXT("TrustedWorldProbe")), ReceiptId, 0.25f));
    TestEqual(TEXT("Exactly one recorded report"), Experience->GetSourceReportedOutcomeCount(), 1);
    TestTrue(TEXT("Reported MSE is 0.25"), FMath::IsNearlyEqual(
        Experience->GetReportedPredictionMSE(), 0.25f));
    TestTrue(TEXT("Gate opens after matched reported outcome"), Experience->AdvanceExperience());
    TestTrue(TEXT("Resolve advances to Complete"), Experience->AdvanceExperience());
    TestTrue(TEXT("Evidence-gated objective completes"), Experience->IsExperienceComplete());

    Experience->ResetExperience();
    TestEqual(TEXT("Reset clears objective reports"), Experience->GetSourceReportedOutcomeCount(), 0);
    TestFalse(TEXT("Cannot replay report after reset"), Experience->ReportEvidenceOutcome(
        FName(TEXT("TrustedWorldProbe")), ReceiptId, 0.25f));

    // Invalid definitions cannot silently bypass the evidence-required Test step.
    FIRLObjectiveDefinition NoTest = Research;
    NoTest.Steps.RemoveAll([](const FIRLExperienceStep& Step)
    {
        return Step.Phase == EIRLExperiencePhase::Test;
    });
    TestFalse(TEXT("Evidence-required objective must have Test phase"), Experience->BeginObjective(NoTest));
    return true;
}
#endif
