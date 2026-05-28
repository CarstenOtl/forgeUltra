# forgeUltra Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the `forgeUltra` repository at `/home/carsten.oertel/code/forgeUltra/` so the IsaacLab `forge` task (with its `factory` dependency vendored) is trainable end-to-end from the `lab232` uv env, the `kuka_sharpa` assets ship inside the repo for future Franka-replacement work, and a vendored SAPO `rl_games` fork is on the import path.

**Architecture:** Pure copy-and-rewrite scaffolding — verbatim vendoring of three external trees (`kuka_sharpa` assets, `factory` task, `forge` task, SAPO `rl_games` fork) into a single `forge_ultra` Python package, with surgical edits to (a) make factory→forge imports relative, (b) rename the three forge gym ids to `-Ultra-v0`, (c) make a SAPO-aware training launcher generic for forge, and (d) make every path repo-relative so the tree is portable to any clone location. Forge still trains on Franka in this iteration; the kuka_sharpa swap is a separate spec.

**Tech Stack:** Python 3.11 / `lab232` uv env / IsaacLab v2.3.2 / `rl_games` (vendored SAPO fork) / gymnasium / Hydra / setuptools.

**Spec:** `/home/carsten.oertel/code/forgeUltra/docs/superpowers/specs/2026-05-28-forgeUltra-design.md`

---

## Conventions for this plan

- **No git this iteration.** The spec says skip git. Each task's "Commit" step from the standard template is replaced with a "Verify" step that runs concrete commands and confirms expected output. Re-add commits if the user changes their mind about git later.
- **Python interpreter:** Use `/home/carsten.oertel/code/lab232/bin/python` for every verification command. Avoid `python` without a path — your shell PATH may point elsewhere.
- **No `cp -r` of `__pycache__`.** Every copy command excludes `__pycache__/` and `*.pyc` to keep the tree clean. The `rsync --exclude='__pycache__/'` pattern is preferred over `cp` for that reason.
- **Repo root:** `/home/carsten.oertel/code/forgeUltra/`. The `docs/superpowers/{specs,plans}/` directory already exists (spec + this plan live there).

---

## Task 1: Create top-level repo skeleton

**Files:**
- Create: `/home/carsten.oertel/code/forgeUltra/forge_ultra/__init__.py`
- Create: `/home/carsten.oertel/code/forgeUltra/forge_ultra/assets/__init__.py`
- Create: `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/__init__.py`
- Create: `/home/carsten.oertel/code/forgeUltra/pyproject.toml`
- Create: `/home/carsten.oertel/code/forgeUltra/setup.py`

- [ ] **Step 1.1: Create the package directory tree**

Run:
```bash
mkdir -p /home/carsten.oertel/code/forgeUltra/forge_ultra/assets \
         /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks
```

- [ ] **Step 1.2: Write `forge_ultra/__init__.py`**

Content:
```python
"""forgeUltra: Isaac Lab forge task scaffold with KUKA-SHARPA assets staged for adaptation."""
```

- [ ] **Step 1.3: Write `forge_ultra/assets/__init__.py`**

Content:
```python
"""forgeUltra asset configurations."""
```

- [ ] **Step 1.4: Write `forge_ultra/tasks/__init__.py`**

Content:
```python
"""forgeUltra task packages."""
```

- [ ] **Step 1.5: Write `pyproject.toml`**

Content:
```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"
```

- [ ] **Step 1.6: Write `setup.py`**

Content:
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

- [ ] **Step 1.7: Verify skeleton structure**

Run:
```bash
find /home/carsten.oertel/code/forgeUltra -maxdepth 3 -not -path '*/docs*' -not -name 'docs' | sort
```

Expected output (order may vary):
```
/home/carsten.oertel/code/forgeUltra
/home/carsten.oertel/code/forgeUltra/forge_ultra
/home/carsten.oertel/code/forgeUltra/forge_ultra/__init__.py
/home/carsten.oertel/code/forgeUltra/forge_ultra/assets
/home/carsten.oertel/code/forgeUltra/forge_ultra/assets/__init__.py
/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks
/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/__init__.py
/home/carsten.oertel/code/forgeUltra/pyproject.toml
/home/carsten.oertel/code/forgeUltra/setup.py
```

---

## Task 2: Vendor the kuka_sharpa assets (verbatim, then fix absolute paths)

**Files:**
- Create (verbatim copy): `/home/carsten.oertel/code/forgeUltra/forge_ultra/assets/kuka_sharpa/` (entire directory from `/home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/assets/kuka_sharpa/`, excluding `__pycache__`)
- Modify: `/home/carsten.oertel/code/forgeUltra/forge_ultra/assets/kuka_sharpa/config.yaml` (rewrite absolute paths to relative)

- [ ] **Step 2.1: Copy the asset tree**

Run:
```bash
rsync -a --exclude='__pycache__/' \
  /home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/assets/kuka_sharpa/ \
  /home/carsten.oertel/code/forgeUltra/forge_ultra/assets/kuka_sharpa/
```

- [ ] **Step 2.2: Verify the copy**

Run:
```bash
ls /home/carsten.oertel/code/forgeUltra/forge_ultra/assets/kuka_sharpa/
```

Expected output:
```
config.yaml
configuration
__init__.py
kuka_sharpa.py
kuka_sharpa.usd
left_sharpa_ha4
urdf
```

Run:
```bash
du -sh /home/carsten.oertel/code/forgeUltra/forge_ultra/assets/kuka_sharpa/
```

Expected: roughly `42M`.

- [ ] **Step 2.3: Rewrite the two absolute paths in `config.yaml`**

Read `/home/carsten.oertel/code/forgeUltra/forge_ultra/assets/kuka_sharpa/config.yaml`. The current first two lines are:

```yaml
asset_path: /home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/assets/kuka_sharpa/urdf/kuka_sharpa_description/iiwa14_left_sharpa_adjusted_restricted.urdf
usd_dir: /home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/assets/kuka_sharpa
```

Replace those two lines with:

```yaml
asset_path: urdf/kuka_sharpa_description/iiwa14_left_sharpa_adjusted_restricted.urdf
usd_dir: .
```

Leave every other line unchanged.

- [ ] **Step 2.4: Verify no absolute paths remain in the asset tree**

Run:
```bash
grep -rn "/home/carsten.oertel" /home/carsten.oertel/code/forgeUltra/forge_ultra/assets/kuka_sharpa/ 2>/dev/null
```

Expected output: (empty — no lines printed)

Run:
```bash
head -2 /home/carsten.oertel/code/forgeUltra/forge_ultra/assets/kuka_sharpa/config.yaml
```

Expected output:
```
asset_path: urdf/kuka_sharpa_description/iiwa14_left_sharpa_adjusted_restricted.urdf
usd_dir: .
```

---

## Task 3: Vendor the SAPO rl_games fork (verbatim)

**Files:**
- Create (verbatim copy): `/home/carsten.oertel/code/forgeUltra/forge_ultra/rl_games/` (entire directory from `/home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/rl_games/`, excluding `__pycache__`)

- [ ] **Step 3.1: Copy the fork**

Run:
```bash
rsync -a --exclude='__pycache__/' \
  /home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/rl_games/ \
  /home/carsten.oertel/code/forgeUltra/forge_ultra/rl_games/
```

- [ ] **Step 3.2: Verify the copy**

Run:
```bash
ls /home/carsten.oertel/code/forgeUltra/forge_ultra/rl_games/
```

Expected output:
```
docs
LICENSE
notebooks
poetry.lock
pyproject.toml
README.md
rl_games
runner.py
tests
```

Run:
```bash
du -sh /home/carsten.oertel/code/forgeUltra/forge_ultra/rl_games/
```

Expected: roughly `40M`.

Note: the vendored fork's known `/home/trrrrr/...` default in `rl_games/envs/diambra/diambra.py:16` is intentionally left as-is per the spec (diambra envs are not on forge's import path; scrubbing would diverge the fork). This is tracked in `todos.md`.

---

## Task 4: Vendor `factory` task and strip gym.register

**Files:**
- Create (verbatim copy): `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/factory/` (from `/home/carsten.oertel/code/IsaacLab-v2.3.2/source/isaaclab_tasks/isaaclab_tasks/direct/factory/`, excluding `__pycache__`)
- Modify: `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/factory/__init__.py` (remove gym.register blocks)

- [ ] **Step 4.1: Copy factory**

Run:
```bash
rsync -a --exclude='__pycache__/' \
  /home/carsten.oertel/code/IsaacLab-v2.3.2/source/isaaclab_tasks/isaaclab_tasks/direct/factory/ \
  /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/factory/
```

- [ ] **Step 4.2: Verify the copy**

Run:
```bash
ls /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/factory/
```

Expected output:
```
agents
factory_control.py
factory_env_cfg.py
factory_env.py
factory_tasks_cfg.py
factory_utils.py
__init__.py
```

- [ ] **Step 4.3: Rewrite `tasks/factory/__init__.py` to strip gym.register**

The current file contains three `gym.register(...)` blocks for `Isaac-Factory-{PegInsert,GearMesh,NutThread}-Direct-v0`. We don't need them — we only consume factory as a Python base for forge, and registering would clash with the upstream `isaaclab_tasks` already on the path.

Overwrite `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/factory/__init__.py` with exactly this content:

```python
# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Vendored Isaac Lab factory task package (gym registration intentionally omitted).

This package is consumed by `forge_ultra.tasks.forge` as a Python-level base
class. Gym ids for the Factory tasks are NOT registered here to avoid
double-registering upstream's `Isaac-Factory-*-Direct-v0` ids when both
packages are on the import path. Use the upstream `isaaclab_tasks.direct.factory`
package if you need to train factory tasks via gym.
"""

from . import agents  # noqa: F401
```

- [ ] **Step 4.4: Verify no gym.register calls remain**

Run:
```bash
grep -n "gym\.register" /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/factory/__init__.py
```

Expected output: (empty — no lines printed)

- [ ] **Step 4.5: Confirm factory has no upstream isaaclab_tasks deps**

Run:
```bash
grep -rn "from isaaclab_tasks\|import isaaclab_tasks" /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/factory/ 2>/dev/null
```

Expected output: (empty — no lines printed; confirms vendoring is self-contained)

---

## Task 5: Vendor `forge` task and rewrite imports + gym ids

**Files:**
- Create (verbatim copy): `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/` (from `/home/carsten.oertel/code/IsaacLab-v2.3.2/source/isaaclab_tasks/isaaclab_tasks/direct/forge/`, excluding `__pycache__`)
- Modify: `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_env_cfg.py` (1 import line)
- Modify: `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_env.py` (2 import lines)
- Modify: `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_tasks_cfg.py` (1 import line)
- Modify: `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/__init__.py` (3 gym id renames)

- [ ] **Step 5.1: Copy forge**

Run:
```bash
rsync -a --exclude='__pycache__/' \
  /home/carsten.oertel/code/IsaacLab-v2.3.2/source/isaaclab_tasks/isaaclab_tasks/direct/forge/ \
  /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/
```

- [ ] **Step 5.2: Verify the copy**

Run:
```bash
ls /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/
```

Expected output:
```
agents
forge_env_cfg.py
forge_env.py
forge_events.py
forge_tasks_cfg.py
forge_utils.py
__init__.py
```

- [ ] **Step 5.3: Rewrite the factory import in `forge_env_cfg.py`**

In `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_env_cfg.py`, replace the line:

```python
from isaaclab_tasks.direct.factory.factory_env_cfg import OBS_DIM_CFG, STATE_DIM_CFG, CtrlCfg, FactoryEnvCfg, ObsRandCfg
```

with:

```python
from ..factory.factory_env_cfg import OBS_DIM_CFG, STATE_DIM_CFG, CtrlCfg, FactoryEnvCfg, ObsRandCfg
```

- [ ] **Step 5.4: Rewrite the two factory imports in `forge_env.py`**

In `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_env.py` (v2.3.2), replace these two lines (lines 12-13 in the source):

```python
from isaaclab_tasks.direct.factory import factory_utils
from isaaclab_tasks.direct.factory.factory_env import FactoryEnv
```

with exactly:

```python
from ..factory import factory_utils
from ..factory.factory_env import FactoryEnv
```

(Note: an earlier plan draft mentioned a third import line for `factory_tasks_cfg` with `FactoryTask, GearMesh, NutThread, PegInsert` — that line is in the v3.0.0-beta2 forge_env.py, not v2.3.2. v2.3.2's forge_env.py only imports the two factory symbols listed above.)

- [ ] **Step 5.4b: Rewrite the factory import in `forge_tasks_cfg.py`**

In `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_tasks_cfg.py`, replace line 8:

```python
from isaaclab_tasks.direct.factory.factory_tasks_cfg import FactoryTask, GearMesh, NutThread, PegInsert
```

with exactly:

```python
from ..factory.factory_tasks_cfg import FactoryTask, GearMesh, NutThread, PegInsert
```

- [ ] **Step 5.5: Rename the three gym ids in `forge/__init__.py`**

In `/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/__init__.py`, change each `gym.register(...)` block's `id=` argument:

| was | becomes |
|---|---|
| `"Isaac-Forge-PegInsert-Direct-v0"` | `"Isaac-Forge-PegInsert-Ultra-v0"` |
| `"Isaac-Forge-GearMesh-Direct-v0"` | `"Isaac-Forge-GearMesh-Ultra-v0"` |
| `"Isaac-Forge-NutThread-Direct-v0"` | `"Isaac-Forge-NutThread-Ultra-v0"` |

Leave the rest of each block (entry_point, kwargs, disable_env_checker) unchanged. The `f"{__name__}..."` entry-point template auto-resolves to the vendored module via `__name__`.

- [ ] **Step 5.6: Verify import rewrites**

Run:
```bash
grep -n "from isaaclab_tasks\|from \.\.factory\|from \.factory" /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_env.py /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_env_cfg.py
```

Expected output (exactly):
```
/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_env.py:12:from ..factory import factory_utils
/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_env.py:13:from ..factory.factory_env import FactoryEnv
/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/forge_env_cfg.py:11:from ..factory.factory_env_cfg import OBS_DIM_CFG, STATE_DIM_CFG, CtrlCfg, FactoryEnvCfg, ObsRandCfg
```

No `from isaaclab_tasks` line should appear.

- [ ] **Step 5.7: Verify gym id renames**

Run:
```bash
grep -n "id=\"Isaac-Forge" /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/__init__.py
```

Expected output:
```
/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/__init__.py:15:    id="Isaac-Forge-PegInsert-Ultra-v0",
/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/__init__.py:24:    id="Isaac-Forge-GearMesh-Ultra-v0",
/home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/__init__.py:33:    id="Isaac-Forge-NutThread-Ultra-v0",
```

(Exact line numbers may differ slightly — the important thing is three `-Ultra-v0` matches, zero `-Direct-v0` matches.)

Run:
```bash
grep -c "Direct-v0" /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/forge/__init__.py
```

Expected output: `0`

---

## Task 6: Copy upstream NVIDIA `train.py` and `play.py` (with one-line forge import)

**Files:**
- Create (verbatim copy + one inserted line): `/home/carsten.oertel/code/forgeUltra/forge_ultra/train.py` (from `/home/carsten.oertel/code/IsaacLab-v2.3.2/scripts/reinforcement_learning/rl_games/train.py`)
- Create (verbatim copy + one inserted line): `/home/carsten.oertel/code/forgeUltra/forge_ultra/play.py` (from `/home/carsten.oertel/code/IsaacLab-v2.3.2/scripts/reinforcement_learning/rl_games/play.py`)

- [ ] **Step 6.1: Copy upstream train.py and play.py**

Run:
```bash
cp /home/carsten.oertel/code/IsaacLab-v2.3.2/scripts/reinforcement_learning/rl_games/train.py \
   /home/carsten.oertel/code/forgeUltra/forge_ultra/train.py
cp /home/carsten.oertel/code/IsaacLab-v2.3.2/scripts/reinforcement_learning/rl_games/play.py \
   /home/carsten.oertel/code/forgeUltra/forge_ultra/play.py
```

- [ ] **Step 6.2: Register vendored forge ids in `train.py`**

In `/home/carsten.oertel/code/forgeUltra/forge_ultra/train.py`, find the existing line (around line 90):

```python
import isaaclab_tasks  # noqa: F401
```

Insert this single line immediately after it:

```python
import forge_ultra.tasks.forge  # noqa: F401  # register Isaac-Forge-*-Ultra-v0
```

- [ ] **Step 6.3: Register vendored forge ids in `play.py`**

In `/home/carsten.oertel/code/forgeUltra/forge_ultra/play.py`, find the existing line (around line 81):

```python
import isaaclab_tasks  # noqa: F401
```

Insert this single line immediately after it:

```python
import forge_ultra.tasks.forge  # noqa: F401  # register Isaac-Forge-*-Ultra-v0
```

- [ ] **Step 6.4: Verify both edits**

Run:
```bash
grep -n "import forge_ultra.tasks.forge\|import isaaclab_tasks" /home/carsten.oertel/code/forgeUltra/forge_ultra/train.py /home/carsten.oertel/code/forgeUltra/forge_ultra/play.py
```

Expected output (line numbers approximate):
```
/home/carsten.oertel/code/forgeUltra/forge_ultra/train.py:90:import isaaclab_tasks  # noqa: F401
/home/carsten.oertel/code/forgeUltra/forge_ultra/train.py:91:import forge_ultra.tasks.forge  # noqa: F401  # register Isaac-Forge-*-Ultra-v0
/home/carsten.oertel/code/forgeUltra/forge_ultra/play.py:81:import isaaclab_tasks  # noqa: F401
/home/carsten.oertel/code/forgeUltra/forge_ultra/play.py:82:import forge_ultra.tasks.forge  # noqa: F401  # register Isaac-Forge-*-Ultra-v0
```

The order matters — `import forge_ultra.tasks.forge` MUST come AFTER `import isaaclab_tasks` (forge's gym.register may import factory_env_cfg which may transitively need things isaaclab_tasks bootstraps).

---

## Task 7: Adapt simtoolreal `train_rl_games.py` for forge

**Files:**
- Create (copy + targeted edits): `/home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py` (from `/home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/train_rl_games.py`)

This is the most substantial edit task. Work through each step in order; do not batch — these edits cumulatively rewrite the simtoolreal-specific surface to a generic forge-aware surface.

- [ ] **Step 7.1: Copy the simtoolreal train script as the starting point**

Run:
```bash
cp /home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/train_rl_games.py \
   /home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py
```

- [ ] **Step 7.2: Remove the SHARPA-specific `--visualize_grasp_bounding_box` argparse block**

In `/home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py`, find this block (it spans roughly lines 29-39 in the original simtoolreal file):

```python
parser.add_argument(
    "--visualize_grasp_bounding_box",
    "--visualize-grasp-bounding-box",
    "--visualize_grasp_bouding_box",
    "--visualize-grasp-bouding-box",
    dest="visualize_grasp_bounding_box",
    action="store_true",
    default=False,
    help="Draw the handle-centered grasp bounding box in the Isaac viewer.",
)
```

Delete it entirely (the whole block).

- [ ] **Step 7.3: Replace the hardcoded SHARPA `task_output_dir` mapping**

Find this block (around lines 43-47 in the simtoolreal original):

```python
task_output_dir = "sharpa_nutscrew_pick_place" if args_cli.task in {
    "sharpa_nutscrew_pick_place",
    "sharpa_nutscrew_pick_place_pretrain_like",
} else "simtoolreal_sharpa"
TASK_OUTPUT_ROOT = pathlib.Path(__file__).resolve().parent / "tasks" / task_output_dir
```

Replace it with:

```python
# Map the requested gym task id to the on-disk task package directory whose
# `agents/` folder holds its RL-Games YAML recipes. For this scaffold, all
# `Isaac-Forge-*-Ultra-v0` tasks live under `tasks/forge/`. Generalize when
# adding more task packages (see todos.md: "Multi-task agents-dir resolver").
def _task_subdir(task_name: str | None) -> str:
    if task_name and task_name.startswith("Isaac-Forge-") and task_name.endswith("-Ultra-v0"):
        return "forge"
    raise ValueError(
        f"Unknown task id {task_name!r}. Register it in forge_ultra/tasks/<pkg>/__init__.py "
        f"and extend _task_subdir() to map its id to <pkg>."
    )


task_output_dir = _task_subdir(args_cli.task)
TASK_OUTPUT_ROOT = pathlib.Path(__file__).resolve().parent / "tasks" / task_output_dir
```

- [ ] **Step 7.4: Replace the simtoolreal task imports with forge**

Find these two lines (around lines 73-74 in the simtoolreal original):

```python
import simtoolreal_lab.tasks.sharpa_nutscrew_pick_place.gym_setup  # noqa: F401
import simtoolreal_lab.tasks.simtoolreal_sharpa.gym_setup  # noqa: F401
```

Replace with:

```python
import forge_ultra.tasks.forge  # noqa: F401  # register Isaac-Forge-*-Ultra-v0
```

- [ ] **Step 7.5: Replace `_task_agents_dir` with a forge-aware version**

Find this function (around lines 80-83 in the simtoolreal original):

```python
def _task_agents_dir(task_name: str | None) -> pathlib.Path:
    if task_name in {"sharpa_nutscrew_pick_place", "sharpa_nutscrew_pick_place_pretrain_like"}:
        return TASKS_DIR / "sharpa_nutscrew_pick_place" / "agents"
    return TASKS_DIR / "simtoolreal_sharpa" / "agents"
```

Replace with:

```python
def _task_agents_dir(task_name: str | None) -> pathlib.Path:
    """Return the on-disk agents/ directory for a given gym task id.

    For this scaffold, all `Isaac-Forge-*-Ultra-v0` ids resolve to
    `tasks/forge/agents`. See todos.md: "Multi-task agents-dir resolver".
    """
    return TASKS_DIR / _task_subdir(task_name) / "agents"
```

(This reuses the `_task_subdir` helper added in Step 7.3.)

- [ ] **Step 7.6: Rename the SimToolReal RL-Games wrappers**

Find these two class declarations (around lines 170 and 185):

```python
class SimToolRealRlGamesVecEnvWrapper(RlGamesVecEnvWrapper):
```

```python
class SimToolRealRlGamesGpuEnv(RlGamesGpuEnv):
```

Rename both, and rename every usage in the file. Easiest path: do a literal text replace, file-wide:

| was | becomes |
|---|---|
| `SimToolRealRlGamesVecEnvWrapper` | `ForgeUltraRlGamesVecEnvWrapper` |
| `SimToolRealRlGamesGpuEnv` | `ForgeUltraRlGamesGpuEnv` |

Both classes appear in the class definition (once each) and in their usage sites (the two `env = ...` and `vecenv.register(...)` lines near lines 271-273 of the original). All four occurrences must be updated.

- [ ] **Step 7.7: Make the `--visualize_grasp_bounding_box` usage block tolerant of forge**

Find this block (around line 214 of the simtoolreal original):

```python
    if args_cli.visualize_grasp_bounding_box:
        env_cfg.debug_grasp_bounding_box = True
    _apply_object_selection(env_cfg)
```

Delete the first two lines (the visualize block — `args_cli.visualize_grasp_bounding_box` no longer exists after Step 7.2). Keep `_apply_object_selection(env_cfg)` but wrap it in a `hasattr` guard so it no-ops for forge (which doesn't define `apply_object_selection`):

Replace those three lines with:

```python
    cfg_module = importlib.import_module(env_cfg.__class__.__module__)
    if hasattr(cfg_module, "apply_object_selection"):
        cfg_module.apply_object_selection(env_cfg)
```

This preserves the simtoolreal-style `apply_object_selection` hook for env-cfg modules that define it (see todos.md), while keeping forge runnable.

- [ ] **Step 7.8: Remove the now-redundant `_apply_object_selection` helper**

The helper at the top of the file (around lines 90-92 of the simtoolreal original) becomes redundant once Step 7.7 inlines the hasattr-guarded equivalent. Delete this whole function:

```python
def _apply_object_selection(env_cfg) -> None:
    cfg_module = importlib.import_module(env_cfg.__class__.__module__)
    cfg_module.apply_object_selection(env_cfg)
```

The `import importlib` at the top stays — it's still used by the inlined block.

- [ ] **Step 7.9: Update the script docstring**

Find the top-of-file docstring (line 1 after the future import in the simtoolreal copy):

```python
"""Train Isaac Lab tasks with the vendored reference RL-Games fork."""
```

Replace with:

```python
"""Train forgeUltra tasks with the vendored SAPO RL-Games fork.

This is the simtoolreal-adapted training entry point. It mirrors
`forge_ultra/train.py` (the upstream NVIDIA IsaacLab rl_games script) but
adds: SAPO-aware env wrappers (`ForgeUltraRlGames*`), an `--agent_cfg`
flag for loading arbitrary YAML recipes from a task's `agents/` dir,
`env.<dotted.key>=value` / `agent.<dotted.key>=value` CLI overrides, and
the vendored `rl_games/` SAPO fork on `sys.path`.

See todos.md for the open question of converging the two entry points.
"""
```

- [ ] **Step 7.10: Sanity-check the file parses as Python**

Run:
```bash
/home/carsten.oertel/code/lab232/bin/python -c "import ast; ast.parse(open('/home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py').read()); print('parses ok')"
```

Expected output:
```
parses ok
```

- [ ] **Step 7.11: Verify no simtoolreal-specific names remain in code**

Run:
```bash
grep -n "simtoolreal\|sharpa\|SimToolReal\|visualize_grasp" /home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py
```

Expected output: at most ONE match — line 3 of the file (a docstring pointer "This is the simtoolreal-adapted training entry point..." that we intentionally kept as a historical reference). No matches in code, imports, identifiers, or paths. If you see any match outside the top-of-file docstring, that's a real issue.

---

## Task 8: Adapt simtoolreal `play_rl_games.py` for forge

**Files:**
- Create (copy + targeted edits): `/home/carsten.oertel/code/forgeUltra/forge_ultra/play_rl_games.py` (from `/home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/play_rl_games.py`)

This is the smaller sibling of Task 7. The play script has fewer simtoolreal-specific bits.

- [ ] **Step 8.1: Copy the simtoolreal play script**

Run:
```bash
cp /home/carsten.oertel/code/simtoolreal_isaacsim/simtoolreal_lab/play_rl_games.py \
   /home/carsten.oertel/code/forgeUltra/forge_ultra/play_rl_games.py
```

- [ ] **Step 8.2: Change the default `--task` value**

Find this line (around line 18):

```python
parser.add_argument("--task", type=str, default="simtoolreal_sharpa", help="Gym task id.")
```

Replace with:

```python
parser.add_argument("--task", type=str, default="Isaac-Forge-PegInsert-Ultra-v0", help="Gym task id.")
```

- [ ] **Step 8.3: Replace the simtoolreal task imports**

Find these two lines (around lines 45-46):

```python
import simtoolreal_lab.tasks.sharpa_nutscrew_pick_place.gym_setup  # noqa: F401
import simtoolreal_lab.tasks.simtoolreal_sharpa.gym_setup  # noqa: F401
```

Replace with:

```python
import forge_ultra.tasks.forge  # noqa: F401  # register Isaac-Forge-*-Ultra-v0
```

- [ ] **Step 8.4: Rename the SimToolReal RL-Games wrappers**

Apply the same rename as Step 7.6 to this file:

| was | becomes |
|---|---|
| `SimToolRealRlGamesVecEnvWrapper` | `ForgeUltraRlGamesVecEnvWrapper` |
| `SimToolRealRlGamesGpuEnv` | `ForgeUltraRlGamesGpuEnv` |

Both classes and all their usages need updating (typically the two class definitions near line 49 and 60, and two usages near line 186-188).

- [ ] **Step 8.5: Update the script docstring**

If the file has a top-of-file docstring referencing simtoolreal, replace it with:

```python
"""Play (replay / evaluate) forgeUltra task checkpoints with the vendored SAPO RL-Games fork.

Companion to `forge_ultra/train_rl_games.py`. Mirrors the simtoolreal play
script with SAPO-aware wrappers but generalized for forge.
"""
```

(If the original file has no docstring, just add this one at the top after any `from __future__` line.)

- [ ] **Step 8.6: Sanity-check the file parses**

Run:
```bash
/home/carsten.oertel/code/lab232/bin/python -c "import ast; ast.parse(open('/home/carsten.oertel/code/forgeUltra/forge_ultra/play_rl_games.py').read()); print('parses ok')"
```

Expected output:
```
parses ok
```

- [ ] **Step 8.7: Verify no simtoolreal-specific names remain**

Run:
```bash
grep -n "simtoolreal\|sharpa\|SimToolReal" /home/carsten.oertel/code/forgeUltra/forge_ultra/play_rl_games.py
```

Expected output: (empty — no lines printed)

---

## Task 9: Write `README.md`

**Files:**
- Create: `/home/carsten.oertel/code/forgeUltra/README.md`

- [ ] **Step 9.1: Write the README**

Content (write exactly as below):

````markdown
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
````

- [ ] **Step 9.2: Verify the README exists**

Run:
```bash
ls -la /home/carsten.oertel/code/forgeUltra/README.md
```

Expected: file present, non-zero size.

---

## Task 10: Write `todos.md`

**Files:**
- Create: `/home/carsten.oertel/code/forgeUltra/todos.md`

- [ ] **Step 10.1: Write the todos file**

Write `/home/carsten.oertel/code/forgeUltra/todos.md` with exactly this content:

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
```

- [ ] **Step 10.2: Verify the file is present**

Run:
```bash
head -3 /home/carsten.oertel/code/forgeUltra/todos.md
```

Expected output:
```
# forgeUltra — open questions

## Training script consolidation
```

---

## Task 11: Install the package and run the import-only smoke test

**Files (none modified — verification only):**

- [ ] **Step 11.1: Install in editable mode**

Run:
```bash
cd /home/carsten.oertel/code/forgeUltra && \
  /home/carsten.oertel/code/lab232/bin/python -m pip install -e .
```

Expected: install completes without errors. Final line should be something like `Successfully installed forge-ultra-0.1.0` or `Successfully installed forge_ultra-0.1.0`.

- [ ] **Step 11.2: Run the import-only smoke test**

This deliberately does NOT launch Isaac Sim — it just confirms the package structure imports cleanly. Pure Python; no `pxr` / `omni` needed.

Run:
```bash
/home/carsten.oertel/code/lab232/bin/python -c "
import forge_ultra
import forge_ultra.tasks
print('forge_ultra package import: ok')
"
```

Expected output:
```
forge_ultra package import: ok
```

Note: importing `forge_ultra.tasks.forge` or `forge_ultra.assets.kuka_sharpa` would trigger isaaclab imports that require Isaac Sim to be running (via `AppLauncher`), so we don't do that here. The full end-to-end check happens in Task 12 inside the AppLauncher context.

- [ ] **Step 11.3: Confirm the package is discoverable from the env**

Run:
```bash
/home/carsten.oertel/code/lab232/bin/python -c "import forge_ultra; print(forge_ultra.__file__)"
```

Expected output: an absolute path ending in `/home/carsten.oertel/code/forgeUltra/forge_ultra/__init__.py` (confirms the editable install pointed at our source tree, not some site-packages copy).

---

## Task 12: End-to-end smoke test — train each entry point for 2 iterations

**Files (none modified — verification only):**

This is the final acceptance test from the spec. Both training scripts should construct the env, resolve the gym id, hand off to `rl_games`, and run two PPO iterations before exiting. We don't care about reward numbers — only that nothing crashes through the full bring-up.

These commands launch Isaac Sim and will take 1–3 minutes each on first run (JIT warp kernel compile, USD load). Run them sequentially, not in parallel.

- [ ] **Step 12.1: Smoke-train through upstream `train.py`**

Run:
```bash
cd /home/carsten.oertel/code/forgeUltra && \
  /home/carsten.oertel/code/lab232/bin/python forge_ultra/train.py \
    --task Isaac-Forge-PegInsert-Ultra-v0 \
    --headless \
    --num_envs 16 \
    --max_iterations 2
```

Expected: process runs to completion (exits cleanly after the 2 PPO epochs). Look for `epoch: 2` (or similar end-of-training log line) in the output. Acceptable: any tqdm-style training progress lines from rl_games, no Python tracebacks.

Common failure modes and what they indicate:
- `gym.error.NameNotFound: Environment ... doesn't exist` → Task 5 gym id rename did not take. Re-check Step 5.5 / 5.7.
- `ModuleNotFoundError: No module named 'forge_ultra.tasks.factory'` → Task 5 import rewrite missed. Re-check Step 5.3 / 5.4 / 5.6.
- `ModuleNotFoundError: No module named 'isaaclab_tasks'` → wrong env. Confirm you're using `/home/carsten.oertel/code/lab232/bin/python`.
- USD load errors mentioning `kuka_sharpa` → unexpected; this scaffold should NOT load the kuka_sharpa USD anywhere (forge still uses Franka). Investigate.

- [ ] **Step 12.2: Smoke-train through simtoolreal-adapted `train_rl_games.py`**

Run:
```bash
cd /home/carsten.oertel/code/forgeUltra && \
  /home/carsten.oertel/code/lab232/bin/python forge_ultra/train_rl_games.py \
    --task Isaac-Forge-PegInsert-Ultra-v0 \
    --headless \
    --num_envs 16 \
    --max_iterations 2 \
    agent.wandb_activate=False
```

Expected: same kind of clean exit after 2 epochs. The vendored `rl_games` fork should be picked up (an `[INFO]` or similar line near the top mentioning the fork path is a good signal but not strictly required).

Common failure modes specific to this script:
- `AttributeError: module 'forge_ultra.tasks.forge.forge_env_cfg' has no attribute 'apply_object_selection'` → Step 7.7's `hasattr` guard didn't take. Re-check.
- `ValueError: Unknown task id ...` from `_task_subdir` → Step 7.3's resolver isn't matching. Confirm task name spelling.
- `NameError: name 'SimToolReal...' is not defined` → Step 7.6 rename incomplete; re-run the search/replace.

- [ ] **Step 12.3: Confirm both succeeded**

If both Step 12.1 and Step 12.2 completed without traceback, the scaffold is functional. Print:

```
forgeUltra scaffold: VERIFIED.
  - upstream train.py:        OK
  - simtoolreal-adapted train_rl_games.py: OK
  - kuka_sharpa assets present in forge_ultra/assets/kuka_sharpa/, not yet wired into forge env
  - todos.md tracks the open questions for follow-up specs
```

---

## Self-review notes

Run this checklist against the spec (`docs/superpowers/specs/2026-05-28-forgeUltra-design.md`) before declaring the plan ready.

**Spec coverage:**
- "Layout" section → covered by Tasks 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.
- "File copy plan: verbatim copies" → Tasks 2 (kuka_sharpa), 3 (rl_games), 4 (factory), 5 (forge), 6 (upstream scripts), 7/8 (simtoolreal scripts as starting points).
- "Edits: forge_env_cfg.py / forge_env.py / forge/__init__.py" → Task 5 steps 5.3, 5.4, 5.5.
- "Edits: factory/__init__.py" → Task 4 step 4.3.
- "Edits: forge_ultra/__init__.py, tasks/__init__.py" → Task 1 steps 1.2-1.4.
- "Edits: kuka_sharpa/config.yaml" → Task 2 step 2.3.
- "Edits: upstream train.py and play.py" → Task 6 steps 6.2, 6.3.
- "Edits: adapted train_rl_games.py / play_rl_games.py" → Tasks 7 and 8.
- "setup.py" / "pyproject.toml" → Task 1 steps 1.5, 1.6.
- "README.md" → Task 9.
- "todos.md" → Task 10.
- "Portability rules" → enforced inline (Task 2 step 2.3 rewrites the only absolute path; verification step 2.4 confirms no other `/home/carsten.oertel` strings).
- "What 'done' looks like" → Tasks 11 (install + import smoke) and 12 (end-to-end train smoke for both scripts).

**Placeholder scan:** no TBD / TODO / "fill in details" / "similar to Task N". Every code block contains the literal content to write.

**Type / name consistency:** `_task_subdir` defined in Step 7.3 and called in Step 7.5; `ForgeUltraRlGamesVecEnvWrapper` and `ForgeUltraRlGamesGpuEnv` consistently renamed across Steps 7.6 and 8.4; `Isaac-Forge-{PegInsert,GearMesh,NutThread}-Ultra-v0` gym ids consistent across Tasks 5, 6, 7, 8, 9, 12.

**Spec-to-plan gap I noticed:** the spec's success criterion (3) — the import-only smoke test — uses `from forge_ultra.assets.kuka_sharpa import KUKA_SHARPA_CFG`. But importing `kuka_sharpa.py` transitively imports `isaaclab.sim`, which requires the AppLauncher context. So Task 11 was downscoped to import just `forge_ultra` and `forge_ultra.tasks` (the pure-Python parents), and the deeper imports are covered indirectly by Task 12 (which runs inside AppLauncher). This is a minor deviation from the spec wording but matches its intent. Noted here so the executing agent doesn't try to "fix" it.
