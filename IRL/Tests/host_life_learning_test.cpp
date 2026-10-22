// Compile outside Unreal: g++ -std=c++17 -O2 -Wall -Wextra -pedantic host_life_learning_test.cpp -o life-test
#include "../Source/IRL/Experience/IRLLifeLearningCore.h"
#include "../Source/IRL/World/IRLWorldScale.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>

using namespace IRLLife;
constexpr double Rewards[4][3] = {
    {-0.3, 0.2, 0.9}, // no resources, no threat
    { 0.9, 0.1, 0.2}, // resources, safe
    {-0.9, 0.9,-0.1}, // no resources, threat
    {-0.7, 0.8,-0.4}  // resources, threat
};

int main()
{
    int Checks = 0;
    for (int C = 0; C < 4; ++C)
    {
        ExperienceLearner Learner;
        const Observation Obs{(C & 1) != 0, (C & 2) != 0};
        const Action Optimal = static_cast<Action>((C == 0) ? 2 : (C == 1 ? 0 : 1));
        int LateCorrect = 0;
        for (int I = 0; I < 1000; ++I)
        {
            PredictionReceipt P;
            assert(Learner.Propose(Obs, P));
            const auto A = static_cast<std::size_t>(P.ChosenAction);
            if (I >= 750 && P.ChosenAction == Optimal) { ++LateCorrect; }
            assert(Learner.RecordObservedOutcome(P, Rewards[C][A], true));
        }
        assert(Learner.Cycles() == 1000);
        assert(Learner.BestEvidenceAction(Obs) == Optimal);
        assert(LateCorrect >= 215); // >=86% during last quarter
        ++Checks;
    }

    {
        ExperienceLearner L;
        const Observation O{true, false};
        PredictionReceipt P;
        assert(L.Propose(O, P));
        assert(!L.Propose(O, P));
        assert(L.Cycles() == 0);
        PredictionReceipt Invalid = P;
        ++Invalid.Sequence;
        assert(!L.RecordObservedOutcome(Invalid, 0.5, true));
        assert(!L.RecordObservedOutcome(P, std::numeric_limits<double>::quiet_NaN(), true));
        assert(!L.RecordObservedOutcome(P, 1.1, true));
        assert(L.Cycles() == 0);
        assert(L.RecordObservedOutcome(P, 0.8, true));
        assert(!L.RecordObservedOutcome(P, 0.8, true));
        assert(L.Cycles() == 1);
        ++Checks;

        auto Child = L.SpawnNextGeneration(0.8);
        assert(Child.Generation() == 1);
        assert(Child.Cycles() == 0);
        assert(Child.Trials(O, Action::Forage) == 0);
        assert(std::abs(Child.PredictedReward(O, Action::Forage) - 0.64) < 1e-9);
        ++Checks;
    }

    {
        ExperienceLearner L;
        const Observation O{false, true};
        PredictionReceipt P;
        assert(L.Propose(O,P));
        assert(L.RecordObservedOutcome(P, -1, false));
        assert(!L.IsAlive());
        assert(!L.Propose(O,P));
        ++Checks;
    }

    {
        ExperienceLearner L;
        const Observation O{true, false};
        int LateShelter = 0;
        // Test changed conditions: threat makes forage suddenly fail.
        for (int I = 0; I < 2000; ++I)
        {
            PredictionReceipt P;
            assert(L.Propose(O,P));
            const double Reward = I < 1000
                ? (P.ChosenAction == Action::Forage ? 0.9 : (P.ChosenAction == Action::Shelter ? 0.1 : 0.2))
                : (P.ChosenAction == Action::Shelter ? 0.9 : (P.ChosenAction == Action::Forage ? -0.9 : -0.1));
            if (I >= 1900 && P.ChosenAction == Action::Shelter) { ++LateShelter; }
            assert(L.RecordObservedOutcome(P, Reward, true));
        }
        assert(L.BestEvidenceAction(O) == Action::Shelter);
        assert(LateShelter >= 80);
        ++Checks;
    }

    {
        const auto B = PopulationBudget::Plan(1000000000000ULL, 2000);
        assert(B.IndividuallyActive == 2000);
        assert(B.AggregatedOnly == 999999998000ULL);
        assert(B.CountsConserved());
        assert(PopulationBudget::Plan(0,2000).CountsConserved());
        assert(PopulationBudget::Plan(std::numeric_limits<std::uint64_t>::max(),2000).CountsConserved());
        assert(!PopulationBudget{10,11,0}.CountsConserved());
        ++Checks;
    }

    {
        using namespace IRLWorldScale;
        assert(MetersToUE(1.75) == 175.0);
        const auto P = FromMeters(6371000.0, -12345.0, 345.0);
        assert(P.X.Sector == 637);
        assert(std::abs(ToMeters(P.X) - 6371000.0) < 1e-7);
        assert(P.Y.Sector == -2);
        assert(std::abs(ToMeters(P.Y) + 12345.0) < 1e-7);
        assert(std::abs(UEToMeters(MetersToUE(123.5)) - 123.5) < 1e-10);
        ++Checks;
    }
    std::cout << "PASS: " << Checks << " independent host test groups; 4000 steady learning steps and 2000 shift steps\n";
    return 0;
}
