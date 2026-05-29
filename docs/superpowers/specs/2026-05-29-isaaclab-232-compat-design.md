# IsaacLab 2.3.2 Compatibility for SAPO + simtoolreal_sharpa env

**Date:** 2026-05-29
**Status:** Approved, ready for implementation plan
**Target env:** `/home/carsten.oertel/code/lab232` (uv env on IsaacLab v2.3.2, Python 3.11)

## Goal

Get the vendored `simtoolreal_sharpa` task (KUKA + SHARPA in-hand manipulation, SAPO-trained) and the simtoolreal-adapted training/play scripts (`train_rl_games.py`, `play_rl_games.py`) running cleanly on IsaacLab v2.3.2.

The simtoolreal codebase was authored against IsaacLab v2.2.1. The user's `lab232` uv env runs v2.3.2. The earlier import error (`ImportError: cannot import name 'dump_pickle' from 'isaaclab.utils.io'`) is the first symptom of this version skew. This spec is the focused upgrade pass to surface and resolve all such breakages so the SAPO + env pipeline is trainable in 2.3.2.

## Static API audit (already done)

A diff of the isaaclab module surface the vendored simtoolreal_sharpa env, SAPO bridge, and adapter scripts touch was performed between local IsaacLab 2.2.1 (`/home/carsten.oertel/code/IsaacLab/`) and 2.3.2 (`/home/carsten.oertel/code/IsaacLab-v2.3.2/`) sources. Findings:

| Module | Status | Notes |
|---|---|---|
| `isaaclab.utils.io` | **broken** | `pkl.py` removed → `dump_pickle`, `load_pickle` no longer importable. Only `dump_yaml`, `load_yaml`, `load_torchscript_model` remain. |
| `isaaclab.envs.DirectRLEnv[Cfg]` | stable | 2 new optional cfg fields (`num_rerenders_on_reset`, `log_dir`) with defaults. No method changes. |
| `isaaclab.assets.{Articulation, RigidObject}[Cfg]` | stable | 2 new methods (`*_wrench_composer`); old `set_external_force_and_torque` deprecated but still works. |
| `isaaclab.scene.InteractiveSceneCfg` | stable | no deltas |
| `isaaclab.sensors.{ContactSensor, ContactSensorCfg}` | stable | 1 new optional cfg field (`track_friction_forces`) |
| `isaaclab.sim.spawners.from_files.*` | stable for us | tendon cfg renames `FixedTendons*→FixedTendon*` don't affect simtoolreal_sharpa (confirmed by grep) |
| `isaaclab.sim.{SimulationCfg, PhysxCfg, RigidBodyMaterialCfg}` | stable | additive optional fields only |
| `isaaclab.utils.{math, dict, assets, configclass}` | stable | `retrieve_file_path`, `print_dict`, math utils, `configclass` all unchanged signatures |
| `isaaclab.app.AppLauncher` | stable | no signature deltas |
| `isaaclab_rl.rl_games.{RlGamesGpuEnv, RlGamesVecEnvWrapper}` | stable | was `rl_games.py` file in 2.2.1, now a package in 2.3.2, but `from isaaclab_rl.rl_games import …` path preserved via package `__init__.py` re-exports. Return type annotations widened (`Box → Box | Dict`); usage unaffected. |
| `isaaclab_tasks.utils.{hydra, parse_cfg}` | stable | no semantic deltas |

**Conclusion:** The 2.3.2 upgrade work for our vendored code is narrow. Exactly one symbol removal needs handling (`dump_pickle`); `load_pickle` is unused by us (our `play_rl_games.py` reads pickles via stdlib `pickle.load`). All other deltas in the touched surface are backwards-compatible.

## Out of scope

- Behavioral parity with simtoolreal's 2.2.1 training curves. Static API compatibility ≠ reward-curve identity. If long runs in 2.3.2 reveal divergent dynamics from simtoolreal's results, that's a separate research spec.
- Bumping further to IsaacLab 3.x. Tracked in `todos.md` for later.
- Bringing in features added in 2.3 / 2.4 (e.g. wrench composers, fabric backend) — additive, not required for the migration.
- Any forge work (forge already trains successfully on 2.3.2 via the upstream NVIDIA path).

## Design

### Compat module

A new file `forge_ultra/_isaaclab_compat.py` collects all shims for IsaacLab version skew. Module name is underscore-prefixed to signal "internal use by vendored scripts/envs, not a public API."

Initial contents (one symbol):

```python
"""Shims for IsaacLab API drift across versions.

Currently targeting IsaacLab v2.3.2 (the `lab232` uv env). Add a shim here
whenever a vendored script/env imports a symbol that was renamed, removed,
or relocated between IsaacLab versions. Keeps the version delta isolated
and easy to diff against a future version-bump PR.
"""

import os
import pickle


def dump_pickle(filename: str, data) -> None:
    """Reproduces v2.2.1 isaaclab.utils.io.dump_pickle (removed in v2.3.2).

    Mirrors the v2.2.1 implementation's convention: append `.pkl` if missing,
    create parent directories along the path, write with the default pickle
    protocol. simtoolreal's `train_rl_games.py` imports `dump_pickle` from
    `isaaclab.utils.io` directly to write `params/env.pkl` and
    `params/agent.pkl` for byte-exact replay by `play_rl_games.py`.
    """
    if not filename.endswith(".pkl"):
        filename += ".pkl"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        pickle.dump(data, f)
```

### `train_rl_games.py` edits

Replace the inline `dump_pickle` helper (currently at line 102) with an import from the compat module.

The current top-of-file stdlib import block (lines 15-22):

```python
import argparse
import importlib
import math
import os
import pathlib
import pickle
import sys
import time
```

becomes (drop `pickle` — no longer needed in this file):

```python
import argparse
import importlib
import math
import os
import pathlib
import sys
import time
```

The current isaaclab import (line 82):

```python
from isaaclab.utils.io import dump_yaml
```

becomes (add the compat import on a new line):

```python
from isaaclab.utils.io import dump_yaml

from forge_ultra._isaaclab_compat import dump_pickle
```

The inline helper definition (currently lines ~100-117, the `def dump_pickle(filename, data) -> None: …` block plus the surrounding blank lines) is deleted entirely.

### `play_rl_games.py` edits

None required. The script reads pickles via stdlib `pickle.load(f)` directly (no `load_pickle` import from isaaclab), and writes no pickles. Pickled cfgs produced by `train_rl_games.py` via the compat-module `dump_pickle` are byte-compatible with the existing read path.

### `CLAUDE.md` edits

Add a short subsection in the "Vendored code invariants" block:

```markdown
## IsaacLab version targeting

The repo targets IsaacLab v2.3.2 (the `lab232` env). Version-skew shims
for APIs that changed between simtoolreal's 2.2.1 baseline and 2.3.2 live
in `forge_ultra/_isaaclab_compat.py`. When you hit an `ImportError` or
`AttributeError` from a vendored script/env against a new isaaclab
version, add a shim there rather than scattering compat code through the
call sites.
```

### `todos.md` edits

Add a new section near the end of the file:

```markdown
## IsaacLab version targeting

- [ ] Bump to IsaacLab 3.x when stable — re-run the static API audit
      against the new version, port any new deltas into
      `forge_ultra/_isaaclab_compat.py`.
- [ ] Drop `_isaaclab_compat.dump_pickle` if 3.x re-adds it to
      `isaaclab.utils.io` (unlikely but check).
- [ ] Long-run reward-curve parity check vs simtoolreal_isaacsim's 2.2.1
      baseline — non-blocking, defer until we have a stable 2.3.2
      training pipeline.
```

## Verification

### Stage 1 — Smoke test (gating)

```bash
cd /home/carsten.oertel/code/forgeUltra && \
  /home/carsten.oertel/code/lab232/bin/python forge_ultra/train_rl_games.py \
    --task simtoolreal_sharpa \
    --headless \
    --num_envs 16 \
    --max_iterations 2 \
    agent.wandb_activate=False
```

Pass criteria:

- Process runs to clean exit (no traceback)
- No `ImportError` / `AttributeError` from isaaclab imports
- No `TypeError` from a renamed cfg field or method signature change
- Both PPO epochs complete (look for `epoch: 2` or rl_games' equivalent end-of-epoch log)
- `tasks/simtoolreal_sharpa/outputs/<date>/<time>/params/env.pkl` exists and is non-empty
- `tasks/simtoolreal_sharpa/outputs/<date>/<time>/params/agent.pkl` exists and is non-empty
- The pickles open cleanly with stdlib pickle: `python -c "import pickle; pickle.load(open('.../env.pkl','rb'))"` returns a config object

### Stage 2 — Behavioral sanity (catches runtime drift the static audit misses)

If Stage 1 passes, glance at the first few epochs' rl_games console output:

- iterations/sec > 0 (not stalled)
- value/policy loss are finite (no NaN)
- A `nn/Sharpa.pth` (or whatever rl_games names it for this task — see `full_experiment_name` in the SAPO YAML) file gets written

### Stage 3 — Out of scope, deferred

Long-run reward-curve parity vs simtoolreal_isaacsim's 2.2.1 baseline. Tracked in `todos.md`. Not a gate for this spec.

### Failure handling

If Stage 1 surfaces a NEW error not caught in the static audit (i.e. a runtime behavioral break in an isaaclab API), the fix follows the hybrid strategy:

- **Trivial rename/removal/relocation** → add a shim to `forge_ultra/_isaaclab_compat.py`. Update the importing script/env to import from the compat module. Re-run.
- **Behavioral change** (e.g. a method now requires different setup, a class no longer exists) → edit the vendored env file in-place. Document the change in a comment with `# IsaacLab 2.3.2: <what changed>`. Re-run.

One fix per error, no batching. Stops being scope creep at three: if three additional fixes are required, pause and re-evaluate whether the hybrid strategy is still the right approach (architectural question, not a fix).

## "Done" definition

1. `forge_ultra/_isaaclab_compat.py` exists with the `dump_pickle` shim.
2. `train_rl_games.py` imports `dump_pickle` from the compat module; the inline helper is gone; `import pickle` is removed from its top imports.
3. `play_rl_games.py` is unchanged (already 2.3.2-compatible via stdlib pickle).
4. `CLAUDE.md` and `todos.md` are updated as specified.
5. The Stage 1 smoke command above runs to clean exit and produces readable `env.pkl` / `agent.pkl` files.
6. The Stage 2 behavioral sanity passes (finite losses, checkpoint written).

No other changes. Forge training, the upstream NVIDIA scripts, the vendored factory/forge tasks, and the kuka_sharpa assets are untouched.
