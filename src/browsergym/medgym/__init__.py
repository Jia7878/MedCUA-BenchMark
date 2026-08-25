"""
MedCUA-Bench — Medical GUI CUA Benchmark for BrowserGym

18 scenarios × 12 tasks × 2 goal settings = 432 environments

    # Outpatient (HTML)
    env = gym.make("browsergym/medgym.emergency_triage.login.intent")

    # Inpatient (OpenEMR Docker + HTML bed_management)
    env = gym.make("browsergym/medgym.openemr.login.step")
    env = gym.make("browsergym/medgym.bed_management.login.intent")

    # Nursing (HTML)
    env = gym.make("browsergym/medgym.nurse_station.login.intent")

    # ICU (HTML)
    env = gym.make("browsergym/medgym.icu_central.login.intent")
    env = gym.make("browsergym/medgym.infusion_pump.full_workflow.step")

    # PACS / Pathology (OHIF Viewer)
    env = gym.make("browsergym/medgym.pacs_radiology.open_ct_study.intent")
    env = gym.make("browsergym/medgym.pathology_viewer.open_wsi.step")

    # Specialized (HTML)
    env = gym.make("browsergym/medgym.imaging_console.login.intent")
    env = gym.make("browsergym/medgym.radiation_tps.login.intent")
    env = gym.make("browsergym/medgym.ecg_workstation.login.intent")
    env = gym.make("browsergym/medgym.endoscopy.login.intent")
    env = gym.make("browsergym/medgym.ultrasound.login.intent")
"""

import inspect

from browsergym.core.registration import register_task

ALL_MEDGYM_TASK_IDS = []

# --- 1) Inpatient EMR & CPOE tasks (OpenEMR Docker) ------------------------
from .openemr_task import OpenEMRTask, TASK_CONFIGS as OEMR_TASK_CONFIGS, SETTINGS as OEMR_SETTINGS

for task_cfg in OEMR_TASK_CONFIGS:
    base_id = task_cfg["task_id"]
    for setting in OEMR_SETTINGS:
        full_id = f"{base_id}.{setting}"
        register_task(
            id=full_id,
            task_class=OpenEMRTask,
            task_kwargs={"task_id": base_id, "setting": setting},
        )
        ALL_MEDGYM_TASK_IDS.append(full_id)

# --- 2) Self-contained HTML scenarios (15 modules) -------------------------
from .base_task import MedGymScenarioTask
from .scenarios import ALL_SCENARIO_MODULES

# Scenarios backed by the OHIF Viewer (not HTML mocks)
_OHIF_SCENARIOS = {"pacs_radiology", "pathology_viewer"}


def _build_checker_registry(module):
    """Extract all check_* functions from a scenario module."""
    return {
        name: obj
        for name, obj in inspect.getmembers(module, inspect.isfunction)
        if name.startswith("check_")
    }


for _mod in ALL_SCENARIO_MODULES:
    _scenario_id = _mod.__name__.rsplit(".", 1)[-1]  # e.g. "emergency_triage"
    if _scenario_id in _OHIF_SCENARIOS:
        continue  # handled below

    _checkers = _build_checker_registry(_mod)

    # Dynamically create a subclass of MedGymScenarioTask for this scenario
    _task_class = type(
        f"MedGym_{_scenario_id}",
        (MedGymScenarioTask,),
        {"scenario_id": _scenario_id, "checker_registry": _checkers},
    )

    for _cfg in _mod.TASK_CONFIGS:
        _base_id = _cfg["task_id"]
        for _setting in _mod.SETTINGS:
            _full_id = f"{_base_id}.{_setting}"
            register_task(
                id=_full_id,
                task_class=_task_class,
                task_kwargs={"task_id": _base_id, "setting": _setting},
            )
            ALL_MEDGYM_TASK_IDS.append(_full_id)

# --- 3) OHIF Viewer scenarios (2 modules) ----------------------------------
from .ohif_task import MedGymOHIFTask

for _ohif_id in sorted(_OHIF_SCENARIOS):
    _mod = None
    for m in ALL_SCENARIO_MODULES:
        if m.__name__.rsplit(".", 1)[-1] == _ohif_id:
            _mod = m
            break
    if _mod is None:
        continue

    _checkers = _build_checker_registry(_mod)

    _task_class = type(
        f"MedGymOHIF_{_ohif_id}",
        (MedGymOHIFTask,),
        {"scenario_id": _ohif_id, "checker_registry": _checkers},
    )

    for _cfg in _mod.TASK_CONFIGS:
        _base_id = _cfg["task_id"]
        for _setting in _mod.SETTINGS:
            _full_id = f"{_base_id}.{_setting}"
            register_task(
                id=_full_id,
                task_class=_task_class,
                task_kwargs={"task_id": _base_id, "setting": _setting},
            )
            ALL_MEDGYM_TASK_IDS.append(_full_id)


from .protocol import make_env
