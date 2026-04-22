# -*- coding: utf-8 -*-
"""
MedGym — Base Task for OHIF Viewer-backed scenarios.

Used by scenarios that deploy the real OHIF DICOM Viewer:
  - pacs_radiology  (basic viewer mode)
  - pathology_viewer (microscopy mode)
  - ecg_diagnosis   (ECG waveform mode)

The OHIF Viewer must be running (default: http://localhost:3000).
Set MEDGYM_OHIF_URL to override.
"""
from __future__ import annotations

import logging
import os
from typing import Tuple

from browsergym.core.task import AbstractBrowserTask

from .safety import SafetyEvalResult

logger = logging.getLogger(__name__)

_DEFAULT_OHIF_URL = "http://localhost:3000"


class MedGymOHIFTask(AbstractBrowserTask):
    """Base task backed by the OHIF Viewer.

    Subclasses set ``scenario_id`` and ``checker_registry`` at class level.
    Task configs may specify ``start_url`` (a path appended to the OHIF base)
    or leave it blank for the study list page.
    """

    # -- class-level attributes (override in subclass) --------------------
    scenario_id: str = ""
    checker_registry: dict = {}

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

        # Resolve config from scenario module
        from . import scenarios as _scenarios_pkg

        scenario_module = getattr(_scenarios_pkg, self.scenario_id)
        cfg = scenario_module.TASK_MAP[task_id]

        self.goal = cfg["goal_intent"] if setting == "intent" else cfg["goal_step"]
        self.checker_name = cfg["checker"]
        self.start_url = cfg.get("start_url", "")
        self._expected = cfg.get("expected_values", {})
        self._difficulty = cfg.get("difficulty", "unknown")
        self._scored = cfg.get("scored", True)

        self.base_url = (
            base_url
            or os.environ.get("MEDGYM_OHIF_URL")
            or _DEFAULT_OHIF_URL
        ).rstrip("/")

    @classmethod
    def get_task_id(cls) -> str:
        return f"medgym.{cls.scenario_id}"

    def setup(self, page) -> Tuple[str, dict]:
        url = f"{self.base_url}{self.start_url}" if self.start_url else self.base_url
        page.goto(url, wait_until="networkidle", timeout=60000)
        # OHIF can take a moment to render
        page.wait_for_timeout(3000)

        self._api_requests: list[dict] = []
        self._page_history: list[str] = []

        page.on("request", lambda req: self._track_request(req))
        page.on("framenavigated", lambda frame: self._track_navigation(frame))

        logger.info("MedGymOHIFTask [%s] setup at %s", self.task_id, url)
        return self.goal, {}

    def _track_request(self, request):
        self._api_requests.append({
            "method": request.method,
            "url": request.url,
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
            page,
            chat_messages,
            self.base_url,
            self._api_requests,
            self._page_history,
            self._expected,
        )

        # Inject task metadata for downstream aggregation
        result.task_metadata = {
            "task_id": self.task_id,
            "scenario": self.scenario_id,
            "setting": self.setting,
            "difficulty": self._difficulty,
            "scored": self._scored,
            "fidelity_level": "L3_production",
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


# ======================================================================
# Helper functions for querying OHIF viewer state from Python checkers
# ======================================================================


def get_ohif_state(page) -> dict:
    """Query OHIF viewer state via page.evaluate().

    Returns a dict with keys:
      - url, pathname, search
      - isStudyList, isViewer, isMicroscopy
      - studyUIDs (from URL query param)
      - viewportCount
      - activeToolName
      - measurements (list of measurement annotations)
      - visiblePanels (list of visible panel CSS classes/ids)
    """
    return page.evaluate(
        """() => {
        const state = {};
        state.url = window.location.href;
        state.pathname = window.location.pathname;
        state.search = window.location.search;

        // Page type detection
        state.isStudyList = state.pathname === '/' || state.pathname === '';
        state.isViewer = state.pathname.includes('/viewer');
        state.isMicroscopy = state.pathname.includes('/microscopy');

        // Study UIDs from URL
        const params = new URLSearchParams(state.search);
        state.studyUIDs = params.get('StudyInstanceUIDs') || '';

        // Viewport count
        const vps = document.querySelectorAll(
            '[data-viewport-uid], .cornerstone-canvas, .viewport-element'
        );
        state.viewportCount = vps.length;

        // Active tool (from toolbar state)
        const activeBtn = document.querySelector(
            'button[class*="active"][data-tool], ' +
            'button[class*="active"][data-cy*="tool"], ' +
            '[class*="ToolbarButton"][class*="active"]'
        );
        state.activeToolName = activeBtn
            ? (activeBtn.getAttribute('data-tool') ||
               activeBtn.getAttribute('data-cy') ||
               activeBtn.textContent.trim())
            : '';

        // Study list rows
        const rows = document.querySelectorAll(
            '[data-cy="study-list-results"] tr, ' +
            'table tbody tr, ' +
            '[class*="StudyListTable"] tr'
        );
        state.studyListRowCount = rows.length;

        // Check for canvas elements (viewports rendered)
        const canvases = document.querySelectorAll('canvas');
        state.canvasCount = canvases.length;

        // Layout grid
        const grid = document.querySelector('[class*="ViewportGrid"]');
        state.hasViewportGrid = !!grid;

        return state;
    }"""
    )
