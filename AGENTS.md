# IRL — One Authoritative Game (Antigravity / Coding Agents)

This repository, `minttack/game`, contains the **one** IRL Unreal Engine 5.8 game in `IRL/IRL.uproject`. This file is always-on project guidance for external developer assistants such as Google Antigravity. It is **not** executable BIE THRIVES Experience code.

## Non-negotiable continuity
- NEVER create or replace IRL with an independent game, starter template, Unity app, HTML/WebGL demo, or new repository.
- Read `IRL/IRL.uproject`, `IRL/Docs/`, current `git status`, `git log`, and open GitHub feature PRs before changing code. `main` is not automatically ahead of a tested feature branch.
- Work in a named isolated feature branch or Git worktree. Do not rebase/force-push another worker, overwrite binary `.uasset` files, silently commit generated Unreal `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, APKs, device serials or secrets. Ask before merging and before destructive operations.
- Creator Decisions 001–030 remain controlling, particularly **026** coexistence of individual freedom and collective autonomy/player guidance, **029** minimal restrictions consistent with essential security/safety, **030** highest demonstrable capability. Do not invent missing ledger text; inspect available PR records. Preserve prior creator decisions.
- **BIE THRIVES Experience must remain an independent, standalone NON-LLM runtime.** A coding agent may externally author/test C++ or Python and operate Unreal Editor, but no language model, Antigravity API or ChatGPT runs *inside* BIE/IRL simulation as its intelligence.
- Android/Moto G is the priority: ARM64, landscape native Unreal 5.8, actual touch movement, real APK and measured phone resource usage. Preserve original PC behavior. The approved realistic artwork is **CONCEPT ART**, not current game graphics.

## Current critical integration gate
1. Inspect this branch's existing `IRL/Tools/Visual/IRL_BUILD_ANDROID_APK_WINDOWS.bat`, `IRL/Tools/Visual/irl_android_apk_runner.py`, `IRL/Tools/Visual/audit_android_class_chain.py`, and Android renderer/source-gate tools.
2. Use the **existing** Unreal 5.8 project and locally installed toolchain. Fix *the first authentic build error* in IRL code. Compile `IRLEditor`, inspect real Blueprint inheritance and PIE, then RunUAT Android ASTC Development packaging. Do not claim success because a source/mock CI test passed.
3. When UE Editor is running, Unreal MCP tools may inspect/edit the editor; use an MCP endpoint on `127.0.0.1` only and retain Ask/approval permissions for scene mutations. Save the original map; prefer a cloned isolated validation level. Never enable remote MCP exposure.
4. Require logs and real `.apk` metadata/hash, then real **authorized** Moto G installation/launch, left/right joystick, Jump/Experience, FPS p95/p99, memory, thermals, and crashes before calling a feature device-tested.
5. Do not auto-install apps, auto-upload releases, modify billing/settings, publish credentials or make network requests using user accounts without explicit approval.

## Evidence vocabulary
`proposed` -> `source implemented` -> `host-tested` -> `UE compiled` -> `editor/PIE tested` -> `APK packaged` -> `physical Moto G tested` -> `integrated` -> `released`. Never skip a rung.

## Required report after each session
Record actual branch+commit, changed files, exact tests and pass/fail output, untouched dependencies, known missing evidence, and smallest next action in a dated `IRL/Docs/` record or proposed update to the canonical shared master ledger. Do not state the shared master records were updated unless they were actually written and checked.

## First active task
**Get a real Unreal Engine 5.8 Android Development APK of this exact IRL project**, not another source-only benchmark. Use the Antigravity/Unreal MCP setup documented at `IRL/Tools/Antigravity/README.md`. If UE 5.8 or Android SDK is unavailable, record the precise blocker and implement the smallest verified code-level fix; no fabricated build.
