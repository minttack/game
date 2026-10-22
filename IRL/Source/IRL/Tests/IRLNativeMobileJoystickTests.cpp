#if WITH_DEV_AUTOMATION_TESTS
#include "Mobile/IRLMobileJoystickCore.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FIRLNativeJoystickMath,
    "IRL.Mobile.JoystickMath",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FIRLNativeJoystickMath::RunTest(const FString& Parameters)
{
    using namespace IRLMobile;
    const Axis2D Idle = FilterJoystick(0.05f,0.08f);
    TestTrue(TEXT("Small finger jitter is discarded"),Idle.X==0.0f && Idle.Y==0.0f);

    const Axis2D Full = FilterJoystick(1.0f,1.0f);
    TestTrue(TEXT("Diagonal speed is bounded"),
        FMath::Abs(std::sqrt(Full.X*Full.X+Full.Y*Full.Y)-1.0f)<0.002f);

    const Axis2D Opposite = FilterJoystick(-1.0f,-1.0f);
    TestTrue(TEXT("Negative stick direction is preserved"),
        Opposite.X<0.0f && Opposite.Y<0.0f);

    const Axis2D Invalid = FilterJoystick(std::numeric_limits<float>::infinity(),0.0f);
    TestTrue(TEXT("Nonfinite touch samples cannot move the avatar"),
        Invalid.X==0.0f && Invalid.Y==0.0f);
    return true;
}
#endif
