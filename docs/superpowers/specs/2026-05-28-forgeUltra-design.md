# forgeUltra — initial repo scaffold design

**Date:** 2026-05-28
**Status:** Approved, ready for implementation plan
**Target env:** `/home/carsten.oertel/code/lab232` (uv env on IsaacLab v2.3.2, Python 3.11)

## Goal

Create a new repository `forgeUltra` at `/home/carsten.oertel/code/forgeUltra/`
that:

1. Mirrors the layout of `simtoolreal_isaacsim/` (the existing reference
   IsaacLab port for the KUKA + SHARPA setup).
2. Vendors the `kuka_sharpa` assets so they are available locally,
   independent of any other repo.
3. Vendors the IsaacLab `forge` direct task (and its `factory`
   dependency) so it can be trained end-to-end from this repo against
   the vendored SAPO-capable `rl_games` fork *and* against upstream
   vanilla `rl_games` via the upstream NVIDIA train script.
4. Is portable: every in-repo path is relative to the source file that
   uses it, so the repo works wherever it is cloned without per-machine
   configuration.

This iteration is **pure scaffolding**. No behavioral changes to forge.
Forge still uses the Franka robot it was designed for; `kuka_sharpa`
sits in `assets/` available for the follow-up adaptation.

## Out of scope (tracked in `todos.md`)

- Replacing Franka with `kuka_sharpa` inside `forge_env_cfg.py` /
  `factory_env_cfg.py`.
- Reconciling action space, fingertip indexing, and control gains for
  the kuka_sharpa morphology.
- SAPO recipes for forge tasks.
- Git initialization or LFS setup.
- Converging the two training entry points into one.

## Naming convention

Per PEP 8 with the IsaacLab ecosystem precedent
(`isaaclab`, `isaaclab_tasks`, `isaaclab_assets`):

| Layer | Name |
|---|---|
| repo / on-disk dir | `forgeUltra` |
| Python package | `forge_ultra` |
| install name in `setup.py` | `forge_ultra` |
| subpackages | `forge_ultra.assets.kuka_sharpa`, `forge_ultra.tasks.forge`, `forge_ultra.tasks.factory`, `forge_ultra.rl_games` |

Gym ids registered by the vendored copy use the `-Ultra-v0` suffix so
they coexist with upstream's `-Direct-v0` ids on the same import path:

- `Isaac-Forge-PegInsert-Ultra-v0`
- `Isaac-Forge-GearMesh-Ultra-v0`
- `Isaac-Forge-NutThread-Ultra-v0`

## Directory layout

```
forgeUltra/
├── pyproject.toml                          # setuptools>=61, wheel
├── setup.py                                # package=forge_ultra
├── README.md                               # install + train recipes
├── todos.md                                # open questions for later
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-05-28-forgeUltra-design.md   # this file
└── forge_ultra/
    ├── __init__.py
    ├── assets/
    │   ├── __init__.py
    │   └── kuka_sharpa/                    # verbatim copy from simtoolreal_lab/assets/kuka_sharpa/
    │       ├── __init__.py                 # exports KUKA_SHARPA_CFG, KUKA_SHARPA_JOINT_NAMES
    │       ├── kuka_sharpa.py
    │       ├── kuka_sharpa.usd             # 42 MB
    │       ├── config.yaml                 # paths rewritten to relative
    │       ├── configuration/
    │       ├── left_sharpa_ha4/
    │       └── urdf/
    ├── tasks/
    │   ├── __init__.py
    │   ├── factory/                        # verbatim from IsaacLab-v2.3.2 isaaclab_tasks/direct/factory/
    │   │   ├── __init__.py                 # gym.register stripped (no double-reg with upstream)
    │   │   ├── factory_control.py
    │   │   ├── factory_env_cfg.py
    │   │   ├── factory_env.py
    │   │   ├── factory_tasks_cfg.py
    │   │   ├── factory_utils.py
    │   │   └── agents/
    │   └── forge/                          # verbatim from IsaacLab-v2.3.2 isaaclab_tasks/direct/forge/
    │       ├── __init__.py                 # gym.register ids renamed to -Ultra-v0
    │       ├── forge_env.py                # 3 factory imports rewritten to relative
    │       ├── forge_env_cfg.py            # 1 factory import rewritten to relative
    │       ├── forge_events.py
    │       ├── forge_tasks_cfg.py
    │       ├── forge_utils.py
    │       └── agents/
    │           ├── __init__.py
    │           ├── rl_games_ppo_cfg.yaml
    │           └── rl_games_ppo_cfg_nut_thread.yaml
    ├── rl_games/                           # verbatim from simtoolreal_lab/rl_games/ (40 MB, SAPO fork)
    ├── train.py                            # upstream NVIDIA verbatim + 1 import line
    ├── play.py                             # upstream NVIDIA verbatim + 1 import line
    ├── train_rl_games.py                   # simtoolreal-adapted, generalized for forge
    └── play_rl_games.py                    # simtoolreal-adapted, generalized for forge
```

## File copy plan

### Verbatim copies (no edits)

| Source | Destination | Size |
|---|---|---|
| `simtoolreal_isaacsim/simtoolreal_lab/assets/kuka_sharpa/` | `forgeUltra/forge_ultra/assets/kuka_sharpa/` | 42 MB |
| `simtoolreal_isaacsim/simtoolreal_lab/rl_games/` | `forgeUltra/forge_ultra/rl_games/` | 40 MB |
| `IsaacLab-v2.3.2/source/isaaclab_tasks/isaaclab_tasks/direct/factory/` (excluding `__pycache__`) | `forgeUltra/forge_ultra/tasks/factory/` | ~ |
| `IsaacLab-v2.3.2/source/isaaclab_tasks/isaaclab_tasks/direct/forge/` (excluding `__pycache__`) | `forgeUltra/forge_ultra/tasks/forge/` | ~ |
| `IsaacLab-v2.3.2/scripts/reinforcement_learning/rl_games/train.py` | `forgeUltra/forge_ultra/train.py` | 261 lines |
| `IsaacLab-v2.3.2/scripts/reinforcement_learning/rl_games/play.py` | `forgeUltra/forge_ultra/play.py` | — |
| `simtoolreal_isaacsim/simtoolreal_lab/train_rl_games.py` | `forgeUltra/forge_ultra/train_rl_games.py` | 299 lines (will be adapted, see below) |
| `simtoolreal_isaacsim/simtoolreal_lab/play_rl_games.py` | `forgeUltra/forge_ultra/play_rl_games.py` | will be adapted |

### Edits

#### `forge_ultra/tasks/forge/forge_env_cfg.py`

Line 11 — make the factory import relative to our vendored copy:

```python
# was:
from isaaclab_tasks.direct.factory.factory_env_cfg import OBS_DIM_CFG, STATE_DIM_CFG, CtrlCfg, FactoryEnvCfg, ObsRandCfg
# becomes:
from ..factory.factory_env_cfg import OBS_DIM_CFG, STATE_DIM_CFG, CtrlCfg, FactoryEnvCfg, ObsRandCfg
```

#### `forge_ultra/tasks/forge/forge_env.py`

Three factory imports made relative:

```python
# was:
from isaaclab_tasks.direct.factory import factory_utils
from isaaclab_tasks.direct.factory.factory_env import FactoryEnv
from isaaclab_tasks.direct.factory.factory_tasks_cfg import FactoryTask, GearMesh, NutThread, PegInsert
# becomes:
from ..factory import factory_utils
from ..factory.factory_env import FactoryEnv
from ..factory.factory_tasks_cfg import FactoryTask, GearMesh, NutThread, PegInsert
```

(Confirmed: `tasks/factory/` has no `isaaclab_tasks` imports of its own, so
vendoring it is self-contained.)

#### `forge_ultra/tasks/forge/__init__.py`

Rewrite the three `gym.register` ids:

```python
Isaac-Forge-PegInsert-Direct-v0  →  Isaac-Forge-PegInsert-Ultra-v0
Isaac-Forge-GearMesh-Direct-v0   →  Isaac-Forge-GearMesh-Ultra-v0
Isaac-Forge-NutThread-Direct-v0  →  Isaac-Forge-NutThread-Ultra-v0
```

Everything else inside `__init__.py` (entry points, kwargs) stays — the
package-qualified entry points like `f"{__name__}.forge_env:ForgeEnv"`
auto-resolve to our vendored module via `__name__`.

#### `forge_ultra/tasks/factory/__init__.py`

Strip any `gym.register(...)` calls (avoids double-registering upstream's
`Isaac-Factory-*-v0` ids when both the upstream `isaaclab_tasks` and our
vendored `forge_ultra.tasks.factory` get imported). Keep the `from . import agents`
line. The factory module is consumed only as a Python-level base class
for forge; it does not need its own gym ids in this scaffold.

#### `forge_ultra/__init__.py` and `forge_ultra/tasks/__init__.py`

Single-line docstrings. No auto-import side effects. Gym registration
happens explicitly via `import forge_ultra.tasks.forge` from the train/play
scripts.

#### `forge_ultra/assets/kuka_sharpa/config.yaml`

Rewrite the two absolute paths to be relative to the file:

```yaml
# was:
asset_path: /home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/assets/kuka_sharpa/urdf/kuka_sharpa_description/iiwa14_left_sharpa_adjusted_restricted.urdf
usd_dir: /home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/assets/kuka_sharpa

# becomes:
asset_path: urdf/kuka_sharpa_description/iiwa14_left_sharpa_adjusted_restricted.urdf
usd_dir: .
```

(The Python loader interprets these relative to the file's own directory.
`kuka_sharpa.py` itself already uses `os.path.dirname(__file__)` and needs
no edit.)

#### `forge_ultra/train.py` and `forge_ultra/play.py` (upstream NVIDIA)

One addition each: after `import isaaclab_tasks  # noqa: F401`, add:

```python
import forge_ultra.tasks.forge  # noqa: F401  # register Isaac-Forge-*-Ultra-v0
```

This registers our vendored gym ids alongside upstream's, so both id
families remain trainable through the upstream script. Upstream's
behavior on the upstream ids is unchanged.

#### `forge_ultra/train_rl_games.py` and `forge_ultra/play_rl_games.py` (simtoolreal-adapted)

Adapt from simtoolreal's scripts:

- Replace the simtoolreal task imports
  (`import simtoolreal_lab.tasks.sharpa_nutscrew_pick_place.gym_setup`,
  `import simtoolreal_lab.tasks.simtoolreal_sharpa.gym_setup`) with:

  ```python
  import forge_ultra.tasks.forge  # noqa: F401
  ```

- Replace `_task_agents_dir(task_name)` with a concrete resolver for this
  iteration: any `Isaac-Forge-*-Ultra-v0` task → `forge_ultra/tasks/forge/agents`.
  (We only ship one task package right now; generalization to multiple
  task packages is tracked in `todos.md`.)

- Apply the same mapping for the `task_output_dir` that simtoolreal's
  script uses to route Hydra's `run.dir`: `Isaac-Forge-*-Ultra-v0` →
  `forge_ultra/tasks/forge/outputs/<date>/<time>`.

- Rename wrappers `SimToolRealRlGamesVecEnvWrapper` → `ForgeUltraRlGamesVecEnvWrapper`
  and `SimToolRealRlGamesGpuEnv` → `ForgeUltraRlGamesGpuEnv`. Logic
  unchanged: they proxy `set_train_info` / `get_env_state` / `set_env_state`
  through to the underlying env when present, no-op otherwise. Vanilla
  forge PPO trains through them with zero behavior change.

- Keep the `--agent_cfg <name|path>` flag (load YAML recipe by basename
  in the task's `agents/` dir or by absolute path).

- Keep the `env.<dotted.key>=value` / `agent.<dotted.key>=value` CLI
  override parsing.

- Drop the SHARPA-specific `--visualize_grasp_bounding_box` flag — not
  applicable to forge.

- Keep the vendored `rl_games/` `sys.path` insertion:
  ```python
  VENDORED_RL_GAMES = pathlib.Path(__file__).resolve().parent / "rl_games"
  if VENDORED_RL_GAMES.is_dir():
      sys.path.insert(0, str(VENDORED_RL_GAMES))
  ```

### `setup.py`

```python
"""forgeUltra setuptools."""
from setuptools import find_packages, setup

setup(
    name="forge_ultra",
    version="0.1.0",
    description="Isaac Lab forge task scaffold with KUKA-SHARPA assets staged for adaptation.",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    package_data={
        "forge_ultra.tasks.forge.agents": ["*.yaml"],
        "forge_ultra.tasks.factory.agents": ["*.yaml"],
    },
    install_requires=[],
)
```

### `pyproject.toml`

Identical to simtoolreal's:

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"
```

### `README.md`

Minimal, includes:

- Status note: forge runs with Franka; `kuka_sharpa` staged in `assets/`
  for the future Franka → kuka_sharpa adaptation.
- `pip install -e .` install instructions (no absolute paths).
- Two CLI examples:

  ```bash
  # Upstream NVIDIA path (vanilla PPO, full upstream features)
  python forge_ultra/train.py --task Isaac-Forge-PegInsert-Ultra-v0 --headless

  # SAPO-capable adapted path (vendored rl_games fork, env.x=y / agent.x=y CLI overrides)
  python forge_ultra/train_rl_games.py --task Isaac-Forge-PegInsert-Ultra-v0 --headless agent.wandb_activate=False
  ```

- Note that the vendored `rl_games/` fork is the SAPO variant; stock forge
  PPO runs fine on it (just doesn't use the SAPO extras).

- Pointer to `todos.md` for open questions.

### `todos.md`

Full seed content (this is what gets written verbatim to
`forgeUltra/todos.md`):

```markdown
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
      switch held/fixed asset selection at run time per task.
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

`train_rl_games.py`'s `_task_agents_dir()` is currently hardcoded to
`forge_ultra/tasks/forge/agents` for any `Isaac-Forge-*-Ultra-v0`. When
we add more task packages, generalize this:

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
```

## Portability rules

Apply throughout:

- All in-repo path resolution uses `pathlib.Path(__file__).resolve().parent / "..."`
  or `os.path.dirname(__file__)`. No `/home/...`, no `cwd`-relative
  assumptions.
- `kuka_sharpa.py` already follows this rule — no change needed.
- `kuka_sharpa/config.yaml` rewritten to repo-relative paths (see Edits
  section above).
- URDF mesh refs that use `package://` are left as-is; that's
  ROS-style resolution and is not broken by relocation. (Confirmed by
  scanning the URDF files: no absolute filesystem paths inside them.)
- `train_rl_games.py` derives Hydra output dir from the gym task id
  generically, not from a hardcoded task-name allowlist.
- The vendored `rl_games/envs/diambra/diambra.py` line-16 hardcoded
  `/home/trrrrr/...` default is left alone — diambra envs are not on
  forge's import path, and scrubbing it would diverge the fork from
  simtoolreal's. Tracked in `todos.md`.

## What "done" looks like for this iteration

1. `/home/carsten.oertel/code/forgeUltra/` exists with the directory
   layout above.
2. `cd /home/carsten.oertel/code/forgeUltra && /home/carsten.oertel/code/lab232/bin/python -m pip install -e .` installs `forge_ultra` cleanly.
3. From the `lab232` env, `python -c "import forge_ultra; import forge_ultra.tasks.forge; import forge_ultra.tasks.factory; from forge_ultra.assets.kuka_sharpa import KUKA_SHARPA_CFG; print('ok')"` prints `ok` (this is the import-only smoke test; it does NOT launch Isaac Sim and so does not require `pxr`).
4. Either of these commands launches forge training end-to-end on Franka
   without error (terminating after a few iterations is fine — the goal
   is to confirm the env constructs, gym id resolves, and the rl_games
   loop starts):

   ```bash
   python forge_ultra/train.py --task Isaac-Forge-PegInsert-Ultra-v0 --headless --max_iterations 2
   python forge_ultra/train_rl_games.py --task Isaac-Forge-PegInsert-Ultra-v0 --headless --max_iterations 2 agent.wandb_activate=False
   ```

5. `todos.md` is present at repo root.

No git, no commits, no behavioral changes.

## Dependencies on later work

The Franka → kuka_sharpa adaptation gets its own spec. This scaffold
deliberately leaves the kuka_sharpa asset unused so that the swap is
a single focused change, and so this scaffold step is verifiable
independently (forge trains on Franka exactly as upstream).
