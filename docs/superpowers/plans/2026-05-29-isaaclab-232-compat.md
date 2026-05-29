# IsaacLab 2.3.2 Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the inline `dump_pickle` shim in `train_rl_games.py` into a dedicated `forge_ultra/_isaaclab_compat.py` module, then verify the `simtoolreal_sharpa` task trains in IsaacLab v2.3.2 via a 2-epoch smoke run.

**Architecture:** A single internal compat module collects all shims for IsaacLab API drift. Today it holds one symbol (`dump_pickle`) covering the only breaking change found in the 2.2.1 → 2.3.2 static API audit. The vendored `simtoolreal_sharpa` env and the simtoolreal-adapted train/play scripts use unchanged isaaclab APIs otherwise. Long-run reward parity vs simtoolreal's 2.2.1 baseline is out of scope; that's tracked as a follow-up in `todos.md`.

**Tech Stack:** Python 3.11, IsaacLab v2.3.2 (in `lab232` uv env), `isaaclab.utils.io`, `isaaclab_rl.rl_games`, vendored SAPO `rl_games/` fork.

**Spec:** `docs/superpowers/specs/2026-05-29-isaaclab-232-compat-design.md`

---

## Conventions for this plan

- **Python interpreter:** Always `/home/carsten.oertel/code/lab232/bin/python` — never bare `python`. The user's shell PATH may resolve elsewhere.
- **No TDD-style unit tests for this work.** The change is a code reorganization (move a helper function from one file to another) plus documentation. The meaningful verification is end-to-end: the file imports without error inside `train_rl_games.py`'s normal startup path. Tasks 5 and 6 cover that.
- **Long-running commands are surfaced for the user to run, not auto-executed.** Per the user's global CLAUDE.md, anything that boots Isaac Sim (Stages 1 + 2 of the spec) is printed for the user. The implementer runs only the fast checks (`ast.parse`, import-only smokes).
- **Git is in use.** The forgeUltra repo has `main` tracking `origin` at `git@github.com:CarstenOtl/forgeUltra.git`. Commit the work as one logical unit after the user confirms Stages 1 + 2 pass.

---

## Task 1: Create the compat module

**Files:**
- Create: `/home/carsten.oertel/code/forgeUltra/forge_ultra/_isaaclab_compat.py`

- [ ] **Step 1.1: Write the new compat module**

Use the Write tool to create `/home/carsten.oertel/code/forgeUltra/forge_ultra/_isaaclab_compat.py` with EXACTLY this content (everything between the OUTER quadruple backticks is the literal file content — the OUTER fences are prompt delimiters only):

````python
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
````

- [ ] **Step 1.2: Verify the file parses and the symbol is importable as pure Python**

```bash
/home/carsten.oertel/code/lab232/bin/python -c "
import ast
ast.parse(open('/home/carsten.oertel/code/forgeUltra/forge_ultra/_isaaclab_compat.py').read())
print('parses ok')
"
```
Expected output:
```
parses ok
```

```bash
/home/carsten.oertel/code/lab232/bin/python -c "
from forge_ultra._isaaclab_compat import dump_pickle
print('compat dump_pickle imported:', dump_pickle)
"
```
Expected output (the second token is the function repr; just confirm it's a function, not an error):
```
compat dump_pickle imported: <function dump_pickle at 0x...>
```

If `ModuleNotFoundError: No module named 'forge_ultra._isaaclab_compat'`, the package needs reinstalling — re-run `pip install -e .` from the repo root (the new module isn't picked up automatically by editable installs for fresh sibling files in some setuptools versions). Specifically:
```bash
cd /home/carsten.oertel/code/forgeUltra && /home/carsten.oertel/code/lab232/bin/python -m pip install -e . 2>&1 | tail -3
```
Then re-try the import. (For editable installs of `find_packages()`-based projects, new modules under an existing package usually get picked up without reinstall — but if not, this gets it.)

---

## Task 2: Wire `train_rl_games.py` to use the compat module

**Files:**
- Modify: `/home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py` (3 separate edits in 3 distinct file locations)

This task removes the inline `dump_pickle` helper from `train_rl_games.py` and replaces it with an import from the new compat module. Verify after each sub-step.

- [ ] **Step 2.1: Remove the now-unused `import pickle` from the stdlib imports block**

The current stdlib imports block (lines 15-22) contains:

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

Use the Edit tool to replace it with (drop the `import pickle` line):

```python
import argparse
import importlib
import math
import os
import pathlib
import sys
import time
```

Why: after Step 2.3 removes the inline `dump_pickle` function, no code in this file uses the `pickle` module directly. The compat module owns `pickle` now.

- [ ] **Step 2.2: Add the compat import after the existing isaaclab.utils.io import**

The current isaaclab import block has (around line 82):

```python
from isaaclab.utils.io import dump_yaml
```

Use the Edit tool to replace that single line with TWO lines (one blank line between them keeps the import visually grouped with isaaclab while flagging the compat origin):

```python
from isaaclab.utils.io import dump_yaml

from forge_ultra._isaaclab_compat import dump_pickle
```

To make `old_string` unique, include enough surrounding context — the previous and next import lines are:

```python
from isaaclab.utils.io import dump_pickle, dump_yaml
```
was already changed in an earlier session to:
```python
from isaaclab.utils.io import dump_yaml
```

So your Edit's `old_string` should match the CURRENT state (line 82). If you grep first to find the unique surrounding context, do:

```bash
grep -nB1 -A1 "from isaaclab.utils.io import dump_yaml" /home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py
```

Use the printed context lines around line 82 to disambiguate the Edit's `old_string`.

- [ ] **Step 2.3: Delete the inline `dump_pickle` function entirely**

The inline definition currently lives at lines 102-116 (the `def dump_pickle(...):` block, including its docstring and body). The block boundaries are:
- Just above: a blank line (line 101) below the `return TASKS_DIR / _task_subdir(task_name) / "agents"` line of `_task_agents_dir`.
- Just below: a blank line (line 117) above `def _load_agent_cfg_override(agent_cfg_path: str) -> dict:` (line 119).

Use the Edit tool to delete the function. Concretely, replace this block:

```python


def dump_pickle(filename: str, data) -> None:
    """Save data as a pickle file. Local shim for IsaacLab v2.3.2 compat.

    `isaaclab.utils.io` in v2.3.2 only exports `dump_yaml` (the upstream
    pre-v3 cut never added `dump_pickle`). simtoolreal's train script
    inherits this dependency for byte-exact env_cfg / agent_cfg replay
    via `play_rl_games.py`. We mirror `dump_yaml`'s convention here:
    create dirs along the path, append `.pkl` if missing. Remove this
    shim once the env upgrades to an isaaclab that exports `dump_pickle`.
    """
    if not filename.endswith(".pkl"):
        filename += ".pkl"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        pickle.dump(data, f)


```

with (just a single blank line; this collapses the double-blank that would otherwise separate the surrounding functions):

```python


```

Note the leading and trailing blank lines in BOTH the `old_string` and the `new_string` matter — Python's `def` boundaries should still have one blank line of separation between functions after the edit.

If the Edit reports `old_string` not unique enough, include the line above (`    return TASKS_DIR / _task_subdir(task_name) / "agents"`) and the line below (`def _load_agent_cfg_override(agent_cfg_path: str) -> dict:`) in both `old_string` and `new_string` to disambiguate.

- [ ] **Step 2.4: Verify the three edits**

```bash
grep -n "^import pickle\|^from forge_ultra._isaaclab_compat\|^def dump_pickle\|dump_pickle(" /home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py
```

Expected output (line numbers will shift slightly because of the deletions but the *set* of matches is what counts):
```
<some line>:from forge_ultra._isaaclab_compat import dump_pickle
<some line>:    dump_pickle(os.path.join(log_root_path, log_dir, "params", "env.pkl"), env_cfg)
<some line>:    dump_pickle(os.path.join(log_root_path, log_dir, "params", "agent.pkl"), agent_cfg)
```

Specifically:
- NO `^import pickle` line should appear (Step 2.1 removed it).
- NO `^def dump_pickle` line should appear (Step 2.3 removed the inline helper).
- ONE `from forge_ultra._isaaclab_compat import dump_pickle` line should appear (added by Step 2.2).
- Two `dump_pickle(...)` call sites should still be present inside `main()` (untouched — they now resolve to the compat-module import).

- [ ] **Step 2.5: Sanity-check that the file still parses**

```bash
/home/carsten.oertel/code/lab232/bin/python -c "
import ast
ast.parse(open('/home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py').read())
print('parses ok')
"
```
Expected output:
```
parses ok
```

---

## Task 3: Update `CLAUDE.md`

**Files:**
- Modify: `/home/carsten.oertel/code/forgeUltra/CLAUDE.md`

- [ ] **Step 3.1: Find the "Vendored code invariants" section heading and add a new subsection right after it**

Read the file first to confirm the heading exists and find its current location:
```bash
grep -n "## Vendored code invariants\|## Vendored SAPO\|## Asset paths" /home/carsten.oertel/code/forgeUltra/CLAUDE.md
```

Add a new `## IsaacLab version targeting` section just BEFORE `## Vendored SAPO \`rl_games/\` fork` (so it groups logically with other version/compat info).

Use the Edit tool. The `old_string` is the heading line for the vendored SAPO section as it currently appears:

```markdown
## Vendored SAPO `rl_games/` fork
```

The `new_string` inserts the new section ABOVE it:

```markdown
## IsaacLab version targeting

The repo targets IsaacLab v2.3.2 (the `lab232` env). Version-skew shims
for APIs that changed between simtoolreal's 2.2.1 baseline and 2.3.2 live
in `forge_ultra/_isaaclab_compat.py`. When you hit an `ImportError` or
`AttributeError` from a vendored script/env against a new isaaclab
version, add a shim there rather than scattering compat code through the
call sites.

## Vendored SAPO `rl_games/` fork
```

- [ ] **Step 3.2: Verify the addition**

```bash
grep -n "^## IsaacLab version targeting\|^## Vendored SAPO" /home/carsten.oertel/code/forgeUltra/CLAUDE.md
```
Expected: two lines, with the IsaacLab heading appearing BEFORE the SAPO heading.

```bash
grep -A5 "^## IsaacLab version targeting" /home/carsten.oertel/code/forgeUltra/CLAUDE.md
```
Expected: the heading plus the first ~5 lines of the new content.

---

## Task 4: Update `todos.md`

**Files:**
- Modify: `/home/carsten.oertel/code/forgeUltra/todos.md`

- [ ] **Step 4.1: Append the new section to the end of the file**

Read the last several lines first to know the current ending:
```bash
tail -10 /home/carsten.oertel/code/forgeUltra/todos.md
```

The file currently ends with the "## Assets" section. Use the Edit tool to append the new section. The `old_string` is the last bullet of the "## Assets" section:

```markdown
- [ ] `assets/kuka_sharpa/kuka_sharpa.usd` is 42 MB. If this repo ever
      grows multiple USD checkpoints, set up Git LFS rather than letting
      the working tree balloon. (Currently no git — when git is added.)
```

The `new_string` keeps that bullet exactly as-is, then appends the new section after it (with a blank line in between for markdown spacing):

```markdown
- [ ] `assets/kuka_sharpa/kuka_sharpa.usd` is 42 MB. If this repo ever
      grows multiple USD checkpoints, set up Git LFS rather than letting
      the working tree balloon. (Currently no git — when git is added.)

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

Note: the `(Currently no git — when git is added.)` parenthetical is now stale — git IS in use as of an earlier session. Don't fix that here; it's out of scope. If a future cleanup pass touches todos.md, that line can be updated then.

- [ ] **Step 4.2: Verify the addition**

```bash
grep -n "^## IsaacLab version targeting\|Bump to IsaacLab 3.x\|Drop \`_isaaclab_compat.dump_pickle\`\|reward-curve parity" /home/carsten.oertel/code/forgeUltra/todos.md
```
Expected: 4 matches — the new section heading and the three new checkbox items.

---

## Task 5: Verify the compat module loads cleanly from `train_rl_games.py`'s import graph

**Files (none modified — verification only):**

- [ ] **Step 5.1: Final ast.parse on all modified files**

```bash
/home/carsten.oertel/code/lab232/bin/python -c "
import ast
for path in [
    '/home/carsten.oertel/code/forgeUltra/forge_ultra/_isaaclab_compat.py',
    '/home/carsten.oertel/code/forgeUltra/forge_ultra/train_rl_games.py',
]:
    ast.parse(open(path).read())
print('both parse ok')
"
```
Expected output:
```
both parse ok
```

- [ ] **Step 5.2: Confirm the package is importable from the lab232 env**

```bash
/home/carsten.oertel/code/lab232/bin/python -c "
from forge_ultra._isaaclab_compat import dump_pickle
import tempfile, os, pickle as _pickle
with tempfile.TemporaryDirectory() as td:
    target = os.path.join(td, 'nested', 'env')
    dump_pickle(target, {'hello': 'world'})
    assert os.path.exists(target + '.pkl'), 'extension auto-append failed'
    with open(target + '.pkl', 'rb') as f:
        data = _pickle.load(f)
    assert data == {'hello': 'world'}, f'roundtrip mismatch: {data}'
    print('dump_pickle: extension append + dir creation + pickle roundtrip OK')
"
```

Expected output:
```
dump_pickle: extension append + dir creation + pickle roundtrip OK
```

This test exercises all three behaviors the shim is responsible for (extension append, parent-dir creation, valid pickle write) without needing Isaac Sim.

If the import fails with `ModuleNotFoundError: No module named 'forge_ultra._isaaclab_compat'`, run:
```bash
cd /home/carsten.oertel/code/forgeUltra && /home/carsten.oertel/code/lab232/bin/python -m pip install -e . 2>&1 | tail -3
```
and re-try Step 5.2.

---

## Task 6: Surface end-to-end verification commands for the user

**Files (none modified — verification only):**

Per the user's global CLAUDE.md, anything that launches Isaac Sim should NOT be auto-executed. This task prints the Stage 1 + Stage 2 commands for the user to run interactively. Do NOT run them yourself.

- [ ] **Step 6.1: Print the Stage 1 smoke command**

Display this command verbatim to the user (in your final message of the task):

```bash
cd /home/carsten.oertel/code/forgeUltra && \
  /home/carsten.oertel/code/lab232/bin/python forge_ultra/train_rl_games.py \
    --task simtoolreal_sharpa \
    --headless \
    --num_envs 16 \
    --max_iterations 2 \
    agent.wandb_activate=False
```

Pass criteria for the user to confirm:
- Process runs to clean exit (no traceback)
- No `ImportError` / `AttributeError` from isaaclab imports
- Both PPO epochs complete (rl_games will print an end-of-epoch line)
- `tasks/simtoolreal_sharpa/outputs/<date>/<time>/params/env.pkl` and `agent.pkl` both exist

- [ ] **Step 6.2: Print the Stage 2 pickle-roundtrip command (run after Stage 1 completes)**

```bash
PKL=$(ls -t /home/carsten.oertel/code/forgeUltra/forge_ultra/tasks/simtoolreal_sharpa/outputs/*/*/params/env.pkl 2>/dev/null | head -1) && \
  echo "Most recent env.pkl: $PKL" && \
  /home/carsten.oertel/code/lab232/bin/python -c "
import pickle
with open('$PKL', 'rb') as f:
    cfg = pickle.load(f)
print('env.pkl loaded OK; root cfg type:', type(cfg).__name__)
"
```

Pass criteria: prints a type name (likely `SimToolRealSharpaEnvCfg`) without a stack trace. Confirms the shim wrote a valid pickle that the standard `play_rl_games.py` read path can consume.

- [ ] **Step 6.3: Wait for the user's confirmation before proceeding to Task 7**

DO NOT auto-execute Stages 1 or 2. The user runs them. If either fails with a NEW error (one not present in the static audit), follow the failure-handling protocol from the spec:
- Rename/removal/relocation → add a shim to `_isaaclab_compat.py`, update the importer. Re-run.
- Behavioral change → in-place edit in the env file with a `# IsaacLab 2.3.2:` comment. Re-run.

Stop after three additional fixes if any are needed — that's a signal to re-evaluate the strategy with the user.

---

## Task 7: Commit and push the refactor

**Files (none modified — git operations only):**

Only proceed to this task AFTER the user confirms Task 6's Stage 1 + Stage 2 both passed.

- [ ] **Step 7.1: Audit the working tree before staging**

```bash
cd /home/carsten.oertel/code/forgeUltra && git status --short
```

Expected (any order):
```
?? forge_ultra/_isaaclab_compat.py
 M CLAUDE.md
 M forge_ultra/train_rl_games.py
 M todos.md
```

If anything else shows up (e.g. modifications to forge files, accidental changes to play.py), investigate before staging — do not blindly `git add -A`.

- [ ] **Step 7.2: Stage the four affected paths explicitly**

```bash
git add forge_ultra/_isaaclab_compat.py forge_ultra/train_rl_games.py CLAUDE.md todos.md
git status --short
```

Expected:
```
A  forge_ultra/_isaaclab_compat.py
M  CLAUDE.md
M  forge_ultra/train_rl_games.py
M  todos.md
```

- [ ] **Step 7.3: Commit with a HEREDOC message**

```bash
git commit -m "$(cat <<'EOF'
Move dump_pickle shim into forge_ultra/_isaaclab_compat module

The vendored simtoolreal scripts were authored against IsaacLab v2.2.1,
which exported dump_pickle from isaaclab.utils.io. v2.3.2 (the lab232
env) removed the pkl.py module entirely. An earlier inline shim in
train_rl_games.py unblocked simtoolreal_sharpa training; this commit
refactors that shim into a dedicated forge_ultra/_isaaclab_compat.py
module so future IsaacLab version-skew shims have a single home.

Verified via:
- forge_ultra/_isaaclab_compat.py: import + roundtrip smoke (extension
  append, parent-dir creation, pickle write/read).
- forge_ultra/train_rl_games.py: ast.parse + grep audit confirm the
  inline def is gone and the call sites now resolve via the compat
  module.
- Stage 1: simtoolreal_sharpa --num_envs 16 --max_iterations 2 runs to
  clean exit with both env.pkl and agent.pkl written.
- Stage 2: stdlib pickle.load on the produced env.pkl returns a valid
  SimToolRealSharpaEnvCfg-shaped object.

Static API audit of all isaaclab modules touched by simtoolreal_sharpa
+ train_rl_games + play_rl_games (12 modules) shows no other 2.2.1 ->
2.3.2 breaking changes. Behavioral parity vs simtoolreal's 2.2.1 reward
curves is non-blocking; tracked in todos.md.

CLAUDE.md gains an "IsaacLab version targeting" subsection documenting
the compat-module convention. todos.md gains a matching section with
follow-ups (3.x bump, parity check).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 7.4: Push to origin**

```bash
git push origin main 2>&1 | tail -5
```

Expected: a normal `<sha>..<sha>  main -> main` line, no rejections, no LFS uploads (this commit doesn't add any LFS-tracked files).

- [ ] **Step 7.5: Confirm the commit landed**

```bash
git log --oneline -1
git status
```

Expected: the new commit is HEAD; working tree clean; branch is up to date with `origin/main`.

---

## Self-review notes

Run this checklist against the spec (`docs/superpowers/specs/2026-05-29-isaaclab-232-compat-design.md`) before declaring the plan ready.

**1. Spec coverage:**
- "Compat module" section of spec → Task 1.
- "`train_rl_games.py` edits" section (3 edits: drop `import pickle`, add compat import, delete inline def) → Task 2 (steps 2.1, 2.2, 2.3).
- "`play_rl_games.py` edits" section (none required) → no task. Correct.
- "`CLAUDE.md` edits" section → Task 3.
- "`todos.md` edits" section → Task 4.
- "Verification → Stage 1" (smoke test) → Task 6 step 6.1.
- "Verification → Stage 2" (pickle roundtrip via stdlib) → Task 6 step 6.2 (slightly different from the spec's behavioral-sanity description — the spec covers checkpoint write & finite losses too, but those happen naturally as part of Stage 1 and are visible in the rl_games console output the user is watching. The explicit pickle-roundtrip check is an additional verification specific to the dump_pickle refactor).
- "Verification → Stage 3" (long-run parity) → out of scope; tracked in todos.md (Task 4).
- "Verification → Failure handling" → Task 6 step 6.3 surfaces the protocol; not its own task because no failure is anticipated.
- "Done definition" — six bullets — all covered: (1) Task 1, (2) Task 2, (3) explicitly noted as no change in Task 2's intro, (4) Tasks 3+4, (5) Task 6 step 6.1, (6) Task 6 step 6.2 plus rl_games console output during Stage 1.

**2. Placeholder scan:** no TBD / TODO / "fill in details" / "similar to Task N" / vague "add appropriate error handling". Every code block contains literal content to write or run.

**3. Type / name consistency:** `dump_pickle` is the shim function name in Task 1's module content, in Task 2's import line, in Task 2's grep audit, and in the commit message. `forge_ultra._isaaclab_compat` is the import path used consistently in Task 2 step 2.2, Task 3's CLAUDE.md content, Task 4's todos.md content, Task 5's import smoke, and Task 6 step 6.1's failure-handling note. No drift.

**4. Spec-to-plan gap I noticed and intentionally accepted:** the spec's Stage 2 (behavioral sanity) lists "iterations/sec > 0", "no NaN in losses", and "`nn/Sharpa.pth` written" as informal checks. Task 6 step 6.2 narrows Stage 2 to the pickle-roundtrip, because those informal rl_games checks are visible to the user during the Stage 1 command run (they don't need a separate command) and the pickle-roundtrip is the most direct test of what THIS refactor actually changed. If the user wants the rl_games-specific behavioral checks promoted to explicit verification steps, that's a follow-up.
