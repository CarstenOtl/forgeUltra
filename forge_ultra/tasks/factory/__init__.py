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
