# IRL / BIE Life-Learning Lab — development & test record

**Authoritative codebase:** https://github.com/minttack/game, Unreal Engine 5.8, default `main` base commit `261cbbbb8264dfde6943cd0fa304029d4867dd3e`.
**Candidate branch:** `workers/irl-life-evolution-lab-20261022` (unmerged; no overwrite of original IRL).
**Parallel dependency:** Draft duo/mobile PR #1. This branch only adds new source and tests; any merge must refresh main and reconcile tests.
**Creator direction:** exactly two human players in the same persistent starting world, many autonomous non-LLM BIE Experience inhabitants, physically realistic 3D scale, eventual evolution, spaceflight, god mode. Decisions 026, 029 and 030 preserved.

## Actual code added
- `IRLLifeLearningCore.h`: four observable states, three decisions; pre-action prediction receipt; externally supplied bounded outcome; recency-sensitive estimate; confidence-driven exploration; failed/survived recording; death stops future cycles.
- Descendant learns with tentative inherited priors (prior influences first decision) and **zero** inherited/claimed observed trials.
- Exact 64-bit large population *representation* and bounded individually active budget. Summarized population is not falsely called a trillion learning minds.
- `UIRLLifeExperienceComponent` Blueprint adapter, server-only calls; cannot run cycles unless game events supply sensing, actions and outcomes.
- `IRLWorldScale.h`: physically based centimeter/meter conversions and double-precision 10-km sector coordinates for X/Y/Z. No rendered planet is created by this header.

## Fresh host verification
Environment: local Linux, g++ 14.2.0 with `-std=c++17 -O2 -Wall -Wextra -pedantic`. The tested pure learning kernel byte-matched committed Git blob `3fde783ee3546c16b34e28f49744aa6553254d55`. Tests used source-mirrored local harnesses, not an Unreal Engine toolchain.

- **10 host functional groups PASS:** four steady-context policy tests (1000 feedback cycles each), feedback rejection and no-learning-without-receipt, offspring reset, death handling, changing-survival-reward test (2000 cycles), trillion-scale arithmetic and centimeter/sector conversion.
- Last 250 decisions in each of four deterministic environments chose the best action **250/250**; not an independent evaluation on unseen real-world game environments.
- In shifted-reward test, last 100 decisions chose newly best shelter behavior **100/100**. The reward function was deterministic and hand-built.
- **Additional inheritance test PASS:** 500 parent feedback cycles, child first selects shelter given 75% inherited prior, while child observation count remains zero until its own outcome.
- **8000-cycle bounded baseline comparison** (four synthetic contexts, fixed seed uniform random baseline): average normalized reward BIE **0.8736**, fixed forage **-0.2500**, uniform random **0.1383**, oracle **0.8750**; training prediction MSE **0.0006**. Results demonstrate the elementary policy can learn these simple reward tables, **not** better general-purpose intelligence or actual biological evolution.
- Unreal automation test `IRL.Experience.LifeLearningEvidence` was authored, **NOT run**. Original First Signal regression also **NOT rerun** in Unreal. Mobile compilation, graphics profiling, live networking, 2-phone test, persistent world and large-population benchmark: **NOT RUN**.

## What still needs implementation
1. Attach life-learning components to real NPC types in the shared IRL world; add physical senses, action effects and validated survival feedback. This is not automatic in the source candidate yet.
2. Persistent journals, source/time/uncertainty metadata, holdout evaluations, negative-transfer checks and promotion gates (BIE independent engine compatibility review required).
3. **Actual multi-resolution ecology**: individuals near players, then real active regional groups, then population cohorts with exact counts, simulation fidelity labels and server load measurement. A count of a trillion does not imply a trillion individually computed agents.
4. Reproduction/genetics beyond a policy prior; generation selection, mutations, ecological causality and biological plausibility.
5. Author/prototype actual realistic 3D planet geometry in Unreal (measured actor scale, material/light reference, physics, atmosphere) and measure on Android hardware. Source coordinate constants do not equal photorealistic gameplay.
6. Integrate with draft duo PR, authority, saves, deterministic replay, and god-mode camera without overwriting another worker.
7. Compare against standard contextual bandits, strong reinforcement-learning and heuristic baselines with unseen seeds and environment shifts. The initial fixed/random controls are weak.

## Reproduce quick source tests
```bash
cd IRL/Tests
g++ -std=c++17 -O2 -Wall -Wextra -pedantic host_life_learning_test.cpp -o /tmp/irl-learning
g++ -std=c++17 -O2 -Wall -Wextra -pedantic host_inheritance_test.cpp -o /tmp/irl-inheritance
g++ -std=c++17 -O2 -Wall -Wextra -pedantic host_life_benchmark.cpp -o /tmp/irl-benchmark
/tmp/irl-learning && /tmp/irl-inheritance && /tmp/irl-benchmark
```

**Disposition:** Implemented + tested C++17 kernel; Unreal integration candidate only; not merged or released. This record is not a claim of autonomous general intelligence, genuinely simulated trillion-agent subjective experiences, biological evolution or photorealistic completed mobile game.
