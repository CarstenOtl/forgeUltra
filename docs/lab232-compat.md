# IsaacLab 2.3.2 compatibility notes

forgeUltra targets **IsaacLab v2.3.2** (the `lab232` uv env). simtoolreal's
upstream code was authored against **v2.2.1**. This document records the
deltas we ran into when porting, the fixes applied, and the convention for
handling future version bumps.

## Audit summary

A static diff of the isaaclab module surface used by `simtoolreal_sharpa`
env, the SAPO adapter scripts, and the vendored `rl_games` bridge was
performed between local v2.2.1 (`/home/carsten.oertel/code/IsaacLab/`) and
v2.3.2 (`/home/carsten.oertel/code/IsaacLab-v2.3.2/`) sources. It surfaced
**one breaking change**. Everything else was backwards-compatible —
additive optional fields, new methods, return-type annotation widenings.

## Breaking changes encountered

### 1. `isaaclab.utils.io.dump_pickle` removed in v2.3.2

**Symptom:**

```
ImportError: cannot import name 'dump_pickle' from 'isaaclab.utils.io'
```

**Cause:** v2.2.1 had a `pkl.py` module exporting `dump_pickle` and
`load_pickle`. v2.3.2 removed the file entirely; only `dump_yaml`,
`load_yaml`, and `load_torchscript_model` remain in `isaaclab.utils.io`.
simtoolreal's `train_rl_games.py` imports `dump_pickle` to write
`params/env.pkl` and `params/agent.pkl` for byte-exact replay by
`play_rl_games.py`.

**Fix:** Local shim at `forge_ultra/_isaaclab_compat.py` mirroring v2.2.1's
`dump_pickle` (creates parent dirs, appends `.pkl` extension, writes with
the default pickle protocol). `train_rl_games.py` imports from the compat
module instead of `isaaclab.utils.io`.

`play_rl_games.py` reads pickles via stdlib `pickle.load` directly (not
`load_pickle`), so no `load_pickle` shim is needed.

Spec: `docs/superpowers/specs/2026-05-29-isaaclab-232-compat-design.md`
Plan: `docs/superpowers/plans/2026-05-29-isaaclab-232-compat.md`
Commit: `041db18`

## Future-proofing convention

When upgrading IsaacLab further (3.x is on the roadmap — see `todos.md`):

1. Re-run the static API audit against the new version (same module list,
   below). The audit can be done with the modules listed in "Audit
   coverage" and the local sources at `/home/carsten.oertel/code/IsaacLab*`.
2. For each rename / removal / relocation: add a shim function to
   `forge_ultra/_isaaclab_compat.py`. Update the importing site to use
   the shim.
3. For each behavioral change (a method that now needs different setup,
   a class that no longer exists): edit the affected vendored file
   in-place. Tag the edit with a `# IsaacLab X.Y.Z:` comment so future
   readers see why the divergence exists.

The compat module is the canonical home for version-skew shims. Do not
scatter compat code through the call sites.

## Audit coverage

Modules diffed between v2.2.1 and v2.3.2 sources:

| Module | Status |
|---|---|
| `isaaclab.utils.io` | **broken** — see above |
| `isaaclab.envs.DirectRLEnv[Cfg]` | stable — 2 additive optional fields (`num_rerenders_on_reset`, `log_dir`) with defaults |
| `isaaclab.assets.{Articulation, RigidObject}[Cfg]` | stable — 2 new methods (`instantaneous_wrench_composer`, `permanent_wrench_composer`); old `set_external_force_and_torque` deprecated but still works |
| `isaaclab.scene.InteractiveSceneCfg` | stable — no deltas |
| `isaaclab.sensors.{ContactSensor, ContactSensorCfg}` | stable — 1 additive optional field (`track_friction_forces`) |
| `isaaclab.sim.spawners.from_files.*` | stable for us — tendon cfg renames `FixedTendons*→FixedTendon*` don't affect simtoolreal_sharpa |
| `isaaclab.sim.{SimulationCfg, PhysxCfg, RigidBodyMaterialCfg}` | stable — additive optional fields only |
| `isaaclab.utils.{math, dict, assets, configclass}` | stable — `retrieve_file_path`, `print_dict`, math utils (`quat_*`, `sample_uniform`, `saturate`), `configclass` all unchanged signatures |
| `isaaclab.app.AppLauncher` | stable |
| `isaaclab_rl.rl_games.{RlGamesGpuEnv, RlGamesVecEnvWrapper}` | stable — was a single `.py` file in 2.2.1, now a package in 2.3.2, but import path preserved via package `__init__.py` re-exports; only return-type annotations widened (`Box → Box | Dict`); class behavior identical |
| `isaaclab_tasks.utils.{hydra, parse_cfg}` | stable — no semantic deltas |

## Vendoring bugs discovered during this work (not 2.3.2-related)

### `simtoolreal_sharpa/gym_setup.py` had hardcoded `simtoolreal_lab.*` paths

The initial vendoring of the simtoolreal_sharpa task rewrote cross-package
Python imports (e.g. `from simtoolreal_lab.assets.kuka_sharpa import …`
→ `from forge_ultra.assets.kuka_sharpa import …`) but missed two
`gym.register(...)` `entry_point` string literals in `gym_setup.py`.
`gym.make("simtoolreal_sharpa")` tried to import `simtoolreal_lab.tasks.…`
at runtime and failed with `ModuleNotFoundError`.

Fixed by templating both `entry_point` strings as
`f"{__package__}.simtoolreal_sharpa_env:SimToolRealSharpaEnv"`, mirroring
the forge vendoring pattern (which used `f"{__name__}…"` from the package
`__init__.py`). This prevents the same oversight if the package is
renamed later.

Commit: `af6b2ef`

## Run-time considerations after compat work

These aren't 2.3.2 compat issues — they're properties of the SAPO recipe
itself — but they bit us during smoke testing so they're worth recording:

**SAPO block-size constraint.** `train_rl_games.py` for `simtoolreal_sharpa`
hits an assertion in `rl_games/common/a2c_common.py`:

```python
assert self.num_actors % self.intr_coef_block_size == 0
```

The SAPO YAML's `expl_coef_block_size: 256` was tuned for `1536 envs / 256
block_size = 6 blocks` (simtoolreal's canonical recipe). Other valid
pairings: `1024 / 256` (4 blocks), `512 / 256` (2 blocks). A `--num_envs 16`
smoke run fails this assertion unless you also pass
`agent.params.config.expl_coef_block_size=16` (1 block, which simtoolreal's
README documents as fine for debug but produces a checkpoint that won't
replay against six-block SAPO).

**`zero_agent.py` forge_kuka-specific diagnostics.** The repo's
`zero_agent.py` includes diagnostic blocks that access `env.unwrapped._robot`
and other forge_kuka-private attributes. When pointed at `simtoolreal_sharpa`
(which exposes `env.unwrapped.robot` instead), those blocks would
`AttributeError`. Guarded with `if hasattr(env.unwrapped, "_robot"):` so
the simulation loop still runs on any task. `random_agent.py` only uses
generic env attributes and works on either task unchanged.
