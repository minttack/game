// Native C++17 bounded control benchmark (synthetic, not a claim of general intelligence).
#include "../Source/IRL/Experience/IRLLifeLearningCore.h"
#include <cassert>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <random>
using namespace IRLLife;
constexpr double Rewards[4][3] = {
    {-0.3, 0.2, 0.9},
    { 0.9, 0.1, 0.2},
    {-0.9, 0.9,-0.1},
    {-0.7, 0.8,-0.4}
};

int main()
{
    ExperienceLearner Learner;
    std::mt19937_64 Random(20261021);
    double LearnerTotal = 0, FixedTotal = 0, RandomTotal = 0, OracleTotal = 0;
    constexpr int Cycles = 8000;
    for (int I = 0; I < Cycles; ++I)
    {
        const int Context = I % 4;
        Observation Obs{(Context & 1) != 0, (Context & 2) != 0};
        PredictionReceipt Prediction;
        assert(Learner.Propose(Obs, Prediction));
        const int ActionIndex = static_cast<int>(Prediction.ChosenAction);
        const double Actual = Rewards[Context][ActionIndex];
        assert(Learner.RecordObservedOutcome(Prediction, Actual, true));
        LearnerTotal += Actual;
        FixedTotal += Rewards[Context][0]; // static forage-only control
        RandomTotal += Rewards[Context][Random() % 3];
        double Oracle = Rewards[Context][0];
        for (int A = 1; A < 3; ++A)
        {
            if (Rewards[Context][A] > Oracle) { Oracle = Rewards[Context][A]; }
        }
        OracleTotal += Oracle;
    }

    std::cout << std::fixed << std::setprecision(4)
        << "sample_count=" << Cycles
        << " avg_bie=" << (LearnerTotal / Cycles)
        << " avg_fixed=" << (FixedTotal / Cycles)
        << " avg_uniform_random=" << (RandomTotal / Cycles)
        << " avg_oracle=" << (OracleTotal / Cycles)
        << " train_mse=" << Learner.TrainingPredictionMSE() << "\n";

    assert(LearnerTotal > FixedTotal + 1000.0);
    assert(LearnerTotal > RandomTotal + 1000.0);
}
