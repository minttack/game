// IRL native 3D display for a finite BIE ecology habitat.
// Editor-placeable actor, no embedded LLM, no change to existing First Signal.
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Experience/IRLEcologyCore.h"
#include "IRLEcologyHabitatActor.generated.h"

class USceneComponent;
class UInstancedStaticMeshComponent;

/** Small, independently simulated ecosystem visible inside the existing IRL world. */
UCLASS(Blueprintable)
class IRL_API AIRLEcologyHabitatActor : public AActor
{
    GENERATED_BODY()
public:
    AIRLEcologyHabitatActor();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UFUNCTION(BlueprintPure, Category="IRL|BIE Habitat")
    int32 LivingCreatureCount() const;

    UFUNCTION(BlueprintPure, Category="IRL|BIE Habitat")
    int32 ObservedExperienceCycles() const;

    UFUNCTION(BlueprintPure, Category="IRL|BIE Habitat")
    int32 TotalFoodConsumed() const { return FoodConsumed; }

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
    TUniquePtr<IRLEcology::Habitat> Runtime;
    int32 FoodConsumed = 0;
    void RefreshVisuals();
};
