#include "Experience/IRLEcologyHabitatActor.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

AIRLEcologyHabitatActor::AIRLEcologyHabitatActor()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 1.0f; // explicitly bounded: one learning step per second
    // Visuals are local proxies, not replicated real-time ecology yet.
    bReplicates = false;

    HabitatRoot = CreateDefaultSubobject<USceneComponent>(TEXT("HabitatRoot"));
    RootComponent = HabitatRoot;
    CreatureVisuals = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("CreatureVisuals"));
    CreatureVisuals->SetupAttachment(HabitatRoot);
    CreatureVisuals->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    FoodVisuals = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("FoodVisuals"));
    FoodVisuals->SetupAttachment(HabitatRoot);
    FoodVisuals->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (Sphere.Succeeded())
    {
        CreatureVisuals->SetStaticMesh(Sphere.Object);
        FoodVisuals->SetStaticMesh(Sphere.Object);
    }
}

void AIRLEcologyHabitatActor::BeginPlay()
{
    Super::BeginPlay();
    if (!HasAuthority()) { return; }
    Runtime = MakeUnique<IRLEcology::Habitat>(
        FMath::Clamp(HabitatWidth,3,32),
        FMath::Clamp(HabitatHeight,3,32),
        static_cast<uint64>(DeterministicSeed));
    Runtime->SetMaxActive(40);
    const int32 W = FMath::Clamp(HabitatWidth,3,32);
    const int32 H = FMath::Clamp(HabitatHeight,3,32);

    // Visible finite resources, real depletion and regrowth. This is intentionally
    // a modest ecology test range, not a generated planet or biological evolution.
    for (int32 Y = 0; Y < H; ++Y)
    {
        for (int32 X = 0; X < W; ++X)
        {
            IRLEcology::Tile T;
            T.FoodCapacity = (X + 2 * Y) % 4 == 0 ? 3 : 0;
            T.Food = T.FoodCapacity;
            T.RegrowthTicks = T.FoodCapacity ? 3 : 0;
            T.Danger = ((3 * X + Y) % 11 == 0) ? 10 : 0;
            T.Shelter = ((X + 3 * Y) % 7 == 0);
            Runtime->SetTile(X,Y,T);
        }
    }
    for (int32 I = 0; I < FMath::Min(InitialPopulation,40); ++I)
    {
        Runtime->AddCreature((3 * I + 1) % W, (5 * I + 2) % H, 55);
    }
    RefreshVisuals();
}

void AIRLEcologyHabitatActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!HasAuthority() || !Runtime) { return; }

    Runtime->StepEveryone(IRLEcology::Policy::BIE);
    if (bAllowDescendants && Runtime->WorldTicks() % 15 == 0)
    {
        const auto& Residents = Runtime->Residents();
        for (const auto& C : Residents)
        {
            if (C.Alive && C.Energy >= 75)
            {
                const uint64 ParentId = C.Id; // no stale vector references after push_back
                Runtime->SpawnDescendant(ParentId,0.75);
                break;
            }
        }
    }
    RefreshVisuals();
}

int32 AIRLEcologyHabitatActor::TotalFoodConsumed() const
{
    return Runtime ? static_cast<int32>(FMath::Min<uint64>(Runtime->FoodConsumed(), MAX_int32)) : 0;
}

int32 AIRLEcologyHabitatActor::LivingCreatureCount() const
{
    if (!Runtime) { return 0; }
    int32 Count = 0;
    for (const auto& C : Runtime->Residents())
    {
        if (C.Alive) { ++Count; }
    }
    return Count;
}

int32 AIRLEcologyHabitatActor::ObservedExperienceCycles() const
{
    if (!Runtime) { return 0; }
    uint64 Cycles = 0;
    for (const auto& C : Runtime->Residents()) { Cycles += C.Experience.Cycles(); }
    return static_cast<int32>(FMath::Min<uint64>(Cycles, MAX_int32));
}

void AIRLEcologyHabitatActor::RefreshVisuals()
{
    if (!Runtime || !CreatureVisuals || !FoodVisuals) { return; }
    CreatureVisuals->ClearInstances();
    FoodVisuals->ClearInstances();
    const int32 W = FMath::Clamp(HabitatWidth,3,32);
    const int32 H = FMath::Clamp(HabitatHeight,3,32);
    const float CellCm = FMath::Clamp(GridCellSizeCm,100.0f,1000.0f);

    for (int32 Y = 0; Y < H; ++Y)
    {
        for (int32 X = 0; X < W; ++X)
        {
            if (Runtime->TileAt(X,Y).Food > 0)
            {
                const FVector P((X - W / 2) * CellCm,(Y - H / 2) * CellCm,30.0f);
                FoodVisuals->AddInstance(FTransform(FRotator::ZeroRotator,P,FVector(0.22f)));
            }
        }
    }

    for (const auto& C : Runtime->Residents())
    {
        if (!C.Alive) { continue; }
        const FVector P((C.X - W / 2) * CellCm,(C.Y - H / 2) * CellCm,70.0f);
        CreatureVisuals->AddInstance(FTransform(FRotator::ZeroRotator,P,FVector(0.42f)));
    }
}
