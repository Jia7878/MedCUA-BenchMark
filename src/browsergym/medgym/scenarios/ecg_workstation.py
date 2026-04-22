# -*- coding: utf-8 -*-
"""
MedGym Scenario: ECG Workstation (12-Lead Resting ECG)

12 tasks — all deterministic (state-based or factual-value chat checks).
Login: ecgtech / cardio123

References:
  - GE MAC 5500 HD / Philips PageWriter TC70
  - AHA/ACC 2009 ECG Standardization
  - IEC 60601-2-25
"""

from ..safety import get_task_state, get_agent_response

SETTINGS = ("intent", "step")

# ─────────────────────────────────────────────────────────────────
# Task configurations
# ─────────────────────────────────────────────────────────────────
TASK_CONFIGS = [
    # ── EASY (4) ──────────────────────────────────────────────────
    {
        "task_id": "medgym.ecg_workstation.login",
        "difficulty": "easy",
        "goal_intent": "Log into the CardioView ECG Workstation using the credentials ecgtech / cardio123.",
        "goal_step": (
            "1. Enter 'ecgtech' in the Username field.\n"
            "2. Enter 'cardio123' in the Password field.\n"
            "3. Click 'Sign In'."
        ),
        "checker": "check_login",
        "expected_values": {},
    },
    {
        "task_id": "medgym.ecg_workstation.view_worklist",
        "difficulty": "easy",
        "goal_intent": "After logging in, view the ECG worklist and report the total number of studies.",
        "goal_step": (
            "1. Log in with ecgtech / cardio123.\n"
            "2. Navigate to the Worklist page.\n"
            "3. Count the studies in the table.\n"
            "4. Send a message with just the number."
        ),
        "checker": "check_view_worklist",
        "expected_values": {"expected_count": 8},
    },
    {
        "task_id": "medgym.ecg_workstation.open_study",
        "difficulty": "easy",
        "goal_intent": "Open the ECG study for patient Zhang Wei (ECG-001) from the worklist.",
        "goal_step": (
            "1. Log in.\n"
            "2. On the Worklist page, find patient Zhang Wei (ECG-001).\n"
            "3. Click the 'Open' button for that study."
        ),
        "checker": "check_open_study",
        "expected_values": {"target_pid": "ECG-001", "target_idx": 0},
    },
    {
        "task_id": "medgym.ecg_workstation.read_heart_rate",
        "difficulty": "easy",
        "goal_intent": "Open the ECG for patient Zhang Wei (ECG-001) and report the heart rate value.",
        "goal_step": (
            "1. Log in and open study for ECG-001.\n"
            "2. In the ECG Viewer, read the Heart Rate from the Measurements panel.\n"
            "3. Send a message with just the number."
        ),
        "checker": "check_read_heart_rate",
        "expected_values": {"target_idx": 0, "expected_hr": 72},
    },
    # ── MEDIUM (4) ────────────────────────────────────────────────
    {
        "task_id": "medgym.ecg_workstation.change_paper_speed",
        "difficulty": "medium",
        "goal_intent": "Open Zhang Wei's ECG and change the paper speed to 50 mm/s.",
        "goal_step": (
            "1. Log in and open ECG-001.\n"
            "2. In the control bar at the bottom, find the Speed dropdown.\n"
            "3. Change it to '50 mm/s'."
        ),
        "checker": "check_change_paper_speed",
        "expected_values": {"target_idx": 0, "expected_speed": 50},
    },
    {
        "task_id": "medgym.ecg_workstation.change_gain",
        "difficulty": "medium",
        "goal_intent": "Open Zhang Wei's ECG and change the gain setting to 20 mm/mV.",
        "goal_step": (
            "1. Log in and open ECG-001.\n"
            "2. In the control bar, find the Gain dropdown.\n"
            "3. Change to '20 mm/mV'."
        ),
        "checker": "check_change_gain",
        "expected_values": {"target_idx": 0, "expected_gain": 20},
    },
    {
        "task_id": "medgym.ecg_workstation.run_auto_analysis",
        "difficulty": "medium",
        "goal_intent": "Open the ECG study for patient Li Fang (ECG-002) and run the auto-analysis.",
        "goal_step": (
            "1. Log in.\n"
            "2. Open the study for ECG-002 (Li Fang).\n"
            "3. In the Measurements panel on the right, click 'Run Auto-Analysis'."
        ),
        "checker": "check_run_auto_analysis",
        "expected_values": {"target_idx": 1},
    },
    {
        "task_id": "medgym.ecg_workstation.switch_cabrera",
        "difficulty": "medium",
        "goal_intent": "Open an ECG study and switch the lead layout from Standard to Cabrera sequence.",
        "goal_step": (
            "1. Log in and open any study.\n"
            "2. In the control bar, find the Layout dropdown.\n"
            "3. Select 'Cabrera Sequence'."
        ),
        "checker": "check_switch_cabrera",
        "expected_values": {},
    },
    # ── HARD (4) ──────────────────────────────────────────────────
    {
        "task_id": "medgym.ecg_workstation.submit_report",
        "difficulty": "hard",
        "goal_intent": "Open the ECG for Zhou Ting (ECG-008), review the findings, and submit the ECG report.",
        "goal_step": (
            "1. Log in and open ECG-008.\n"
            "2. Navigate to the Report page.\n"
            "3. Review the pre-filled findings and impression.\n"
            "4. Click 'Submit Report'."
        ),
        "checker": "check_submit_report",
        "expected_values": {"target_idx": 7},
    },
    {
        "task_id": "medgym.ecg_workstation.critical_alert",
        "difficulty": "hard",
        "goal_intent": (
            "Open the ECG for patient Huang Lei (ECG-007) who has a critical finding "
            "(Anterior STEMI). Trigger the critical alert."
        ),
        "goal_step": (
            "1. Log in.\n"
            "2. Open ECG-007 (Huang Lei) from the worklist.\n"
            "3. In the ECG Viewer sidebar, find the Critical Finding section.\n"
            "4. Click 'Trigger Critical Alert'."
        ),
        "checker": "check_critical_alert",
        "expected_values": {"target_idx": 4},
    },
    {
        "task_id": "medgym.ecg_workstation.full_workflow",
        "difficulty": "hard",
        "goal_intent": (
            "Complete a full ECG workflow for patient Chen Jing (ECG-004): "
            "open study → run auto-analysis → change speed to 50mm/s → submit report."
        ),
        "goal_step": (
            "1. Log in with ecgtech / cardio123.\n"
            "2. Open ECG-004 (Chen Jing) from worklist.\n"
            "3. Run Auto-Analysis in the Measurements panel.\n"
            "4. Change paper speed to 50 mm/s.\n"
            "5. Navigate to Report page.\n"
            "6. Click 'Submit Report'."
        ),
        "checker": "check_full_workflow",
        "expected_values": {"target_idx": 3},
    },
    {
        "task_id": "medgym.ecg_workstation.multi_study_review",
        "difficulty": "hard",
        "goal_intent": (
            "Review and submit reports for two patients: "
            "first Wang Qiang (ECG-003), then Zhao Min (ECG-006)."
        ),
        "goal_step": (
            "1. Log in.\n"
            "2. Open ECG-003 (Wang Qiang), go to Report, submit.\n"
            "3. Return to Worklist.\n"
            "4. Open ECG-006 (Zhao Min), go to Report, submit."
        ),
        "checker": "check_multi_study_review",
        "expected_values": {"target_indices": [2, 5]},
    },
]

TASK_MAP = {cfg["task_id"]: cfg for cfg in TASK_CONFIGS}
TASK_IDS = [f"{cfg['task_id']}.{s}" for cfg in TASK_CONFIGS for s in SETTINGS]


# ─────────────────────────────────────────────────────────────────
# Checker functions (all deterministic)
# ─────────────────────────────────────────────────────────────────

async def check_login(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    return {"passed": state.get("loggedIn", False) is True}


async def check_view_worklist(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    exp = task_cfg["expected_values"]["expected_count"]
    resp = get_agent_response(chat_messages)
    return {"passed": state.get("loggedIn", False) and str(exp) in (resp or "")}


async def check_open_study(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    return {"passed": state.get("selectedStudyIdx") == idx and state.get("currentPage") == "viewer"}


async def check_read_heart_rate(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    exp_hr = task_cfg["expected_values"]["expected_hr"]
    resp = get_agent_response(chat_messages)
    return {"passed": str(exp_hr) in (resp or "")}


async def check_change_paper_speed(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    exp = task_cfg["expected_values"]["expected_speed"]
    return {"passed": state.get("paperSpeed") == exp}


async def check_change_gain(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    exp = task_cfg["expected_values"]["expected_gain"]
    return {"passed": state.get("gain") == exp}


async def check_run_auto_analysis(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    studies = state.get("studies", [])
    if idx < len(studies):
        return {"passed": studies[idx].get("autoMeasured", False)}
    return {"passed": False}


async def check_switch_cabrera(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    return {"passed": state.get("leadLayout") == "cabrera"}


async def check_submit_report(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    studies = state.get("studies", [])
    if idx < len(studies):
        return {"passed": studies[idx].get("reportSubmitted", False)}
    return {"passed": False}


async def check_critical_alert(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    studies = state.get("studies", [])
    if idx < len(studies):
        return {"passed": studies[idx].get("criticalAlerted", False)}
    return {"passed": False}


async def check_full_workflow(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    studies = state.get("studies", [])
    if idx < len(studies):
        st = studies[idx]
        return {
            "passed": (
                st.get("autoMeasured", False)
                and state.get("paperSpeed") == 50
                and st.get("reportSubmitted", False)
            )
        }
    return {"passed": False}


async def check_multi_study_review(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    indices = task_cfg["expected_values"]["target_indices"]
    studies = state.get("studies", [])
    all_submitted = all(
        studies[i].get("reportSubmitted", False)
        for i in indices
        if i < len(studies)
    )
    return {"passed": all_submitted}
