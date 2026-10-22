#if WITH_DEV_AUTOMATION_TESTS

#include "World/IRLDuoSpawnRules.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FIRLDuoSpawnRulesTest,
	"IRL.World.DuoSpawnRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FIRLDuoSpawnRulesTest::RunTest(const FString& Parameters)
{
	TestTrue(TEXT("An empty duo has a free slot"), IRLDuoSpawnRules::HasOpenSlot(0));
	TestTrue(TEXT("One human can be joined"), IRLDuoSpawnRules::HasOpenSlot(1));
	TestFalse(TEXT("Two humans fill the duo"), IRLDuoSpawnRules::HasOpenSlot(2));
	TestFalse(TEXT("Negative count cannot grant admission"), IRLDuoSpawnRules::HasOpenSlot(-1));
	TestFalse(TEXT("Same ground position at different altitude is not distinct"),
		IRLDuoSpawnRules::IsDistinctLocation(FVector(0, 0, 0), FVector(0, 0, 5000)));
	TestFalse(TEXT("Near points are not distinct"),
		IRLDuoSpawnRules::IsDistinctLocation(FVector(0, 0, 0), FVector(1000, 0, 0)));
	TestTrue(TEXT("Separated points are distinct"),
		IRLDuoSpawnRules::IsDistinctLocation(FVector(0, 0, 0), FVector(1800, 0, 0)));
	return true;
}

#endif
