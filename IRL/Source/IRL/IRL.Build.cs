// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class IRL : ModuleRules
{
	public IRL(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"IRL",
			"IRL/Variant_Platforming",
			"IRL/Variant_Platforming/Animation",
			"IRL/Variant_Combat",
			"IRL/Variant_Combat/AI",
			"IRL/Variant_Combat/Animation",
			"IRL/Variant_Combat/Gameplay",
			"IRL/Variant_Combat/Interfaces",
			"IRL/Variant_Combat/UI",
			"IRL/Variant_SideScrolling",
			"IRL/Variant_SideScrolling/AI",
			"IRL/Variant_SideScrolling/Gameplay",
			"IRL/Variant_SideScrolling/Interfaces",
			"IRL/Variant_SideScrolling/UI"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
