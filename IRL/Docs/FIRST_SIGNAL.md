# IRL: The First Signal

The First Signal is IRL's first playable vertical slice. It adds a luminous signal near the first Player Start in the default Third Person map.

## Player loop

1. Play the default Third Person map.
2. Approach the blue signal to begin the objective.
3. Press **E** to move through Objective, Observe, Bloom, Test, Resolve, and Complete.
4. Read Blue's method guidance and BIE's bounded interpretation in the on-screen client messages.
5. Complete First Signal to awaken **Motion Bloom**, then press **E** to investigate motion through orbit, oscillation, impact, constraint, and feedback.

Blue guides *how to reason*. BIE states *what the current evidence supports*. Neither silently chooses for the player.

## Unreal verification

After pulling this change on the Windows machine, right-click `IRL.uproject`, generate project files if Unreal requests it, then open the project and allow Unreal to compile the `IRL` module. Press Play in the default Third Person level.

The automated lifecycle test is named `IRL.Experience.FirstSignalLifecycle` and can be run from Unreal's Session Frontend Automation tab.
