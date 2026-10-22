#include "Visual/IRLLivingBiomeDetailActor.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"

AIRLLivingBiomeDetailActor::AIRLLivingBiomeDetailActor()
{
    PrimaryActorTick.bCanEverTick = false; // static instancing, not one tick per leaf
    bReplicates = false; // local decorative-only meshes, never authoritative bot state

    PatchRoot = CreateDefaultSubobject<USceneComponent>(TEXT("PatchRoot"));
    SetRootComponent(PatchRoot);
    GroundCoverInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("GroundCover"));
    StoneInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("StoneInstances"));
    LeafLitterInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("LeafLitter"));
    GroundCoverInstances->SetupAttachment(PatchRoot);
    StoneInstances->SetupAttachment(PatchRoot);
    LeafLitterInstances->SetupAttachment(PatchRoot);
    GroundCoverInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    StoneInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    LeafLitterInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GroundCoverInstances->SetCastShadow(false); // many tiny shadows cost GPU time
    LeafLitterInstances->SetCastShadow(false);
}

void AIRLLivingBiomeDetailActor::BeginPlay()
{
    Super::BeginPlay();
#if PLATFORM_ANDROID
    ApplyVisualTier(1); // device profile starts conservatively on Android
#else
    ApplyVisualTier(2); // desktop authoring preview
#endif
}

void AIRLLivingBiomeDetailActor::ApplyVisualTier(int32 NewTier)
{
    NewTier = FMath::Clamp(NewTier,0,2);
    if (LastTier == NewTier) { return; }
    LastTier = NewTier;
    Rebuild();
}

void AIRLLivingBiomeDetailActor::Rebuild()
{
    if (!GetWorld()) { return; }
    GroundCoverInstances->ClearInstances();
    StoneInstances->ClearInstances();
    LeafLitterInstances->ClearInstances();
    LastInstanceCount = 0;

    if (GroundCoverMesh) { GroundCoverInstances->SetStaticMesh(GroundCoverMesh); }
    if (StoneMesh) { StoneInstances->SetStaticMesh(StoneMesh); }
    if (LeafLitterMesh) { LeafLitterInstances->SetStaticMesh(LeafLitterMesh); }
    if (GroundCoverMaterial) { GroundCoverInstances->SetMaterial(0,GroundCoverMaterial); }
    if (StoneMaterial) { StoneInstances->SetMaterial(0,StoneMaterial); }
    if (LeafLitterMaterial) { LeafLitterInstances->SetMaterial(0,LeafLitterMaterial); }

    FRandomStream GroundRandom(Seed);
    FRandomStream StoneRandom(Seed ^ 0x1735);
    FRandomStream LitterRandom(Seed ^ 0x5e21);
    const int32 GroundCount[] = { 90, 230, 460 };
    const int32 StoneCount[] = { 20, 45, 75 };
    const int32 LitterCount[] = { 35, 90, 190 };
    Populate(GroundCoverInstances,GroundCount[LastTier],GroundRandom,
        0.60f,MinimumWalkableNormalZ,4000.0f);
    Populate(StoneInstances,StoneCount[LastTier],StoneRandom,
        0.25f,0.45f,11000.0f);
    Populate(LeafLitterInstances,LitterCount[LastTier],LitterRandom,
        0.25f,MinimumWalkableNormalZ,2200.0f);
}

void AIRLLivingBiomeDetailActor::Populate(UHierarchicalInstancedStaticMeshComponent* Instances,
    int32 Count, FRandomStream& Random, float BaseScale,
    float MaximumSlopeZ, float CullDistanceCm)
{
    if (!Instances || !Instances->GetStaticMesh() || !GetWorld()) { return; }
    Instances->SetCullDistances(300, static_cast<int32>(CullDistanceCm));
    const float Radius = FMath::Clamp(PatchRadiusCm,100.0f,5000.0f);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(IRLBiomeTrace),false,this);
    for (int32 I=0; I<Count; ++I)
    {
        const float Angle = Random.FRandRange(0.0f, UE_TWO_PI);
        const float Distance = FMath::Sqrt(Random.FRand()) * Radius;
        const FVector Origin = GetActorLocation() +
            FVector(FMath::Cos(Angle)*Distance,FMath::Sin(Angle)*Distance,0.0f);
        FHitResult Hit;
        const bool bGrounded = GetWorld()->LineTraceSingleByChannel(Hit,
            Origin + FVector(0,0,1500.0f),
            Origin - FVector(0,0,3000.0f),
            ECC_WorldStatic,Params);
        if (!bGrounded || Hit.ImpactNormal.Z < MaximumSlopeZ) { continue; }
        const FVector Local = GetActorTransform().InverseTransformPosition(Hit.ImpactPoint);
        const float Scale = BaseScale * Random.FRandRange(0.75f,1.30f);
        const FTransform Transform(FRotator(0,Random.FRandRange(0.0f,360.0f),0),
            Local,FVector(Scale));
        Instances->AddInstance(Transform);
        ++LastInstanceCount;
    }
}
