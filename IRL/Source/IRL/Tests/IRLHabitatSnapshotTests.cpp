// IRL: Engine automation checks for the bounded native visual snapshot contract.
#if WITH_DEV_AUTOMATION_TESTS
#include "Experience/IRLHabitatSnapshotCore.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FIRLHabitatSnapshotCodecTest,
    "IRL.Experience.HabitatSnapshotCodec",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FIRLHabitatSnapshotCodecTest::RunTest(const FString& Parameters)
{
    IRLHabitatNet::Frame Frame;
    Frame.Sequence = 1;
    Frame.Width = 32;
    Frame.Height = 32;
    TestTrue(TEXT("Valid bounded food cell"), IRLHabitatNet::AddFood(Frame,31,31));
    TestTrue(TEXT("Valid creature identity"), IRLHabitatNet::AddCreature(Frame,101,30,29));
    TestTrue(TEXT("Full valid frame"), IRLHabitatNet::Validate(Frame));
    TestTrue(TEXT("New frame accepted"), IRLHabitatNet::IsNewer(0,Frame));
    TestFalse(TEXT("Duplicate frame rejected"), IRLHabitatNet::IsNewer(1,Frame));

    int32 X=-1, Y=-1;
    int NativeX=0, NativeY=0;
    TestTrue(TEXT("Decode cell"), IRLHabitatNet::DecodeCell(32,32,Frame.CreatureCells[0],NativeX,NativeY));
    X=NativeX; Y=NativeY;
    TestEqual(TEXT("Creature X preserved"),X,30);
    TestEqual(TEXT("Creature Y preserved"),Y,29);
    TestFalse(TEXT("Out-of-bounds cells rejected"),IRLHabitatNet::AddFood(Frame,32,0));
    TestFalse(TEXT("Duplicate identity rejected"),IRLHabitatNet::AddCreature(Frame,101,0,0));

    Frame.FoodCells.push_back(1024);
    TestFalse(TEXT("Malformed frame rejected"), IRLHabitatNet::Validate(Frame));
    Frame.FoodCells.pop_back();
    TestTrue(TEXT("Repaired frame passes"), IRLHabitatNet::Validate(Frame));
    return true;
}
#endif
