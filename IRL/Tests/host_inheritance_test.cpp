// Native C++17 evidence: inherited preferences affect offspring actions without false observations.
#include "../Source/IRL/Experience/IRLLifeLearningCore.h"
#include <cassert>
#include <iostream>
using namespace IRLLife;

int main()
{
    ExperienceLearner Parent;
    Observation Threat{true, true};
    for (int I = 0; I < 500; ++I)
    {
        PredictionReceipt P;
        assert(Parent.Propose(Threat, P));
        const double Reward = P.ChosenAction == Action::Shelter ? 0.95 : -0.6;
        assert(Parent.RecordObservedOutcome(P, Reward, true));
    }
    assert(Parent.BestEvidenceAction(Threat) == Action::Shelter);

    ExperienceLearner Child = Parent.SpawnNextGeneration(0.75);
    assert(Child.Generation() == 1);
    assert(Child.Cycles() == 0);
    assert(Child.Trials(Threat, Action::Shelter) == 0);
    PredictionReceipt First;
    assert(Child.Propose(Threat, First));
    assert(First.ChosenAction == Action::Shelter);
    assert(First.PredictedReward > 0.6);
    assert(Child.Cycles() == 0);
    assert(Child.RecordObservedOutcome(First, 0.9, true));
    assert(Child.Cycles() == 1);

    std::cout << "PASS: inherited tentative prior guides first action without fake observations\n";
}
