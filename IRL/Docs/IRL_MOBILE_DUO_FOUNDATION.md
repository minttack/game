# IRL Mobile Duo — first integration candidate (source only)

## The ONE intended game

Modify the existing `IRL/IRL.uproject` Unreal Engine 5.8 project; never treat this patch as a replacement game. Preserve all accepted creator decisions, especially individual autonomy and a shared living universe. The original First Signal, Motion Bloom and Resonance Garden experience loop stays intact.

## Target design, not yet implemented

Two human players join the same persistent starting planet in different regions. Both can independently explore and eventually reunite. All non-player creatures and civilizations use native BIE THRIVES-style observe/predict/act/compare/correct loops, not embedded language models. Ecological evolution, civilization, spaceships and an optional god-scale camera/mode are future milestones, not features in this patch.

## Implementation added here

1. Existing server `AIRLGameMode` refuses a third incoming human via `PreLogin`, while AI controllers do not use human slots.
2. First person uses normal PlayerStart. Second uses an existing distinct PlayerStart (minimum horizontal distance 12 m) or probes ground collision for a new safe-looking PlayerStart. Preferred starting distance 500 m, configurable on the GameMode class. If ground cannot be found, logs an explicit error and falls back to standard spawn; separated locations are NOT guaranteed in an unsuitable level.
3. Existing player keeps their assigned start across respawn on the same controller, and assignment is removed on logout.
4. Android-only baseline uses 30 FPS, ~80% rendering scale and reduced high-end rendering features; desktop settings are untouched. Real on-device profiling is required and platform CVar overrides must be verified.
5. `IRL.World.DuoSpawnRules` editor automation test checks two-human admission and minimum horizontal separation. Existing `IRL.Experience.FirstSignalLifecycle` test remains.

## To make this playable

- **Verify active GameMode parent.** DefaultEngine.ini points to `/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode`, not directly to the modified C++ class. Open that blueprint in UE 5.8 and verify its parent is `AIRLGameMode`. World Settings GameMode Override or `?game=` can supersede defaults. Reparent as needed after review. If the active GameMode is unrelated, these rules WILL NOT run.
- Make a persistent shared planet/level and put at least two grounded, non-obstructed PlayerStart actors **500 m or more** apart. For a real planet, author spawn territories explicitly; the temporary ray-trace fallback is not full navigation validation.
- Build/run the editor automation test. PIE test Listen Server + 2 clients, third-user rejection, respawn, reconnection, traversing between starting areas, original Experience beacon progression, and replication. Inspect errors.
- Set up Unreal Android toolchain through **Platforms → SDK Management → Android → Install SDK**, compile, preview mobile renderer, package and run on TWO Android phones, and measure frame time, memory, thermals and ping. Official UE 5.8 reference: https://dev.epicgames.com/documentation/en-us/unreal-engine/android-quick-start .
- Build actual multiplayer join/invites/server discovery and persistent server state. The code patch does not provide lobbies, internet hosting or match persistence.
- Advance BIE native NPC behavior only after implementing measurable predictions, outcomes, baseline controls and independent tests. Keep BIE separate from LLMs and avoid claims of autonomous learning until demonstrated.

## Verification status

Native policy checks can be compiled with a minimal host stub; **UE 5.8 C++ compilation, Unreal automation tests, Android APK/AAB packaging, two-client world gameplay and on-device FPS tests remain NOT RUN** in this environment. No merge to main without these gates. This is a feature-branch proposal, not a finished or released mobile game.
