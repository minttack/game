// IRL / BIE Experience: bounded, non-LLM prediction/outcome evidence ledger.
// This records *reported* outcomes. Only trusted game-world code can establish
// whether a report corresponds to an actually observed event.
#pragma once

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace IRLEvidence
{
struct Outcome
{
    std::uint32_t TrialId = 0;
    std::uint32_t SourceTag = 0;
    double Prediction = 0.0;
    double Observation = 0.0;
    double SquaredError = 0.0;
};

class Ledger
{
public:
    static constexpr std::size_t MaxOutcomes = 1024;

    bool Predict(double Expected, std::uint32_t SourceTag, std::uint32_t& OutTrialId)
    {
        if (Pending || !std::isfinite(Expected) || Expected < -1.0 || Expected > 1.0 ||
            SourceTag == 0 || Recorded.size() >= MaxOutcomes || NextTrialId == 0)
        {
            return false;
        }
        CurrentTrialId = NextTrialId++;
        CurrentPrediction = Expected;
        CurrentSource = SourceTag;
        Pending = true;
        OutTrialId = CurrentTrialId;
        return true;
    }

    bool ReportOutcome(std::uint32_t TrialId, std::uint32_t SourceTag, double Actual)
    {
        if (!Pending || TrialId == 0 || TrialId != CurrentTrialId ||
            SourceTag != CurrentSource || !std::isfinite(Actual) ||
            Actual < -1.0 || Actual > 1.0 || Recorded.size() >= MaxOutcomes)
        {
            return false;
        }
        const double Error = Actual - CurrentPrediction;
        Recorded.push_back({ CurrentTrialId, CurrentSource, CurrentPrediction,
            Actual, Error * Error });
        TotalSquaredError += Error * Error;
        Pending = false;
        CurrentTrialId = 0;
        CurrentSource = 0;
        return true;
    }

    // New objective means no carried-over evidence. Keep IDs monotonic so stale
    // tokens cannot be replayed into subsequent objectives.
    void ResetObjective()
    {
        Pending = false;
        CurrentTrialId = 0;
        CurrentSource = 0;
        CurrentPrediction = 0.0;
        Recorded.clear();
        TotalSquaredError = 0.0;
    }

    std::size_t ReportedCount() const { return Recorded.size(); }
    bool HasPendingTrial() const { return Pending; }
    const std::vector<Outcome>& Outcomes() const { return Recorded; }
    double MeanSquaredPredictionError() const
    {
        return Recorded.empty() ? 0.0 : TotalSquaredError / static_cast<double>(Recorded.size());
    }

private:
    std::uint32_t NextTrialId = 1;
    std::uint32_t CurrentTrialId = 0;
    std::uint32_t CurrentSource = 0;
    double CurrentPrediction = 0.0;
    double TotalSquaredError = 0.0;
    bool Pending = false;
    std::vector<Outcome> Recorded;
};
}
