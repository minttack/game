#if WITH_DEV_AUTOMATION_TESTS
#include "Experience/IRLLifeLearningCore.h"
#include "World/IRLWorldScale.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FIRLLifeCorePolicyTest, "IRL.Experience.LifeLearningEvidence",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FIRLLifeCorePolicyTest::RunTest(const FString& Parameters)
{
    IRLLife::ExperienceLearner Learner;
    IRLLife::Observation Food{true, false};
    IRLLife::PredictionReceipt Receipt;
    TestTrue(TEXT("first committed prediction"), Learner.Propose(Food, Receipt));
    TestFalse(TEXT("cannot erase unresolved prediction"), Learner.Propose(Food, Receipt));
    TestEqual(TEXT("no observations before outcome"), Learner.Cycles(), std::uint64_t(0));
    TestTrue(TEXT("record real outcome"), Learner.RecordObservedOutcome(Receipt, 0.8, true));
    TestEqual(TEXT("experience counter"), Learner.Cycles(), std::uint64_t(1));
    const IRLLife::ExperienceLearner Child = Learner.SpawnNextGeneration(0.75);
    TestEqual(TEXT("child has no invented observations"), Child.Cycles(), std::uint64_t(0));
    TestEqual(TEXT("child has new generation"), Child.Generation(), std::uint32_t(1));

    const auto Budget = IRLLife::PopulationBudget::Plan(1000000000000ULL, 1000);
    TestTrue(TEXT("population count stays conserved"), Budget.CountsConserved());
    TestEqual(TEXT("only bounded active individuals"),
        Budget.IndividuallyActive, std::uint64_t(1000));
    TestEqual(TEXT("real world centimeter scale"),
        IRLWorldScale::MetersToUE(1.75), 175.0);
    return true;
}
#endif
