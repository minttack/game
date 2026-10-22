// IRL native 3D display for a finite BIE ecology habitat.
// Editor-placeable actor, no embedded LLM, no change to existing First Signal.
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Experience/IRLEcologyCore.h"
#include "Experience/IRLHabitatSnapshotCore.h"
#include "IRLEcologyHabitatActor.generated.h"

class USceneComponent;
class UInstancedStaticMeshComponent;

/** Single replicated visual snapshot. The server alone runs BIE life decisions. */
USTRUCT()
struct FIRLHabitatVisualFrame
{
    GENERATED_BODY()

    UPROPERTY() uint32 Sequence = 0;
    UPROPERTY() uint8 Width = 0;
    UPROPERTY() uint8 Height = 0;
    UPROPERTY() float CellSizeCm = 200.0f;
    UPROPERTY() int64 CompletedExperienceCycles = 0;
    UPROPERTY() int64 FoodConsumed = 0;
    UPROPERTY() TArray<uint16> FoodCells;
    UPROPERTY() TArray<uint16> CreatureCells;
    UPROPERTY() TArray<int64> CreatureIds;
};

/** Small, independently simulated ecosystem visible inside the existing IRL world. */
UCLASS(Blueprintable)
class IRL_API AIRLEcologyHabitatActor : public AActor
{
    GENERATED_BODY()
public:
    AIRLEcologyHabitatActor();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UFUNCTION(BlueprintPure, Category="IRL|BIE Habitat")
    int32 LivingCreatureCount() const;

    UFUNCTION(BlueprintPure, Category="IRL|BIE Habitat")
    int32 ObservedExperienceCycles() const;

    UFUNCTION(BlueprintPure, Category="IRL|BIE Habitat")
    int32 TotalFoodConsumed() const;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="IRL|BIE Habitat")
    TObjectPtr<USceneComponent> HabitatRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="IRL|BIE Habitat")
    TObjectPtr<UInstancedStaticMeshComponent> CreatureVisuals;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="IRL|BIE Habitat")
    TObjectPtr<UInstancedStaticMeshComponent> FoodVisuals;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="IRL|BIE Habitat", meta=(ClampMin="3",ClampMax="32"))
    int32 HabitatWidth = 12;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="IRL|BIE Habitat", meta=(ClampMin="3",ClampMax="32"))
    int32 HabitatHeight = 12;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="IRL|BIE Habitat", meta=(ClampMin="1",ClampMax="40"))
    int32 InitialPopulation = 10;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="IRL|BIE Habitat", meta=(ClampMin="100",ClampMax="1000"))
    float GridCellSizeCm = 200.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="IRL|BIE Habitat")
    int32 DeterministicSeed = 12345;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="IRL|BIE Habitat")
    bool bAllowDescendants = true;

private:
    // This actor is relevant for BOTH players in a single controlled habitat.
    // Do not set all large-world ecosystems to globally relevant.
    UPROPERTY(ReplicatedUsing=OnRep_VisualFrame)
    FIRLHabitatVisualFrame VisualFrame;

    UFUNCTION()
    void OnRep_VisualFrame();

    TUniquePtr<IRLEcology::Habitat> Runtime; // server only
    uint32 LastAppliedSequence = 0;
    bool BuildNativeFrame(IRLHabitatNet::Frame& Out) const;
    void CaptureVisualFrame();                 // server only
    void RefreshVisuals(const IRLHabitatNet::Frame& Frame);
};
