// Copyright (c) IRL project contributors. Non-LLM BIE Experience learning kernel.
#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>

namespace IRLLife
{
enum class Action : std::uint8_t { Forage = 0, Shelter = 1, Explore = 2 };
constexpr std::size_t ActionCount = 3;
constexpr std::size_t ContextCount = 4;

struct Observation
{
    bool FoodNearby = false;
    bool ThreatNearby = false;

    std::size_t Context() const
    {
        return (FoodNearby ? 1u : 0u) | (ThreatNearby ? 2u : 0u);
    }
};

struct PredictionReceipt
{
    std::uint64_t Sequence = 0;
    std::size_t Context = 0;
    Action ChosenAction = Action::Forage;
    double PredictedReward = 0.0;
    bool Valid = false;
};

struct ActionEvidence
{
    std::uint64_t ObservedTrials = 0;
    double EstimatedReward = 0.0;
    double InheritedPrior = 0.0;
};

// No LLM, no network, no invented observation. The game world MUST deliver the
// measured outcome after executing the selected action. All rewards are [-1, 1].
class ExperienceLearner
{
public:
    bool Propose(const Observation& ObservationNow, PredictionReceipt& Out)
    {
        if (!Alive || AwaitingOutcome)
        {
            return false;
        }

        const std::size_t Context = ObservationNow.Context();
        const std::size_t Choice = SelectAction(Context);
        const ActionEvidence& Evidence = Table[Context][Choice];
        Pending.Sequence = NextSequence++;
        Pending.Context = Context;
        Pending.ChosenAction = static_cast<Action>(Choice);
        Pending.PredictedReward = Evidence.ObservedTrials
            ? Evidence.EstimatedReward : Evidence.InheritedPrior;
        Pending.Valid = true;
        AwaitingOutcome = true;
        Out = Pending;
        return true;
    }

    bool RecordObservedOutcome(const PredictionReceipt& Receipt,
        double ActualNormalizedReward, bool DidSurvive)
    {
        if (!AwaitingOutcome || !Pending.Valid || !Receipt.Valid ||
            Receipt.Sequence != Pending.Sequence ||
            Receipt.Context != Pending.Context ||
            Receipt.ChosenAction != Pending.ChosenAction ||
            Receipt.PredictedReward != Pending.PredictedReward ||
            !std::isfinite(ActualNormalizedReward) ||
            ActualNormalizedReward < -1.0 || ActualNormalizedReward > 1.0)
        {
            return false;
        }

        ActionEvidence& Evidence = Table[Pending.Context]
            [static_cast<std::size_t>(Pending.ChosenAction)];
        const double Error = ActualNormalizedReward - Pending.PredictedReward;

        // Recency-sensitive evidence allows correction after conditions change.
        // ObservedTrials is lifetime feedback count; EstimatedReward is an EMA.
        if (Evidence.ObservedTrials == 0)
        {
            Evidence.EstimatedReward = ActualNormalizedReward;
        }
        else
        {
            Evidence.EstimatedReward += 0.10 * (ActualNormalizedReward - Evidence.EstimatedReward);
        }
        ++Evidence.ObservedTrials;
        ++CompletedCycles;
        if (DidSurvive) { ++SurvivedCycles; }
        RewardSum += ActualNormalizedReward;
        SquaredPredictionError += Error * Error;

        Alive = DidSurvive;
        AwaitingOutcome = false;
        Pending.Valid = false;
        return true;
    }

    Action BestEvidenceAction(const Observation& ObservationNow) const
    {
        const auto& Evidence = Table[ObservationNow.Context()];
        std::size_t Best = 0;
        double BestEstimate = Evidence[0].ObservedTrials
            ? Evidence[0].EstimatedReward : Evidence[0].InheritedPrior;
        for (std::size_t I = 1; I < ActionCount; ++I)
        {
            const double Estimate = Evidence[I].ObservedTrials
                ? Evidence[I].EstimatedReward : Evidence[I].InheritedPrior;
            if (Estimate > BestEstimate)
            {
                BestEstimate = Estimate;
                Best = I;
            }
        }
        return static_cast<Action>(Best);
    }

    std::uint64_t Trials(const Observation& Obs, Action Which) const
    {
        return Table[Obs.Context()][static_cast<std::size_t>(Which)].ObservedTrials;
    }

    double PredictedReward(const Observation& Obs, Action Which) const
    {
        const auto& E = Table[Obs.Context()][static_cast<std::size_t>(Which)];
        return E.ObservedTrials ? E.EstimatedReward : E.InheritedPrior;
    }

    std::uint64_t Cycles() const { return CompletedCycles; }
    std::uint64_t SuccessfulSurvivalSteps() const { return SurvivedCycles; }
    bool IsAlive() const { return Alive; }
    bool HasPendingOutcome() const { return AwaitingOutcome; }
    std::uint32_t Generation() const { return GenerationNumber; }
    double AverageReward() const
    {
        return CompletedCycles ? RewardSum / static_cast<double>(CompletedCycles) : 0.0;
    }
    double TrainingPredictionMSE() const
    {
        return CompletedCycles
            ? SquaredPredictionError / static_cast<double>(CompletedCycles) : 0.0;
    }

    // Descendants inherit tentative policy biases, NOT fictitious observations.
    // Their own trial counts and verified survival start at zero.
    ExperienceLearner SpawnNextGeneration(double PriorRetention) const
    {
        ExperienceLearner Child;
        if (!std::isfinite(PriorRetention)) { PriorRetention = 0.0; }
        PriorRetention = std::max(0.0, std::min(1.0, PriorRetention));
        Child.GenerationNumber = GenerationNumber + 1;
        for (std::size_t C = 0; C < ContextCount; ++C)
        {
            for (std::size_t A = 0; A < ActionCount; ++A)
            {
                const ActionEvidence& Source = Table[C][A];
                Child.Table[C][A].InheritedPrior = PriorRetention *
                    (Source.ObservedTrials ? Source.EstimatedReward : Source.InheritedPrior);
            }
        }
        return Child;
    }

private:
    std::array<std::array<ActionEvidence, ActionCount>, ContextCount> Table{};
    PredictionReceipt Pending{};
    std::uint64_t NextSequence = 1;
    std::uint64_t CompletedCycles = 0;
    std::uint64_t SurvivedCycles = 0;
    std::uint32_t GenerationNumber = 0;
    double RewardSum = 0.0;
    double SquaredPredictionError = 0.0;
    bool Alive = true;
    bool AwaitingOutcome = false;

    std::size_t SelectAction(std::size_t Context) const
    {
        const auto& Evidence = Table[Context];
        std::uint64_t Total = 0;
        for (const auto& E : Evidence) { Total += E.ObservedTrials; }

        // Sample each action at least once in every newly observed context.
        for (std::size_t A = 0; A < ActionCount; ++A)
        {
            if (Evidence[A].ObservedTrials == 0) { return A; }
        }

        std::size_t Best = 0;
        double BestScore = -std::numeric_limits<double>::infinity();
        for (std::size_t A = 0; A < ActionCount; ++A)
        {
            // Upper confidence exploration: learning remains revisable.
            const double Bonus = 0.35 * std::sqrt(
                std::log(static_cast<double>(Total) + 1.0) /
                static_cast<double>(Evidence[A].ObservedTrials));
            const double Score = Evidence[A].EstimatedReward + Bonus;
            if (Score > BestScore)
            {
                BestScore = Score;
                Best = A;
            }
        }
        return Best;
    }
};

struct PopulationBudget
{
    std::uint64_t RepresentedPopulation = 0;
    std::uint64_t IndividuallyActive = 0;
    std::uint64_t AggregatedOnly = 0;

    static PopulationBudget Plan(std::uint64_t Total, std::uint64_t ActiveLimit)
    {
        PopulationBudget Result;
        Result.RepresentedPopulation = Total;
        Result.IndividuallyActive = std::min(Total, ActiveLimit);
        Result.AggregatedOnly = Total - Result.IndividuallyActive;
        return Result;
    }
    bool CountsConserved() const
    {
        return IndividuallyActive <= RepresentedPopulation &&
            AggregatedOnly == RepresentedPopulation - IndividuallyActive;
    }
};
} // namespace IRLLife
