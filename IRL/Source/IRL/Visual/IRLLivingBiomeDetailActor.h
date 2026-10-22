// IRL detail placement: original or licensed PBR meshes on phone-efficient HISM batches.
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IRLLivingBiomeDetailActor.generated.h"

class UHierarchicalInstancedStaticMeshComponent;
class USceneComponent;
class UStaticMesh;
class UMaterialInterface;

UCLASS(Blueprintable)
class IRL_API AIRLLivingBiomeDetailActor : public AActor
{
    GENERATED_BODY()
public:
    AIRLLivingBiomeDetailActor();
    virtual void BeginPlay() override;

    /** Local presentation quality; this actor does NOT alter physical food or
        BIE life outcomes. Can be driven by Android's BIE visual budget. */
    UFUNCTION(BlueprintCallable, Category="IRL|Visual Biome")
    void ApplyVisualTier(int32 NewTier);

    UFUNCTION(BlueprintPure, Category="IRL|Visual Biome")
    int32 LastGeneratedInstanceCount() const { return LastInstanceCount; }

protected:
    UPROPERTY(VisibleAnywhere, Category="IRL|Visual Biome")
    TObjectPtr<USceneComponent> PatchRoot;
    UPROPERTY(VisibleAnywhere, Category="IRL|Visual Biome")
    TObjectPtr<UHierarchicalInstancedStaticMeshComponent> GroundCoverInstances;
    UPROPERTY(VisibleAnywhere, Category="IRL|Visual Biome")
    TObjectPtr<UHierarchicalInstancedStaticMeshComponent> StoneInstances;
    UPROPERTY(VisibleAnywhere, Category="IRL|Visual Biome")
    TObjectPtr<UHierarchicalInstancedStaticMeshComponent> LeafLitterInstances;

    // Assign real, properly licensed PBR meshes/materials in the game editor.
    UPROPERTY(EditAnywhere, Category="IRL|Visual Biome|Assets")
    TObjectPtr<UStaticMesh> GroundCoverMesh;
    UPROPERTY(EditAnywhere, Category="IRL|Visual Biome|Assets")
    TObjectPtr<UStaticMesh> StoneMesh;
    UPROPERTY(EditAnywhere, Category="IRL|Visual Biome|Assets")
    TObjectPtr<UStaticMesh> LeafLitterMesh;
    UPROPERTY(EditAnywhere, Category="IRL|Visual Biome|Assets")
    TObjectPtr<UMaterialInterface> GroundCoverMaterial;
    UPROPERTY(EditAnywhere, Category="IRL|Visual Biome|Assets")
    TObjectPtr<UMaterialInterface> StoneMaterial;
    UPROPERTY(EditAnywhere, Category="IRL|Visual Biome|Assets")
    TObjectPtr<UMaterialInterface> LeafLitterMaterial;

    UPROPERTY(EditAnywhere, Category="IRL|Visual Biome|Distribution", meta=(ClampMin="100",ClampMax="5000"))
    float PatchRadiusCm = 2500.0f;
    UPROPERTY(EditAnywhere, Category="IRL|Visual Biome|Distribution")
    int32 Seed = 12121;
    UPROPERTY(EditAnywhere, Category="IRL|Visual Biome|Distribution", meta=(ClampMin="0.1",ClampMax="1.0"))
    float MinimumWalkableNormalZ = 0.70f;

private:
    int32 LastTier = INDEX_NONE;
    int32 LastInstanceCount = 0;
    void Rebuild();
    void Populate(UHierarchicalInstancedStaticMeshComponent* Instances,
        int32 Count, FRandomStream& Random, float BaseScale,
        float MaximumSlopeZ, float CullDistanceCm);
};
