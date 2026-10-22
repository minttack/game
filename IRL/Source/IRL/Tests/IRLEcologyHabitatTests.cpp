// Engine-side tests for the same standalone native ecology kernel.
#if WITH_DEV_AUTOMATION_TESTS
#include "Experience/IRLEcologyCore.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FIRLGroundedEcologyTest,
    "IRL.Experience.GroundedEcology",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FIRLGroundedEcologyTest::RunTest(const FString& Parameters)
{
    IRLEcology::Habitat Habitat(3,3,123);
    TestTrue(TEXT("Habitat valid"),Habitat.Valid());
    TestTrue(TEXT("Finite food patch"),Habitat.SetTile(1,1,{2,2,0,0,false}));
    TestTrue(TEXT("Add individual"),Habitat.AddCreature(1,1));
    const auto First = Habitat.Step(1,IRLEcology::Policy::BIE);
    TestTrue(TEXT("Actual first step"),First.Valid);
    TestTrue(TEXT("Food consumed"),First.DidConsumeFood);
    TestEqual(TEXT("Finite food decreases"),Habitat.TileAt(1,1).Food,1);
    TestEqual(TEXT("Receipt cycle increments"),First.ExperienceCyclesAfter,std::uint64_t(1));
    TestEqual(TEXT("Food accounting increments"),Habitat.FoodConsumed(),std::uint64_t(1));
    const auto Second = Habitat.Step(1,IRLEcology::Policy::BIE);
    TestTrue(TEXT("Second action witnessed"),Second.Valid);
    TestEqual(TEXT("Two cycles directly observed"),Habitat.Find(1)->Experience.Cycles(),std::uint64_t(2));

    IRLEcology::Habitat Danger(1,1,1);
    TestTrue(TEXT("Risk patch"),Danger.SetTile(0,0,{0,0,0,90,false}));
    TestTrue(TEXT("Seed endangered life"),Danger.AddCreature(0,0,40));
    auto Death = Danger.Step(1);
    TestTrue(TEXT("Death has observed receipt"),Death.Valid);
    TestFalse(TEXT("Actual physical energy loss causes death"),Death.Survived);
    TestFalse(TEXT("No learning action after death"),Danger.Step(1).Valid);
    return true;
}
#endif
