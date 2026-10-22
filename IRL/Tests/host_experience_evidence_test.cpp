#include "../Source/IRL/Experience/IRLExperienceEvidenceCore.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
using IRLEvidence::Ledger;

int main()
{
    Ledger L;
    std::uint32_t Token = 0;
    assert(L.ReportedCount() == 0);
    assert(!L.Predict(std::numeric_limits<double>::quiet_NaN(), 41, Token));
    assert(!L.Predict(1.1, 41, Token));
    assert(!L.Predict(0.5, 0, Token));
    assert(!L.ReportOutcome(1, 41, 0.2));
    assert(L.Predict(0.75, 41, Token));
    const auto First = Token;
    assert(L.ReportedCount() == 0);
    assert(!L.Predict(0.2, 41, Token));
    assert(!L.ReportOutcome(First, 99, 0.5));
    assert(!L.ReportOutcome(First+1, 41, 0.5));
    assert(!L.ReportOutcome(First, 41, std::numeric_limits<double>::infinity()));
    assert(!L.ReportOutcome(First, 41, -1.01));
    assert(L.ReportedCount() == 0);
    assert(L.ReportOutcome(First, 41, 0.25));
    assert(!L.ReportOutcome(First, 41, 0.25));
    assert(L.ReportedCount() == 1);
    assert(std::abs(L.MeanSquaredPredictionError() - 0.25) < 1e-12);
    assert(L.Outcomes().at(0).TrialId == First);
    assert(L.Outcomes().at(0).SourceTag == 41);
    assert(L.Outcomes().at(0).Observation == 0.25);
    assert(L.Predict(-0.5, 41, Token));
    assert(L.ReportOutcome(Token, 41, -0.5));
    assert(L.ReportedCount() == 2);
    assert(std::abs(L.MeanSquaredPredictionError() - 0.125) < 1e-12);
    assert(L.Predict(0.5, 41, Token));
    const auto PendingOld = Token;
    L.ResetObjective();
    assert(!L.HasPendingTrial());
    assert(L.ReportedCount() == 0);
    assert(!L.ReportOutcome(PendingOld, 41, 0.5));
    assert(L.Predict(0.7, 41, Token));
    assert(Token > PendingOld);
    assert(L.ReportOutcome(Token, 41, 0.6));
    L.ResetObjective();
    for(int i=0; i<static_cast<int>(Ledger::MaxOutcomes); ++i)
    {
        assert(L.Predict(0.25, 44, Token));
        assert(L.ReportOutcome(Token, 44, 0.5));
    }
    assert(L.ReportedCount() == Ledger::MaxOutcomes);
    assert(!L.Predict(0.25, 44, Token));
    assert(std::abs(L.MeanSquaredPredictionError() - 0.0625) < 1e-12);
    std::cout << "PASS evidence ledger: invalid values, source mismatch, replay, predict-first, reset, metrics, 1024-outcome cap\n";
}
