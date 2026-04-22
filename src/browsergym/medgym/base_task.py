# -*- coding: utf-8 -*-
"""
MedGym — Base Task for self-contained HTML scenario applications.

14 scenarios (everything except outpatient + 3 OHIF-backed imaging scenarios)
inherit from this class.  Each scenario serves a single-page HTML app via
file:// or Vite dev server, with state tracked in window._taskState.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Tuple

from browsergym.core.task import AbstractBrowserTask

from .safety import SafetyEvalResult, get_task_state

logger = logging.getLogger(__name__)

_SCENARIOS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scenarios"
_DEFAULT_SCENARIO_PORT_BASE = 4000  # each scenario gets its own port


class MedGymScenarioTask(AbstractBrowserTask):
    """Base task for HTML-based MedGym scenarios.

    Subclasses set ``scenario_id`` and ``checker_registry`` at class level.
    """

    # -- class-level attributes (override in subclass) --------------------
    scenario_id: str = ""            # e.g. "emergency_triage"
    checker_registry: dict = {}      # name -> callable

    def __init__(
        self,
        seed: int,
        task_id: str,
        setting: str = "step",
        base_url: str | None = None,
    ):
        super().__init__(seed)
        self.seed = seed
        self.task_id = task_id
        self.setting = setting

        # Resolve config from scenario's TASK_MAP
        from . import scenarios as _scenarios_pkg
        scenario_module = getattr(_scenarios_pkg, self.scenario_id)
        cfg = scenario_module.TASK_MAP[task_id]

        self.goal = cfg["goal_intent"] if setting == "intent" else cfg["goal_step"]
        self.checker_name = cfg["checker"]
        self.start_page = cfg.get("start_page", "index.html")
        self.start_hash = cfg.get("start_hash", "")
        self._expected = cfg.get("expected_values", {})
        self._difficulty = cfg.get("difficulty", "unknown")
        self._scored = cfg.get("scored", True)

        # URL resolution
        env_var = f"MEDGYM_{self.scenario_id.upper()}_URL"
        self.base_url = (
            base_url
            or os.environ.get(env_var)
            or f"file://{_SCENARIOS_DIR / self.scenario_id / self.start_page}"
        ).rstrip("/")

    @classmethod
    def get_task_id(cls) -> str:
        return f"medgym.{cls.scenario_id}"

    def setup(self, page) -> Tuple[str, dict]:
        url = self.base_url
        if self.start_hash:
            url += f"#{self.start_hash}"
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)

        # Initialize the scenario app with the seed
        try:
            page.evaluate(f"() => window._medgym_init && window._medgym_init({self.seed})")
            page.wait_for_timeout(500)
        except Exception:
            pass

        # Navigate to start_hash if needed (for SPAs)
        if self.start_hash:
            try:
                page.evaluate(f"() => window._medgym_navigate && window._medgym_navigate('{self.start_hash}')")
                page.wait_for_timeout(500)
            except Exception:
                pass

        self._api_requests: list[dict] = []
        self._page_history: list[str] = []

        page.on("request", lambda req: self._track_request(req))
        page.on("framenavigated", lambda frame: self._track_navigation(frame))

        logger.info("MedGymScenarioTask [%s] setup at %s", self.task_id, url)
        return self.goal, {}

    def _track_request(self, request):
        url = request.url
        method = request.method
        self._api_requests.append({
            "method": method,
            "url": url,
            "post_data": request.post_data,
        })

    def _track_navigation(self, frame):
        try:
            if frame.url and frame == frame.page.main_frame:
                self._page_history.append(frame.url)
        except Exception:
            pass

    def validate(self, page, chat_messages) -> Tuple[float, bool, str, dict]:
        checker_fn = self.checker_registry.get(self.checker_name)
        if checker_fn is None:
            return 0.0, True, f"Unknown checker: {self.checker_name}", {}

        result: SafetyEvalResult = checker_fn(
            page, chat_messages, self.base_url,
            self._api_requests, self._page_history,
            self._expected,
        )

        # Inject task metadata for downstream aggregation
        result.task_metadata = {
            "task_id": self.task_id,
            "scenario": self.scenario_id,
            "setting": self.setting,
            "difficulty": self._difficulty,
            "scored": self._scored,
            "fidelity_level": "L1_html",
            "n_api_requests": len(self._api_requests),
            "n_page_navigations": len(self._page_history),
        }

        return (
            result.final_reward,
            result.done,
            result.summary_message,
            result.to_info_dict(),
        )

    def teardown(self) -> None:
        pass
