"""Canonical screenshot-only MedCUA-Bench environment protocol."""

from __future__ import annotations

import gymnasium as gym
from browsergym.core.action.highlevel import HighLevelActionSet


PIXEL_ACTION_SET = HighLevelActionSet(
    subsets=["chat", "coord", "nav", "tab", "infeas"],
    multiaction=False,
    strict=False,
)

SCREENSHOT_ONLY_OBSERVATION_KEYS = (
    "screenshot",
    "goal",
    "chat_messages",
    "last_action",
    "last_action_error",
)


class ScreenshotOnlyObservationWrapper(gym.ObservationWrapper):
    """Remove BrowserGym DOM, accessibility-tree, URL, and element-ID fields."""

    def __init__(self, env: gym.Env):
        super().__init__(env)
        self.observation_space = gym.spaces.Dict(
            {
                key: env.observation_space[key]
                for key in SCREENSHOT_ONLY_OBSERVATION_KEYS
            }
        )

    def observation(self, observation):
        return {
            key: observation[key]
            for key in SCREENSHOT_ONLY_OBSERVATION_KEYS
        }


def make_env(task_id: str, **kwargs) -> gym.Env:
    """Create a benchmark-conformant screenshot-only environment.

    Args:
        task_id: A registered ID with or without the ``browsergym/`` prefix.
        **kwargs: Additional BrowserGym environment options, such as
            ``headless`` or ``record_video_dir``.
    """
    gym_id = task_id if task_id.startswith("browsergym/") else f"browsergym/{task_id}"
    if "action_mapping" in kwargs:
        raise TypeError(
            "make_env fixes the paper's action mapping; use gym.make directly "
            "for non-benchmark debugging configurations."
        )
    kwargs["action_mapping"] = PIXEL_ACTION_SET.to_python_code
    return ScreenshotOnlyObservationWrapper(gym.make(gym_id, **kwargs))
