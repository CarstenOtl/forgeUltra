# forgeUltra — open questions

## Training script consolidation

We ship two side-by-side training entry points right now:

- `forge_ultra/train.py` / `play.py` — upstream NVIDIA IsaacLab rl_games
  script, copied verbatim. Vanilla PPO. Full upstream feature set (PBT via
  `PbtAlgoObserver`, `MultiObserver`, Ray integration via `--ray-proc-id`,
  `--export_io_descriptors`, full wandb/track flags).

- `forge_ultra/train_rl_games.py` / `play_rl_games.py` — adapted from
  simtoolreal_isaacsim. SAPO-aware (the `ForgeUltraRlGames*` wrappers
  proxy `set_train_info` / `get_env_state` / `set_env_state` to the
  underlying env when present; no-op otherwise). Routes vendored
  `rl_games/` (SAPO fork) onto `sys.path`.

Open: do we want to converge on ONE script that combines both?

- [ ] Keep both indefinitely, or merge?
- [ ] If merge: take simtoolreal's as base (preserves SAPO support, the
      CLI overrides, the per-task `tasks/<task>/outputs/...` layout) and
      port the upstream-only features into it (PBT, MultiObserver, Ray,
      export_io_descriptors, wandb/track flags). Or vice versa.
- [ ] How to expose vanilla vs SAPO mode — a `--mode {vanilla,sapo}`
      flag, or detect from the agent cfg?

## simtoolreal agent cfg features worth keeping

Things from `simtoolreal_lab/.../agents/rl_games_sapo_cfg.yaml` and the
simtoolreal train script that are nicer than upstream:

- [ ] `--agent_cfg <name|path>` flag: pick an arbitrary YAML recipe from
      the task's `agents/` dir without changing the gym registration.
- [ ] CLI overrides via `env.<dotted.key>=value` and
      `agent.<dotted.key>=value`. Much faster than hydra-quoting nested
      keys.
- [ ] `apply_object_selection(env_cfg)` hook on the env cfg module —
      switch held/fixed asset selection at run time per task. (Currently
      wired in `train_rl_games.py` as a `hasattr`-guarded no-op for
      forge; activates automatically if a future env cfg module defines
      `apply_object_selection`.)
- [ ] Per-task hydra output dir under `tasks/<task>/outputs/<date>/<time>`
      rather than a single global `outputs/`.

Decide which of these to also surface on the upstream `train.py` path,
or just leave them simtoolreal-side.

## Franka → kuka_sharpa swap inside forge

Out of scope for this scaffold iteration; tracked here so the asset
isn't forgotten. When ready, separate spec covering:

- [ ] Replace robot cfg references inside `forge_env_cfg.py` /
      `factory_env_cfg.py` with `KUKA_SHARPA_CFG`.
- [ ] Reconcile action space (Franka 7 DoF vs KUKA+SHARPA 29 DoF).
- [ ] Reconcile fingertip indexing / pose targets / control gains.
- [ ] Reconcile `default_task_prop_gains` (currently 6-DoF Franka EE).
- [ ] Decide whether `factory/` stays in sync with upstream or diverges
      for the kuka_sharpa morphology.

## Gym id consolidation

We register `Isaac-Forge-PegInsert-Ultra-v0`,
`Isaac-Forge-GearMesh-Ultra-v0`, `Isaac-Forge-NutThread-Ultra-v0` —
distinct from upstream's `*-Direct-v0` so both coexist on the import
path. Open:

- [ ] Keep both id families forever (upstream as reference, ours as
      modified), or drop the upstream import once we've fully diverged?

## Multi-task agents-dir resolver

`train_rl_games.py`'s `_task_subdir()` is currently hardcoded:
`Isaac-Forge-*-Ultra-v0` → `forge`. When we add more task packages,
generalize this:

- [ ] Walk `forge_ultra/tasks/*/agents/` and resolve by the task
      package that registered the requested gym id, instead of a
      hardcoded prefix match.

## Vendored rl_games fork

- [ ] `rl_games/envs/diambra/diambra.py` line 16 has a hardcoded
      default `/home/trrrrr/Documents/github/ml/diambra/...` — unused
      by us (diambra envs aren't on forge's path) but still ships in
      the vendored fork. Decide whether to scrub it for cleanliness or
      leave for upstream-merge parity.
- [ ] Periodic sync strategy with whatever simtoolreal does to the fork
      (none specified yet).

## Factory vendoring

- [ ] `tasks/factory/` is a verbatim copy of IsaacLab-v2.3.2's
      `direct/factory/`. Decide whether to track upstream changes
      manually or pin and diverge.

## Assets

- [ ] `assets/kuka_sharpa/kuka_sharpa.usd` is 42 MB. If this repo ever
      grows multiple USD checkpoints, set up Git LFS rather than letting
      the working tree balloon. (Currently no git — when git is added.)
