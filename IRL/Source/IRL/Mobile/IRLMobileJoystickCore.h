// IRL phone-only joystick safety: deterministic, independent non-LLM input filter.
// No Unreal includes so behavior is verifiable in a native C++17 host build.
#pragma once
#include <cmath>

namespace IRLMobile
{
struct Axis2D { float X=0.0f; float Y=0.0f; };
inline Axis2D FilterJoystick(float X,float Y,float Deadzone=0.12f)
{
    if (!std::isfinite(X) || !std::isfinite(Y) ||
        !std::isfinite(Deadzone) || Deadzone<0.0f || Deadzone>=1.0f)
        return {};
    const float SizeSquared=X*X+Y*Y;
    if (!std::isfinite(SizeSquared) || SizeSquared<=Deadzone*Deadzone)
        return {};
    const float Length=std::sqrt(SizeSquared);
    const float UnitX=X/Length, UnitY=Y/Length;
    // Preserve analog control; remap radial dead-zone without diagonal boosts.
    const float Remapped=std::fmin(1.0f,(Length-Deadzone)/(1.0f-Deadzone));
    return {UnitX*Remapped,UnitY*Remapped};
}
}
