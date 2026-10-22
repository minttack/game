#include "Experience/IRLEcologyHabitatActor.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
#include "Net/UnrealNetwork.h"

AIRLEcologyHabitatActor::AIRLEcologyHabitatActor()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 1.0f; // explicitly bounded: one learning step per second
    bReplicates = true;
    bReplicateMovement = false; // world-placed habitat stays at its placed transform
    bAlwaysRelevant = true;     // ONLY for the small duo pilot habitat
    NetUpdateFrequency = 2.0f;
    MinNetUpdateFrequency = 1.0f;

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
    CaptureVisualFrame();
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
    CaptureVisualFrame();
}

void AIRLEcologyHabitatActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AIRLEcologyHabitatActor, VisualFrame);
}

int32 AIRLEcologyHabitatActor::TotalFoodConsumed() const
{
    return static_cast<int32>(FMath::Min<int64>(
        VisualFrame.FoodConsumed, static_cast<int64>(MAX_int32)));
}

int32 AIRLEcologyHabitatActor::LivingCreatureCount() const
{
    return VisualFrame.CreatureCells.Num();
}

int32 AIRLEcologyHabitatActor::ObservedExperienceCycles() const
{
    return static_cast<int32>(FMath::Min<int64>(
        VisualFrame.CompletedExperienceCycles, static_cast<int64>(MAX_int32)));
}

bool AIRLEcologyHabitatActor::BuildNativeFrame(IRLHabitatNet::Frame& Out) const
{
    Out.Sequence = VisualFrame.Sequence;
    Out.Width = VisualFrame.Width;
    Out.Height = VisualFrame.Height;
    Out.CellSizeCm = VisualFrame.CellSizeCm;

    if (VisualFrame.CompletedExperienceCycles < 0 || VisualFrame.FoodConsumed < 0)
    {
        return false;
    }
    Out.CompletedExperienceCycles = static_cast<uint64>(VisualFrame.CompletedExperienceCycles);
    Out.FoodConsumed = static_cast<uint64>(VisualFrame.FoodConsumed);
    for (uint16 Cell : VisualFrame.FoodCells) Out.FoodCells.push_back(Cell);
    for (uint16 Cell : VisualFrame.CreatureCells) Out.CreatureCells.push_back(Cell);
    for (int64 Id : VisualFrame.CreatureIds)
    {
        if (Id <= 0) return false;
        Out.CreatureIds.push_back(static_cast<uint64>(Id));
    }
    return IRLHabitatNet::Validate(Out);
}

void AIRLEcologyHabitatActor::CaptureVisualFrame()
{
    if (!HasAuthority() || !Runtime) { return; }

    IRLHabitatNet::Frame Native;
    // 32-bit sequence wraps only after more than a century at 1 Hz.
    if (VisualFrame.Sequence == MAX_uint32) { return; }
    Native.Sequence = VisualFrame.Sequence + 1;
    Native.Width = static_cast<uint8>(FMath::Clamp(HabitatWidth,3,32));
    Native.Height = static_cast<uint8>(FMath::Clamp(HabitatHeight,3,32));
    Native.CellSizeCm = FMath::Clamp(GridCellSizeCm,100.0f,1000.0f);
    Native.FoodConsumed = Runtime->FoodConsumed();
    for (const auto& Creature : Runtime->Residents())
    {
        Native.CompletedExperienceCycles += Creature.Experience.Cycles();
        if (Creature.Alive && !IRLHabitatNet::AddCreature(
            Native,Creature.Id,Creature.X,Creature.Y))
        {
            UE_LOG(LogTemp,Error,TEXT("IRL habitat: active creature count or cell out of snapshot bounds"));
            return;
        }
    }

    for (int32 Y=0;Y<Native.Height;++Y)
    {
        for (int32 X=0;X<Native.Width;++X)
        {
            if (Runtime->TileAt(X,Y).Food > 0 &&
                !IRLHabitatNet::AddFood(Native,X,Y))
            {
                UE_LOG(LogTemp,Error,TEXT("IRL habitat: invalid food cell"));
                return;
            }
        }
    }

    if (!IRLHabitatNet::Validate(Native) ||
        Native.CompletedExperienceCycles > static_cast<uint64>(MAX_int64) ||
        Native.FoodConsumed > static_cast<uint64>(MAX_int64))
    {
        UE_LOG(LogTemp,Error,TEXT("IRL habitat: snapshot validation failure"));
        return;
    }

    VisualFrame.Sequence = Native.Sequence;
    VisualFrame.Width = Native.Width;
    VisualFrame.Height = Native.Height;
    VisualFrame.CellSizeCm = Native.CellSizeCm;
    VisualFrame.CompletedExperienceCycles = static_cast<int64>(Native.CompletedExperienceCycles);
    VisualFrame.FoodConsumed = static_cast<int64>(Native.FoodConsumed);
    VisualFrame.FoodCells.Reset();
    VisualFrame.CreatureCells.Reset();
    VisualFrame.CreatureIds.Reset();
    for (uint16 Cell : Native.FoodCells) VisualFrame.FoodCells.Add(Cell);
    for (uint16 Cell : Native.CreatureCells) VisualFrame.CreatureCells.Add(Cell);
    for (uint64 Id : Native.CreatureIds) VisualFrame.CreatureIds.Add(static_cast<int64>(Id));

    // RepNotifies run on receiving clients, not automatically on the server.
    LastAppliedSequence = Native.Sequence;
    if (GetNetMode() != NM_DedicatedServer) RefreshVisuals(Native);
    ForceNetUpdate();
}

void AIRLEcologyHabitatActor::OnRep_VisualFrame()
{
    IRLHabitatNet::Frame Native;
    if (!BuildNativeFrame(Native) ||
        !IRLHabitatNet::IsNewer(LastAppliedSequence,Native))
    {
        return; // never render invalid/duplicate/stale network state
    }
    LastAppliedSequence = Native.Sequence;
    RefreshVisuals(Native);
}

void AIRLEcologyHabitatActor::RefreshVisuals(const IRLHabitatNet::Frame& Frame)
{
    if (!CreatureVisuals || !FoodVisuals || !IRLHabitatNet::Validate(Frame)) return;

    CreatureVisuals->ClearInstances();
    FoodVisuals->ClearInstances();
    const float CellCm = Frame.CellSizeCm;
    const int32 W = Frame.Width, H = Frame.Height;

    for (uint16 Packed : Frame.FoodCells)
    {
        int X=0,Y=0;
        if (!IRLHabitatNet::DecodeCell(Frame.Width,Frame.Height,Packed,X,Y)) return;
        const FVector P((X - W / 2) * CellCm,(Y - H / 2) * CellCm,30.0f);
        FoodVisuals->AddInstance(FTransform(FRotator::ZeroRotator,P,FVector(0.22f)));
    }
    for (uint16 Packed : Frame.CreatureCells)
    {
        int X=0,Y=0;
        if (!IRLHabitatNet::DecodeCell(Frame.Width,Frame.Height,Packed,X,Y)) return;
        const FVector P((X - W / 2) * CellCm,(Y - H / 2) * CellCm,70.0f);
        CreatureVisuals->AddInstance(FTransform(FRotator::ZeroRotator,P,FVector(0.42f)));
    }
}
