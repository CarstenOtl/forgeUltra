# forgeUltra

Isaac Lab scaffold for the `forge` task with the KUKA + SHARPA assets
staged in `forge_ultra/assets/kuka_sharpa/` for future adaptation.

## Status

This is the **scaffold iteration**. Forge still uses the Franka robot it
was designed for. `kuka_sharpa` lives in `assets/` but is not yet wired
into the env cfg. Swapping Franka → kuka_sharpa is a separate spec —
see `todos.md`.

## Layout

```
forge_ultra/
├── assets/kuka_sharpa/          # vendored from simtoolreal_isaacsim
├── tasks/factory/               # vendored from IsaacLab-v2.3.2 (no gym.register)
├── tasks/forge/                 # vendored from IsaacLab-v2.3.2 (gym ids: -Ultra-v0)
├── rl_games/                    # vendored SAPO fork from simtoolreal
├── train.py                     # upstream NVIDIA rl_games train (vanilla PPO)
├── play.py                      # upstream NVIDIA rl_games play
├── train_rl_games.py            # simtoolreal-adapted (SAPO-capable, --agent_cfg)
└── play_rl_games.py             # simtoolreal-adapted (SAPO-capable)
```

## Install

From the repo root, with the `lab232` uv env active (or by calling its
interpreter directly):

```bash
/home/carsten.oertel/code/lab232/bin/python -m pip install -e .
```

## Train

Two side-by-side entry points (see `todos.md` for the open question of
converging them):

**Upstream NVIDIA path** — vanilla PPO, full upstream feature set (PBT,
MultiObserver, Ray, `--export_io_descriptors`):

```bash
/home/carsten.oertel/code/lab232/bin/python forge_ultra/train.py \
  --task Isaac-Forge-PegInsert-Ultra-v0 --headless
```

**SAPO-capable adapted path** — uses the vendored `rl_games/` fork,
supports `env.<key>=value` / `agent.<key>=value` CLI overrides:

```bash
/home/carsten.oertel/code/lab232/bin/python forge_ultra/train_rl_games.py \
  --task Isaac-Forge-PegInsert-Ultra-v0 --headless agent.wandb_activate=False
```

Available forge task ids: `Isaac-Forge-PegInsert-Ultra-v0`,
`Isaac-Forge-GearMesh-Ultra-v0`, `Isaac-Forge-NutThread-Ultra-v0`.
Upstream's `Isaac-Forge-*-Direct-v0` ids remain available too (both
families coexist on the import path).

## Open questions

See `todos.md`.
