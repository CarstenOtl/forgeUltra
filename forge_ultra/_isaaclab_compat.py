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
