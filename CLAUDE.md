# forgeUltra — Claude project guidance

Project-specific facts for working in this repo. User-level rules in
`~/.claude/CLAUDE.md` still apply.

## Python env

Always use `/home/carsten.oertel/code/lab232/bin/python` (uv env, IsaacLab
v2.3.2, Python 3.11). The repo is installed editable into this env. Do not
suggest `python` without the full path — the user's shell PATH may resolve
to a different interpreter.

## What this repo is (and isn't)

Scaffold of the IsaacLab `forge` task, with `factory` vendored as its
Python base and the KUKA + SHARPA assets staged in `forge_ultra/assets/`
for a planned Franka→kuka_sharpa swap. **Forge still runs on Franka** in
this iteration — kuka_sharpa is present but not wired into any env cfg.
The swap is an explicit follow-up spec, tracked in `todos.md`.

## Two training entry points (ship both, intentionally)

| Script | Role | When to use |
|---|---|---|
| `forge_ultra/train.py` / `play.py` | upstream NVIDIA IsaacLab rl_games scripts + one line registering our gym ids | vanilla PPO, full upstream features (PBT, MultiObserver, Ray, `--export_io_descriptors`, `--track` wandb) |
| `forge_ultra/train_rl_games.py` / `play_rl_games.py` | simtoolreal-adapted, generalized for forge | SAPO-aware wrappers (`ForgeUltraRlGames*`), `--agent_cfg <name|path>`, `env.<dotted.key>=value` / `agent.<dotted.key>=value` CLI overrides, per-task `tasks/<task>/outputs/...` layout, vendored SAPO `rl_games/` fork on `sys.path` |

Don't unify these without a spec — `todos.md` tracks the open question.

## Tasks and gym ids

Two task families are vendored:

**forge** (vendored from IsaacLab v2.3.2 `isaaclab_tasks.direct.forge`):
- `Isaac-Forge-PegInsert-Ultra-v0`
- `Isaac-Forge-GearMesh-Ultra-v0`
- `Isaac-Forge-NutThread-Ultra-v0`

Upstream's `Isaac-Forge-*-Direct-v0` family also coexists on the import
path (both upstream `isaaclab_tasks` and our vendored copy register their
own). Either family trains through either entry-point script.

**simtoolreal_sharpa** (vendored from `simtoolreal_isaacsim` @ 2b210ec — KUKA + SHARPA in-hand manipulation, SAPO-trained):
- `simtoolreal_sharpa`
- `simtoolreal_sharpa_pretrain_like`

Ids kept verbatim (no `-Ultra-v0` suffix) for 1:1 comparability against
upstream simtoolreal results. Task lives at
`forge_ultra/tasks/simtoolreal_sharpa/` and depends on
`forge_ultra.assets.kuka_sharpa` and `forge_ultra.assets.dextoolbench_usd`.
Trains via either entry-point; SAPO recipes are in
`tasks/simtoolreal_sharpa/agents/rl_games_sapo*.yaml` and require
`train_rl_games.py` (the vendored SAPO fork on sys.path).

`train_rl_games.py`'s `_task_subdir()` maps both id families to their
on-disk subdirs. When you add another task package, extend that helper.

## Vendored code invariants

When editing files under `forge_ultra/tasks/forge/` or `forge_ultra/tasks/factory/`:

- **Never** add new `from isaaclab_tasks.direct.factory...` imports.
  All forge→factory references go through the vendored copy via
  `from ..factory...` relative imports. Currently in:
  `forge_env_cfg.py:11`, `forge_env.py:12-13`, `forge_tasks_cfg.py:8`.
- `tasks/factory/__init__.py` intentionally has NO `gym.register(...)`
  calls — registering would double up with upstream `isaaclab_tasks`
  and raise `NameAlreadyRegistered`. Factory is consumed only as a
  Python base for forge.
- All other forge/factory files (`forge_events.py`, `forge_utils.py`,
  `factory_*.py`, `agents/*.yaml`) are byte-identical to IsaacLab v2.3.2
  source. Diverge intentionally only — and update the relevant todos
  entry if you do.

## IsaacLab version targeting

The repo targets IsaacLab v2.3.2 (the `lab232` env). Version-skew shims
for APIs that changed between simtoolreal's 2.2.1 baseline and 2.3.2 live
in `forge_ultra/_isaaclab_compat.py`. When you hit an `ImportError` or
`AttributeError` from a vendored script/env against a new isaaclab
version, add a shim there rather than scattering compat code through the
call sites.

## Vendored SAPO `rl_games/` fork

`forge_ultra/rl_games/` is a verbatim copy from simtoolreal. The fork has
a hardcoded `/home/trrrrr/...` default in `rl_games/envs/diambra/diambra.py:16`
that is **intentional** — diambra envs aren't on forge's path, and
scrubbing would diverge our fork from simtoolreal's. Leave it alone unless
the user asks for a fork-cleanup pass. Tracked in `todos.md`.

`train_rl_games.py` does `sys.path.insert(0, str(VENDORED_RL_GAMES))`
before any `from rl_games import ...`, so the vendored fork wins over any
pip-installed `rl_games`. `train.py` does NOT — it picks up whatever
`rl_games` `lab232` provides.

## Asset paths

All in-repo path resolution must stay portable:

- Python files: `os.path.dirname(__file__)` or
  `pathlib.Path(__file__).resolve().parent`. No `/home/...`, no
  `cwd`-relative paths.
- `forge_ultra/assets/kuka_sharpa/config.yaml`'s `asset_path` and
  `usd_dir` are intentionally relative (`urdf/...` and `.`). Loaders
  resolve them relative to the file's own directory. Do not "fix" these
  to absolutes.
- URDF `package://...` mesh refs use ROS-style resolution and are not
  broken by relocation. Confirmed clean during scaffold.

## Run policy

Per the user's global CLAUDE.md: do not auto-launch Isaac Sim training
runs via Bash. Print the command for the user instead. Fast read-only
greps, `ast.parse` sanity, `pip install -e .` (no-dep, sub-30s) are fine
to run directly.

## Git policy

No git in this iteration — user explicitly opted out. Don't run
`git init`, `git add`, `git commit`, or suggest committing changes
unless the user changes their mind.

## Where the design lives

- Spec: `docs/superpowers/specs/2026-05-28-forgeUltra-design.md`
- Plan: `docs/superpowers/plans/2026-05-28-forgeUltra-scaffold.md`
- Open follow-ups: `todos.md`

When asked "why did we do X this way", check the spec first — most
design decisions have rationale recorded there.
