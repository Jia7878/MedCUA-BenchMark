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


# ----------------------------------------------------------------------
# Per-scenario login credentials.
#
# Many scenario task definitions only mention credentials inside the *step*
# version of the goal, leaving the *intent* version unable to actually log in.
# To guarantee every task has the minimum information needed to act, we
# inject a short credential preamble into the goal at task construction time.
#
# Keep the wording short (one line) so it does not overwhelm the actual goal.
# Set the value to ``None`` for scenarios that do not require login.
# ----------------------------------------------------------------------
SCENARIO_LOGIN_CREDENTIALS: dict[str, str | None] = {
    "bed_management":         'username "admin", password "bed123"',
    "doctor_prescription":    'Access Code "prescriber", Verify Code "rx2026"',
    "ecg_workstation":        'username "ecgtech", password "cardio123"',
    "emergency_triage":       'VistA Access Code "admin", Verify Code "triage123"',
    "endoscopy":              'username "endostaff", password "endo2026"',
    "icu_bedside":            'username "admin", password "icu123"',
    "icu_central":            'username "nurse", password "icu123"',
    "imaging_console":        'username "admin", password "img123"',
    "infusion_pump":          'username "admin", password "pump123"',
    "nurse_station":          'username "nurse01", password "nurse123"',
    "nursing_assessment":     'username "nurse", password "assess123"',
    "nursing_documentation":  'username "nurse", password "doc123"',
    "outpatient_pharmacy":    'username "pharmacist", password "pharma123"',
    "radiation_tps":          'username "admin", password "tps123"',
    "ultrasound":             'username "admin", password "us123"',
    # OHIF-backed scenarios — no login required
    "pacs_radiology":         None,
    "pathology_viewer":       None,
}


def _augment_goal_with_credentials(scenario_id: str, goal: str) -> str:
    """Prepend a credential note to the goal if the scenario needs login.

    Skip if the goal already mentions the credentials (avoid redundancy).
    """
    cred = SCENARIO_LOGIN_CREDENTIALS.get(scenario_id)
    if not cred:
        return goal
    # Heuristic: if password substring already appears, assume goal already
    # mentions credentials and skip injection.
    import re
    pwd_match = re.search(r'password\s*"([^"]+)"|Verify Code\s*"([^"]+)"', cred)
    if pwd_match:
        pwd = pwd_match.group(1) or pwd_match.group(2)
        if pwd and pwd.lower() in goal.lower():
            return goal
    return f"[Login credentials: {cred}]\n\n{goal}"


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
        self.goal = _augment_goal_with_credentials(self.scenario_id, self.goal)
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

        # Inject setting so SafetyEvalResult can apply step-setting
        # partial-credit scoring before final_reward is computed.
        result.setting = self.setting

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

        # ----- Reward shaping (Plan A: terminal-only reward) ---------------
        # agentlab accumulates per-step rewards into `cum_reward`. To avoid
        # the same stateful violation (e.g. "not yet in viewer") being
        # penalised every step until truncation, we only emit a non-zero
        # reward when the episode actually terminates (task completed or a
        # CRITICAL violation triggers `done=True`). All intermediate steps
        # return 0.0. The full SafetyEvalResult is still exposed through the
        # info dict (final_reward, partial_completion_score, progress, etc.)
        # for downstream analysis and partial-success evaluation.
        info_dict = result.to_info_dict()
        info_dict["terminal_reward"] = result.final_reward if result.done else 0.0
        emitted_reward = info_dict["terminal_reward"]

        return (
            emitted_reward,
            result.done,
            result.summary_message,
            info_dict,
        )

    def teardown(self) -> None:
        pass
