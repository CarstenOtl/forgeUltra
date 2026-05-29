# forgeUltra

Isaac Lab vendored task collection targeting **IsaacLab v2.3.2** (the
`lab232` uv env). Hosts the upstream `forge` task plus a SAPO-trained
KUKA + SHARPA in-hand manipulation task ported from `simtoolreal_isaacsim`.

## Layout

```
forge_ultra/
├── _isaaclab_compat.py          # shims for IsaacLab API drift (see docs/lab232-compat.md)
├── assets/
│   ├── kuka_sharpa/             # KUKA iiwa14 + left SHARPA hand (URDF + USD), from simtoolreal
│   └── dextoolbench_usd/        # manipulation objects (hammers, screwdrivers, brushes, …)
├── tasks/
│   ├── factory/                 # vendored from IsaacLab v2.3.2 (gym.register stripped)
│   ├── forge/                   # vendored from IsaacLab v2.3.2 (gym ids: -Ultra-v0)
│   └── simtoolreal_sharpa/      # vendored from simtoolreal_isaacsim @ 2b210ec
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

See `docs/lab232-compat.md` for the IsaacLab 2.2.1 → 2.3.2 changes folded
into the vendored code.

## Tasks

Two task families ship side-by-side.

### `forge` (vendored from IsaacLab v2.3.2 `isaaclab_tasks.direct.forge`)

Three peg-insertion / gear-mesh / nut-thread variants. Trained with vanilla
PPO on a 7-DoF Franka arm.

Gym ids:
- `Isaac-Forge-PegInsert-Ultra-v0`
- `Isaac-Forge-GearMesh-Ultra-v0`
- `Isaac-Forge-NutThread-Ultra-v0`

Upstream's `Isaac-Forge-*-Direct-v0` family also coexists on the import
path (both upstream `isaaclab_tasks` and our vendored copy register their
own).

### `simtoolreal_sharpa` (vendored from `simtoolreal_isaacsim` @ 2b210ec)

KUKA iiwa14 + left SHARPA in-hand manipulation. Trained with SAPO
(mixed exploration) via the vendored `rl_games/` fork. Object set drawn
from `assets/dextoolbench_usd/` (hammers, screwdrivers, brushes,
markers, …).

Gym ids (kept verbatim from simtoolreal for 1:1 comparability with their
results):
- `simtoolreal_sharpa`
- `simtoolreal_sharpa_pretrain_like`

## Train

Two side-by-side entry-point pairs (see `todos.md` for the open question
of converging them).

**Upstream NVIDIA path** — vanilla PPO, full upstream feature set (PBT,
MultiObserver, Ray, `--export_io_descriptors`):

```bash
/home/carsten.oertel/code/lab232/bin/python forge_ultra/train.py \
  --task Isaac-Forge-PegInsert-Ultra-v0 --headless
```

**SAPO-capable adapted path** — uses the vendored `rl_games/` fork,
supports `env.<key>=value` / `agent.<key>=value` CLI overrides:

```bash
# forge (vanilla PPO via the SAPO-capable script — wrappers no-op for non-SAPO recipes)
/home/carsten.oertel/code/lab232/bin/python forge_ultra/train_rl_games.py \
  --task Isaac-Forge-PegInsert-Ultra-v0 --headless agent.wandb_activate=False

# simtoolreal_sharpa (SAPO, six-block mixed exploration per upstream README)
/home/carsten.oertel/code/lab232/bin/python forge_ultra/train_rl_games.py \
  --task simtoolreal_sharpa \
  --num_envs 1536 \
  --headless \
  agent.params.config.expl_coef_block_size=256 \
  agent.wandb_activate=False
```

SAPO requires `num_envs % expl_coef_block_size == 0`. simtoolreal's
canonical six-block recipe is `1536 / 256`. Other valid pairings:
`1024 / 256` (4 blocks), `512 / 256` (2 blocks). One-block debug
settings like `--num_envs 16 agent.params.config.expl_coef_block_size=16`
work for smoke testing but the resulting checkpoint is not replay-shape
compatible with the six-block SAPO recipe.

Outputs land under `tasks/<task>/outputs/<date>/<time>/` (Hydra) and
`tasks/<task>/logs/<run_name>/` (rl_games checkpoints + params).

## Play / replay

```bash
# forge — best-so-far checkpoint, viewer
/home/carsten.oertel/code/lab232/bin/python forge_ultra/play.py \
  --task Isaac-Forge-PegInsert-Ultra-v0 --num_envs 4 --real-time --livestream 2

# simtoolreal_sharpa — same pattern, SAPO replay via train_rl_games's sibling
/home/carsten.oertel/code/lab232/bin/python forge_ultra/play_rl_games.py \
  --task simtoolreal_sharpa --num_envs 4 --real-time --livestream 2 \
  --checkpoint tasks/simtoolreal_sharpa/logs/<run>/nn/<best>.pth
```

`--livestream 2` enables WebRTC streaming for remote viewing (browser at
`http://<host>:8211/streaming/webrtc-client/`).

## Open questions

See `todos.md`.
