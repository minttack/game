// Copyright Epic Games, Inc. All Rights Reserved.

#include "Experience/IRLExperienceBeacon.h"

#include "Camera/PlayerCameraManager.h"
#include "Components/PointLightComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/World.h"
#include "Experience/IRLExperienceSubsystem.h"
#include "GameFramework/Pawn.h"
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
	if (SphereMesh.Succeeded())
	{
		SignalMesh->SetStaticMesh(SphereMesh.Object);
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
}

void AIRLExperienceBeacon::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	RunningTime += DeltaSeconds;
	const float Wave = (FMath::Sin(RunningTime * PulseSpeed * UE_TWO_PI) + 1.0f) * 0.5f;
	const float Scale = 0.55f * (1.0f + Wave * PulseAmplitude);
	SignalMesh->SetRelativeScale3D(FVector(Scale));
	SignalLight->SetIntensity(FMath::Lerp(6500.0f, 11000.0f, Wave));

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
	if (bObjectiveStarted || !Cast<APawn>(OtherActor) || !GetGameInstance())
	{
		return;
	}

	if (UIRLExperienceSubsystem* Experience = GetGameInstance()->GetSubsystem<UIRLExperienceSubsystem>())
	{
		bObjectiveStarted = Experience->BeginDefaultObjective();
		if (bObjectiveStarted)
		{
			InstructionText->SetText(FText::FromString(TEXT("SIGNAL RECEIVED\nPRESS E TO ADVANCE")));
			TriggerSphere->SetGenerateOverlapEvents(false);
		}
	}
}
