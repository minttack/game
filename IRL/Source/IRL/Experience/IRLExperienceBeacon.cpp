// Copyright Epic Games, Inc. All Rights Reserved.

#include "Experience/IRLExperienceBeacon.h"

#include "Camera/PlayerCameraManager.h"
#include "Components/PointLightComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Experience/IRLExperienceSubsystem.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "UObject/ConstructorHelpers.h"

AIRLExperienceBeacon::AIRLExperienceBeacon()
{
	PrimaryActorTick.bCanEverTick = true;

	TriggerSphere = CreateDefaultSubobject<USphereComponent>(TEXT("TriggerSphere"));
	SetRootComponent(TriggerSphere);
	TriggerSphere->InitSphereRadius(170.0f);
	TriggerSphere->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	TriggerSphere->SetCollisionResponseToAllChannels(ECR_Ignore);
	TriggerSphere->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);

	SignalMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SignalMesh"));
	SignalMesh->SetupAttachment(TriggerSphere);
	SignalMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	SignalMesh->SetRelativeScale3D(FVector(0.55f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> ConeMesh(TEXT("/Engine/BasicShapes/Cone.Cone"));
	if (SphereMesh.Succeeded())
	{
		SignalMesh->SetStaticMesh(SphereMesh.Object);
	}

	for (int32 Index = 0; Index < 5; ++Index)
	{
		UStaticMeshComponent* Petal = CreateDefaultSubobject<UStaticMeshComponent>(
			*FString::Printf(TEXT("MotionPetal%d"), Index));
		Petal->SetupAttachment(TriggerSphere);
		Petal->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Petal->SetRelativeScale3D(FVector(0.13f, 0.13f, 0.28f));
		Petal->SetVisibility(false);
		if (SphereMesh.Succeeded())
		{
			Petal->SetStaticMesh(SphereMesh.Object);
		}
		MotionPetals.Add(Petal);
	}

	for (int32 Index = 0; Index < 8; ++Index)
	{
		UStaticMeshComponent* Mote = CreateDefaultSubobject<UStaticMeshComponent>(
			*FString::Printf(TEXT("MagicMote%d"), Index));
		Mote->SetupAttachment(TriggerSphere);
		Mote->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Mote->SetRelativeScale3D(FVector(0.28f));
		Mote->SetVisibility(false);
		if (SphereMesh.Succeeded())
		{
			Mote->SetStaticMesh(SphereMesh.Object);
		}
		MagicMotes.Add(Mote);

		UPointLightComponent* MoteLight = CreateDefaultSubobject<UPointLightComponent>(
			*FString::Printf(TEXT("MagicLight%d"), Index));
		MoteLight->SetupAttachment(Mote);
		MoteLight->SetIntensity(6000.0f);
		MoteLight->SetAttenuationRadius(520.0f);
		MoteLight->SetCastShadows(false);
		MoteLight->SetVisibility(false);
		MagicLights.Add(MoteLight);
	}

	for (int32 Index = 0; Index < 12; ++Index)
	{
		UStaticMeshComponent* Shard = CreateDefaultSubobject<UStaticMeshComponent>(
			*FString::Printf(TEXT("PortalShard%d"), Index));
		Shard->SetupAttachment(TriggerSphere);
		Shard->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Shard->SetRelativeScale3D(FVector(0.18f, 0.18f, 0.72f));
		Shard->SetVisibility(false);
		if (ConeMesh.Succeeded())
		{
			Shard->SetStaticMesh(ConeMesh.Object);
		}
		PortalShards.Add(Shard);
	}

	SignalLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("SignalLight"));
	SignalLight->SetupAttachment(SignalMesh);
	SignalLight->SetLightColor(FLinearColor(0.08f, 0.42f, 1.0f));
	SignalLight->SetIntensity(9000.0f);
	SignalLight->SetAttenuationRadius(850.0f);
	SignalLight->SetCastShadows(false);

	InstructionText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("InstructionText"));
	InstructionText->SetupAttachment(TriggerSphere);
	InstructionText->SetRelativeLocation(FVector(0.0f, 0.0f, 145.0f));
	InstructionText->SetHorizontalAlignment(EHTA_Center);
	InstructionText->SetWorldSize(30.0f);
	InstructionText->SetTextRenderColor(FColor(115, 196, 255));
	InstructionText->SetText(FText::FromString(TEXT("THE FIRST SIGNAL\nAPPROACH TO BEGIN")));
}

void AIRLExperienceBeacon::BeginPlay()
{
	Super::BeginPlay();
	TriggerSphere->OnComponentBeginOverlap.AddDynamic(this, &AIRLExperienceBeacon::HandleBeginOverlap);

	if (UGameInstance* GameInstance = GetGameInstance())
	{
		if (UIRLExperienceSubsystem* Experience = GameInstance->GetSubsystem<UIRLExperienceSubsystem>())
		{
			Experience->OnExperienceAdvanced.AddUniqueDynamic(this, &AIRLExperienceBeacon::HandleExperienceAdvanced);
			Experience->OnExperienceCompleted.AddUniqueDynamic(this, &AIRLExperienceBeacon::HandleExperienceCompleted);
		}
	}
}

void AIRLExperienceBeacon::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	RunningTime += DeltaSeconds;
	const float Wave = (FMath::Sin(RunningTime * PulseSpeed * UE_TWO_PI) + 1.0f) * 0.5f;
	const float Scale = 0.55f * (1.0f + Wave * PulseAmplitude);
	SignalMesh->SetRelativeScale3D(FVector(Scale));
	SignalLight->SetIntensity(FMath::Lerp(6500.0f, 11000.0f, Wave));

	if (bMotionBloomReady || bMotionBloomActive)
	{
		for (int32 Index = 0; Index < MotionPetals.Num(); ++Index)
		{
			const float Angle = RunningTime * (bMotionBloomActive ? 1.8f : 0.8f)
				+ (UE_TWO_PI * static_cast<float>(Index) / MotionPetals.Num());
			const float Radius = 115.0f + 18.0f * FMath::Sin(RunningTime * 1.4f + Index);
			const float Height = 35.0f * FMath::Sin(Angle * 2.0f);
			MotionPetals[Index]->SetRelativeLocation(FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, Height));
			MotionPetals[Index]->SetRelativeRotation(FRotator(0.0f, FMath::RadiansToDegrees(Angle), 25.0f));
		}
	}

	if (bResonanceReady || bResonanceActive)
	{
		const float PhaseEnergy = 1.0f + static_cast<float>(CurrentPhase) * 0.16f;
		for (int32 Index = 0; Index < MagicMotes.Num(); ++Index)
		{
			const float Strand = Index % 2 == 0 ? 1.0f : -1.0f;
			const float Angle = RunningTime * PhaseEnergy * Strand + Index * (UE_PI / 2.0f);
			const float Radius = (205.0f + 32.0f * FMath::Sin(RunningTime * 0.7f)) * PhaseEnergy;
			const float Height = -45.0f + Index * 48.0f + 42.0f * FMath::Sin(Angle * 0.5f);
			const float MoteScale = 0.24f + 0.10f * (0.5f + 0.5f * FMath::Sin(Angle * 2.0f));
			MagicMotes[Index]->SetRelativeLocation(FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, Height));
			MagicMotes[Index]->SetRelativeScale3D(FVector(MoteScale));
			MagicLights[Index]->SetIntensity(4200.0f + 4800.0f * (0.5f + 0.5f * FMath::Sin(Angle * 2.0f)));
		}

		for (int32 Index = 0; Index < PortalShards.Num(); ++Index)
		{
			const float CrownAngle = UE_TWO_PI * static_cast<float>(Index) / PortalShards.Num()
				+ RunningTime * 0.22f * PhaseEnergy;
			const float CrownRadius = 265.0f + 30.0f * FMath::Sin(RunningTime + Index * 0.6f);
			PortalShards[Index]->SetRelativeLocation(FVector(
				20.0f * FMath::Sin(CrownAngle * 3.0f),
				FMath::Cos(CrownAngle) * CrownRadius,
				260.0f + FMath::Sin(CrownAngle) * CrownRadius));
			PortalShards[Index]->SetRelativeRotation(FRotator(
				FMath::RadiansToDegrees(CrownAngle),
				RunningTime * 35.0f,
				90.0f));
		}
	}

	if (InstructionText && GetWorld() && GetWorld()->GetFirstPlayerController())
	{
		const FVector CameraLocation = GetWorld()->GetFirstPlayerController()->PlayerCameraManager
			? GetWorld()->GetFirstPlayerController()->PlayerCameraManager->GetCameraLocation()
			: GetActorLocation();
		const FRotator FaceCamera = (CameraLocation - InstructionText->GetComponentLocation()).Rotation();
		InstructionText->SetWorldRotation(FRotator(0.0f, FaceCamera.Yaw, 0.0f));
	}
}

void AIRLExperienceBeacon::HandleBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComponent, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	APawn* Pawn = Cast<APawn>(OtherActor);
	if (bObjectiveStarted || !Pawn || !GetGameInstance())
	{
		return;
	}

	if (UIRLExperienceSubsystem* Experience = GetGameInstance()->GetSubsystem<UIRLExperienceSubsystem>())
	{
		if (APlayerController* PlayerController = Cast<APlayerController>(Pawn->GetController()))
		{
			EnableInput(PlayerController);
			if (InputComponent)
			{
				InputComponent->BindKey(EKeys::E, IE_Pressed, this, &AIRLExperienceBeacon::AdvanceExperience);
			}
		}

		bObjectiveStarted = Experience->BeginDefaultObjective();
		if (bObjectiveStarted)
		{
			TriggerSphere->SetGenerateOverlapEvents(false);
		}
	}
}

void AIRLExperienceBeacon::AdvanceExperience()
{
	if (UGameInstance* GameInstance = GetGameInstance())
	{
		if (UIRLExperienceSubsystem* Experience = GameInstance->GetSubsystem<UIRLExperienceSubsystem>())
		{
			if (bResonanceReady)
			{
				bResonanceReady = false;
				bResonanceActive = Experience->BeginResonanceGardenObjective();
			}
			else if (bMotionBloomReady)
			{
				bMotionBloomReady = false;
				bMotionBloomActive = Experience->BeginMotionBloomObjective();
			}
			else
			{
				Experience->AdvanceExperience();
			}
		}
	}
}

void AIRLExperienceBeacon::HandleExperienceAdvanced(EIRLExperiencePhase Phase, const FText& BlueGuidance,
	const FText& BIEStatement)
{
	CurrentPhase = Phase;
	const UEnum* PhaseEnum = StaticEnum<EIRLExperiencePhase>();
	const FText PhaseName = PhaseEnum
		? PhaseEnum->GetDisplayNameTextByValue(static_cast<int64>(Phase))
		: FText::FromString(TEXT("Experience"));
	const FText Prompt = Phase == EIRLExperiencePhase::Complete
		? FText::FromString(TEXT("OBJECTIVE COMPLETE"))
		: FText::FromString(TEXT("PRESS E FOR NEXT PHASE"));

	InstructionText->SetText(FText::Format(
		FText::FromString(TEXT("{0}\n{1}")),
		PhaseName.ToUpper(),
		Prompt));
}

void AIRLExperienceBeacon::HandleExperienceCompleted(FName ObjectiveId)
{
	if (ObjectiveId == TEXT("FirstSignal"))
	{
		bMotionBloomReady = true;
		for (UStaticMeshComponent* Petal : MotionPetals)
		{
			Petal->SetVisibility(true);
		}
		SignalLight->SetLightColor(FLinearColor(0.72f, 0.18f, 1.0f));
		InstructionText->SetText(FText::FromString(TEXT("MOTION BLOOM AWAKENED\nPRESS E TO BEGIN")));
		return;
	}

	if (ObjectiveId == TEXT("MotionBloom"))
	{
		bMotionBloomActive = false;
		bResonanceReady = true;
		for (int32 Index = 0; Index < MagicMotes.Num(); ++Index)
		{
			MagicMotes[Index]->SetVisibility(true);
			MagicLights[Index]->SetVisibility(true);
			MagicLights[Index]->SetLightColor(FLinearColor::MakeFromHSV8(static_cast<uint8>(Index * 31), 220, 255));
		}
		for (UStaticMeshComponent* Shard : PortalShards)
		{
			Shard->SetVisibility(true);
		}
		SignalLight->SetLightColor(FLinearColor(1.0f, 0.16f, 0.72f));
		InstructionText->SetText(FText::FromString(TEXT("RESONANCE GARDEN OPEN\nPRESS E TO ENTER")));
		return;
	}

	bResonanceActive = false;
	SignalLight->SetLightColor(FLinearColor(1.0f, 0.78f, 0.18f));
	InstructionText->SetText(FText::FromString(TEXT("RESONANCE GARDEN\nHARMONIZED")));
}
