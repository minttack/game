// Source of truth for game-space coordinates. No invented extra dimensions.
#pragma once
#include <cmath>
#include <cstdint>

namespace IRLWorldScale
{
constexpr double UnrealUnitsPerMeter = 100.0; // 1 UE unit is 1 cm
constexpr double SectorWidthMeters = 10000.0;  // 10 km simulation sector
constexpr double BaselineHumanHeightMeters = 1.75;
constexpr double EarthReferenceRadiusMeters = 6371000.0; // reference, not an actual planet

struct AxisLocation
{
    std::int64_t Sector = 0;
    double LocalMeters = 0.0;
};

inline AxisLocation MakeAxis(double GlobalMeters)
{
    const double Index = std::floor(GlobalMeters / SectorWidthMeters);
    const auto Sector = static_cast<std::int64_t>(Index);
    return { Sector, GlobalMeters - static_cast<double>(Sector) * SectorWidthMeters };
}

struct Position3D
{
    AxisLocation X, Y, Z;
};

inline Position3D FromMeters(double X, double Y, double Z)
{
    return { MakeAxis(X), MakeAxis(Y), MakeAxis(Z) };
}

inline double ToMeters(const AxisLocation& Axis)
{
    return static_cast<double>(Axis.Sector) * SectorWidthMeters + Axis.LocalMeters;
}

inline double MetersToUE(double Meters) { return Meters * UnrealUnitsPerMeter; }
inline double UEToMeters(double UnrealUnits) { return UnrealUnits / UnrealUnitsPerMeter; }
}
