// IRL / BIE Experience: observable, bounded mobile visual-quality adaptation.
// Independent C++17 policy. No language model. Frame time is NOT GPU time.
#pragma once
#include <cmath>
#include <cstdint>

namespace IRLVisual
{
enum class Tier : std::uint8_t { Economy = 0, Balanced = 1, Detail = 2 };
enum class Reason : std::uint8_t { None = 0, SustainedSlow = 1, SustainedHeadroom = 2 };
struct Decision
{
    Tier Selected = Tier::Balanced;
    Reason Cause = Reason::None;
    double MeanFrameMs = 0.0;
    std::uint32_t ValidFrames = 0;
    std::uint64_t ObservationWindow = 0;
    bool Changed = false;
};
class BudgetController
{
public:
    void Reset(Tier Start = Tier::Balanced, double TargetFPS = 30.0)
    {
        Selected = Start;
        TargetFrameMs = std::isfinite(TargetFPS) && TargetFPS >= 20.0 && TargetFPS <= 120.0 ? 1000.0 / TargetFPS : 1000.0 / 30.0;
        WindowSeconds = 0.0;
        SampleCount = 0;
        ConsecutiveSlow = ConsecutiveFast = CooldownWindows = 0;
        Windows = RejectedFrames = 0;
        LastMeanFrameMs = 0.0;
    }
    // Called with actual game-thread frame delta. Return true ONLY when a whole
    // observation window has closed, never on an individual frame spike.
    bool Observe(double FrameSeconds, Decision& Out)
    {
        if (!std::isfinite(FrameSeconds) || FrameSeconds <= 0.0 || FrameSeconds > 0.20)
        {
            ++RejectedFrames; // loading, pause or corrupt sample; not hidden
            return false;
        }
        WindowSeconds += FrameSeconds;
        ++SampleCount;
        if (WindowSeconds < 2.0 || SampleCount < 15)
            return false;

        ++Windows;
        const double Mean = (WindowSeconds * 1000.0) / static_cast<double>(SampleCount);
        LastMeanFrameMs = Mean;
        Out = Decision{};
        Out.Selected = Selected;
        Out.MeanFrameMs = Mean;
        Out.ValidFrames = SampleCount;
        Out.ObservationWindow = Windows;
        WindowSeconds = 0.0;
        SampleCount = 0;

        // Initial renderer/shader loading is not a fair steady-state benchmark.
        if (Windows <= 3)
        {
            ConsecutiveSlow = ConsecutiveFast = 0;
            return true;
        }
        if (CooldownWindows > 0)
        {
            --CooldownWindows;
            ConsecutiveSlow = ConsecutiveFast = 0;
            return true;
        }
        if (Mean > TargetFrameMs * 1.16)
        {
            ++ConsecutiveSlow; ConsecutiveFast = 0;
        }
        else if (Mean < TargetFrameMs * 0.82)
        {
            ++ConsecutiveFast; ConsecutiveSlow = 0;
        }
        else
        {
            ConsecutiveSlow = ConsecutiveFast = 0;
        }
        if (ConsecutiveSlow >= 2 && Selected != Tier::Economy)
        {
            Selected = static_cast<Tier>(static_cast<int>(Selected) - 1);
            Out.Cause = Reason::SustainedSlow; Out.Changed = true;
        }
        else if (ConsecutiveFast >= 6 && Selected != Tier::Detail)
        {
            Selected = static_cast<Tier>(static_cast<int>(Selected) + 1);
            Out.Cause = Reason::SustainedHeadroom; Out.Changed = true;
        }
        if (Out.Changed)
        {
            CooldownWindows = 3;
            ConsecutiveSlow = ConsecutiveFast = 0;
            Out.Selected = Selected;
        }
        return true;
    }
    Tier CurrentTier() const { return Selected; }
    double LastWindowMeanMs() const { return LastMeanFrameMs; }
    std::uint64_t TotalWindows() const { return Windows; }
    std::uint64_t RejectedSamples() const { return RejectedFrames; }
private:
    Tier Selected = Tier::Balanced;
    double TargetFrameMs = 1000.0 / 30.0;
    double WindowSeconds = 0.0;
    double LastMeanFrameMs = 0.0;
    std::uint32_t SampleCount = 0, ConsecutiveSlow = 0, ConsecutiveFast = 0, CooldownWindows = 0;
    std::uint64_t Windows = 0, RejectedFrames = 0;
};
}
