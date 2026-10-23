// BIE THRIVES Experience: bounded, local-only IRL mobile measurement kernel.
// PURE C++17: no LLM, networking, disk access, system clock or Unreal headers.
// Frame samples measure GAME/FRAME delta only. They are NOT GPU frame times.
#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace IRLMobileEvidence
{
enum class InputKind : std::uint8_t { MoveAxis, LookAxis, JumpPress, ExperiencePress };

struct Window
{
    std::uint32_t Frames = 0, Rejected = 0;
    std::uint32_t MoveAxes = 0, LookAxes = 0, Jumps = 0, Experiences = 0;
    double DurationSeconds = 0.0;
    double MeanMs = 0.0, P50Ms = 0.0, P95Ms = 0.0, P99Ms = 0.0, MaxMs = 0.0;
};

class Recorder
{
public:
    static constexpr std::size_t Capacity = 1024;
    void Reset()
    {
        Used = 0; Rejected = 0; Elapsed = 0.0;
        MoveCount = LookCount = JumpCount = ExperienceCount = 0;
    }
    void MarkInput(InputKind Kind)
    {
        // Count received joystick AXIS CALLBACKS, not fingers/taps.
        // This gives evidence that the bindings fire, not that movement works.
        switch (Kind)
        {
        case InputKind::MoveAxis:       if (MoveCount < UINT32_MAX) ++MoveCount; break;
        case InputKind::LookAxis:       if (LookCount < UINT32_MAX) ++LookCount; break;
        case InputKind::JumpPress:      if (JumpCount < UINT32_MAX) ++JumpCount; break;
        case InputKind::ExperiencePress:if (ExperienceCount < UINT32_MAX) ++ExperienceCount; break;
        }
    }
    bool Observe(double FrameSeconds, Window& Out)
    {
        if (!std::isfinite(FrameSeconds) || FrameSeconds <= 0.0 || FrameSeconds > 0.20)
        {
            if (Rejected < UINT32_MAX) ++Rejected;
            return false;
        }
        // 10s steady-state window, or earlier only if array capacity reached.
        Samples[Used++] = FrameSeconds * 1000.0;
        Elapsed += FrameSeconds;
        if (Elapsed + 1e-7 < 10.0 && Used < Capacity) return false;
        if (Used < 60)
        {
            Reset(); // never call a tiny interval a 10-second performance sample
            return false;
        }
        std::sort(Samples.begin(), Samples.begin() + Used);
        Window W{};
        W.Frames = static_cast<std::uint32_t>(Used);
        W.Rejected = Rejected;
        W.DurationSeconds = Elapsed;
        W.MoveAxes = MoveCount; W.LookAxes = LookCount;
        W.Jumps = JumpCount; W.Experiences = ExperienceCount;
        double Sum = 0.0;
        for (std::size_t I = 0; I < Used; ++I) Sum += Samples[I];
        W.MeanMs = Sum / static_cast<double>(Used);
        W.P50Ms = Quantile(0.50);
        W.P95Ms = Quantile(0.95);
        W.P99Ms = Quantile(0.99);
        W.MaxMs = Samples[Used-1];
        Out = W;
        Reset();
        return true;
    }
private:
    double Quantile(double Fraction) const
    {
        const std::size_t Index = std::max<std::size_t>(
            1, static_cast<std::size_t>(std::ceil(static_cast<double>(Used)*Fraction))) - 1;
        return Samples[Index];
    }
    std::array<double,Capacity> Samples{};
    std::size_t Used = 0;
    std::uint32_t Rejected = 0;
    std::uint32_t MoveCount = 0, LookCount = 0, JumpCount = 0, ExperienceCount = 0;
    double Elapsed = 0.0;
};
}
