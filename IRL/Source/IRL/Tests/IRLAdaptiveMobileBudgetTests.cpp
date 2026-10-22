#if WITH_DEV_AUTOMATION_TESTS
#include "Visual/IRLVisualBudgetCore.h"
#include "Misc/AutomationTest.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FIRLAdaptiveMobileBudgetTest,
    "IRL.Visual.MobileBudgetPolicy",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FIRLAdaptiveMobileBudgetTest::RunTest(const FString& Parameters)
{
    IRLVisual::BudgetController Budget;
    IRLVisual::Decision Decision;
    TestEqual(TEXT("Balanced initial tier"), static_cast<int32>(Budget.CurrentTier()), 1);
    for (int I=0;I<150;++I) { Budget.Observe(1.0 / 30.0,Decision); }
    TestEqual(TEXT("Stable thirty FPS doesn't thrash"),static_cast<int32>(Budget.CurrentTier()),1);
    for (int I=0;I<150;++I) { Budget.Observe(1.0 / 20.0,Decision); }
    TestEqual(TEXT("Repeated slow frames reduce cost"),static_cast<int32>(Budget.CurrentTier()),0);
    TestTrue(TEXT("Frames were actually measured"),Budget.TotalWindows() >= 5);
    return true;
}
#endif
