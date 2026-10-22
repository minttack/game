// IRL BIE Experience: compact, bounded visual snapshot codec, no LLM.
#pragma once
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <vector>

namespace IRLHabitatNet
{
constexpr std::uint8_t MaxSide = 32;
constexpr std::size_t MaxActiveVisuals = 40;
constexpr std::size_t MaxCellCount = MaxSide * MaxSide;
constexpr std::size_t MaxSnapshotBytes = 4096;

struct Frame
{
    std::uint32_t Sequence = 0;
    std::uint8_t Width = 0, Height = 0;
    float CellSizeCm = 200.0f;
    std::uint64_t CompletedExperienceCycles = 0;
    std::uint64_t FoodConsumed = 0;
    std::vector<std::uint16_t> FoodCells;
    std::vector<std::uint16_t> CreatureCells;
    std::vector<std::uint64_t> CreatureIds;
};

inline bool ValidDimensions(std::uint8_t Width, std::uint8_t Height)
{
    return Width >= 1 && Height >= 1 && Width <= MaxSide && Height <= MaxSide;
}

// Each 16-bit entry encodes a 2D cell within the declared rectangular habitat.
inline bool EncodeCell(std::uint8_t Width, std::uint8_t Height,
    int X, int Y, std::uint16_t& Out)
{
    if (!ValidDimensions(Width, Height) || X < 0 || Y < 0 ||
        X >= Width || Y >= Height) return false;
    Out = static_cast<std::uint16_t>(Y * Width + X);
    return true;
}

inline bool DecodeCell(std::uint8_t Width, std::uint8_t Height,
    std::uint16_t Packed, int& X, int& Y)
{
    if (!ValidDimensions(Width, Height) || Packed >= Width * Height)
        return false;
    X = static_cast<int>(Packed % Width);
    Y = static_cast<int>(Packed / Width);
    return true;
}

inline std::size_t EstimatedBytes(const Frame& F)
{
    // Conservative per-payload estimate, not an actual UE wire-byte measurement.
    constexpr std::size_t HeaderAllowance = 96;
    return HeaderAllowance + 2 * F.FoodCells.size() +
        2 * F.CreatureCells.size() + 8 * F.CreatureIds.size();
}

inline bool Validate(const Frame& F)
{
    if (F.Sequence == 0 || !ValidDimensions(F.Width, F.Height) ||
        !std::isfinite(F.CellSizeCm) ||
        F.CellSizeCm < 100.0f || F.CellSizeCm > 1000.0f ||
        F.FoodCells.size() > static_cast<std::size_t>(F.Width) * F.Height ||
        F.CreatureCells.size() > MaxActiveVisuals ||
        F.CreatureCells.size() != F.CreatureIds.size() ||
        EstimatedBytes(F) > MaxSnapshotBytes) return false;

    std::array<bool, MaxCellCount> SeenFood{};
    for (std::uint16_t Cell : F.FoodCells)
    {
        if (Cell >= F.Width * F.Height || SeenFood[Cell]) return false;
        SeenFood[Cell] = true;
    }
    for (std::size_t I = 0; I < F.CreatureCells.size(); ++I)
    {
        if (F.CreatureCells[I] >= F.Width * F.Height || F.CreatureIds[I] == 0)
            return false;
        for (std::size_t J = 0; J < I; ++J)
        {
            if (F.CreatureIds[J] == F.CreatureIds[I]) return false;
        }
    }
    return true;
}

inline bool AddFood(Frame& F, int X, int Y)
{
    std::uint16_t Cell;
    if (!EncodeCell(F.Width,F.Height,X,Y,Cell) ||
        F.FoodCells.size() >= MaxCellCount) return false;
    for (auto Existing : F.FoodCells)
        if (Existing == Cell) return false;
    F.FoodCells.push_back(Cell);
    return true;
}

inline bool AddCreature(Frame& F, std::uint64_t Id, int X, int Y)
{
    std::uint16_t Cell;
    if (Id == 0 || F.CreatureCells.size() >= MaxActiveVisuals ||
        !EncodeCell(F.Width,F.Height,X,Y,Cell)) return false;
    for (auto Existing : F.CreatureIds) if (Existing == Id) return false;
    F.CreatureIds.push_back(Id);
    F.CreatureCells.push_back(Cell);
    return true;
}

// Clients never apply stale frames, including duplicates from retries.
inline bool IsNewer(std::uint32_t LastSequence, const Frame& Incoming)
{
    return Validate(Incoming) && Incoming.Sequence > LastSequence;
}
