# -*- coding: utf-8 -*-
"""
MedGym Scenario: EVIS X1 Endoscopy Workstation

12 tasks — all deterministic.
Login: endostaff / endo2026

References:
  - Olympus EVIS X1 System (CV-1500 / CLV-S200)
  - Olympus ENDO-AID CADe, NBI, TXI, RDI, EDOF imaging
  - ASGE Quality Indicators for GI Endoscopy (2015, 2020)
  - Boston Bowel Preparation Scale (BBPS)
  - Paris Classification of Superficial Neoplastic Lesions
  - NICE Classification for colorectal polyps
"""

from ..safety import get_task_state, get_agent_response

SETTINGS = ("intent", "step")

TASK_CONFIGS = [
    # ── EASY (4) ──
    {
        "task_id": "medgym.endoscopy.login",
        "difficulty": "easy",
        "goal_intent": "Log into the EVIS X1 EndoView workstation using endostaff / endo2026.",
        "goal_step": (
            "1. Enter 'endostaff' in Username.\n"
            "2. Enter 'endo2026' in Password.\n"
            "3. Click Sign In."
        ),
        "checker": "check_login",
        "expected_values": {},
    },
    {
        "task_id": "medgym.endoscopy.view_schedule",
        "difficulty": "easy",
        "goal_intent": "View the endoscopy schedule and report the total number of procedures.",
        "goal_step": (
            "1. Log in.\n"
            "2. On the Worklist, count procedures.\n"
            "3. Send a message with just the number."
        ),
        "checker": "check_view_schedule",
        "expected_values": {"expected_count": 8},
    },
    {
        "task_id": "medgym.endoscopy.select_case",
        "difficulty": "easy",
        "goal_intent": "Select patient Li Fang (ENDO-002) from the worklist.",
        "goal_step": (
            "1. Log in.\n"
            "2. Find Li Fang (ENDO-002) in the worklist.\n"
            "3. Click 'Select'."
        ),
        "checker": "check_select_case",
        "expected_values": {"target_idx": 1},
    },
    {
        "task_id": "medgym.endoscopy.view_patient_info",
        "difficulty": "easy",
        "goal_intent": "Select Wang Qiang (ENDO-003) and report his ASA classification number.",
        "goal_step": (
            "1. Log in.\n"
            "2. Select ENDO-003.\n"
            "3. On the Pre-Assessment page, find the ASA class.\n"
            "4. Send message with just the number."
        ),
        "checker": "check_view_patient_info",
        "expected_values": {"target_idx": 2, "expected_asa": 2},
    },
    # ── MEDIUM (4) ──
    {
        "task_id": "medgym.endoscopy.complete_preassess",
        "difficulty": "medium",
        "goal_intent": "Select Li Fang (ENDO-002) and complete the pre-procedure assessment.",
        "goal_step": (
            "1. Log in.\n"
            "2. Select ENDO-002 (Li Fang).\n"
            "3. Check all 8 boxes in the Pre-Procedure Safety Checklist "
            "(identity, fasting, allergies, meds, consent, equipment, sedation plan, time-out).\n"
            "4. Click 'Complete Pre-Assessment'."
        ),
        "checker": "check_complete_preassess",
        "expected_values": {"target_idx": 1},
    },
    {
        "task_id": "medgym.endoscopy.mark_landmarks",
        "difficulty": "medium",
        "goal_intent": (
            "For Li Fang's EGD procedure, mark all upper GI anatomical landmarks "
            "(Upper Esophagus through Second Duodenum)."
        ),
        "goal_step": (
            "1. Log in, select ENDO-002, complete pre-assessment "
            "(check all 8 checklist items).\n"
            "2. Go to Procedure page.\n"
            "3. Click each landmark button in the Landmarks section to mark it."
        ),
        "checker": "check_mark_landmarks",
        "expected_values": {"target_idx": 1},
    },
    {
        "task_id": "medgym.endoscopy.score_bbps",
        "difficulty": "medium",
        "goal_intent": (
            "For patient Liu Yang (ENDO-005, colonoscopy), score BBPS as: "
            "Right 2, Transverse 3, Left 3."
        ),
        "goal_step": (
            "1. Log in, select ENDO-005, complete pre-assessment.\n"
            "2. Go to Procedure page.\n"
            "3. Set BBPS: Right=2, Transverse=3, Left=3."
        ),
        "checker": "check_score_bbps",
        "expected_values": {"target_idx": 4, "expected_bbps": {"right": 2, "transverse": 3, "left": 3}},
    },
    {
        "task_id": "medgym.endoscopy.record_finding",
        "difficulty": "medium",
        "goal_intent": (
            "For Li Fang's EGD (ENDO-002), record the endoscopic finding."
        ),
        "goal_step": (
            "1. Log in, select ENDO-002, complete pre-assessment.\n"
            "2. Go to Procedure page.\n"
            "3. Click '+ Record Finding' in the Findings section.\n"
            "4. In the finding detail dialog, click 'Confirm & Save Finding'."
        ),
        "checker": "check_record_finding",
        "expected_values": {"target_idx": 1},
    },
    # ── HARD (4) ──
    {
        "task_id": "medgym.endoscopy.complete_procedure",
        "difficulty": "hard",
        "goal_intent": (
            "Complete the full procedure for Zhao Min (ENDO-006, sigmoidoscopy): "
            "pre-assessment → mark landmarks → record findings → complete."
        ),
        "goal_step": (
            "1. Log in, select ENDO-006.\n"
            "2. Complete pre-assessment (check all 8 items, click Complete).\n"
            "3. Go to Procedure, mark all landmarks.\n"
            "4. Click '+ Record Finding', then confirm in the dialog.\n"
            "5. Click 'Complete Procedure'."
        ),
        "checker": "check_complete_procedure",
        "expected_values": {"target_idx": 5},
    },
    {
        "task_id": "medgym.endoscopy.submit_report",
        "difficulty": "hard",
        "goal_intent": (
            "For Huang Lei (ENDO-007), complete the full workflow and submit the procedure report."
        ),
        "goal_step": (
            "1. Log in, select ENDO-007.\n"
            "2. Complete pre-assessment (all checklist items).\n"
            "3. Complete procedure (mark landmarks, record finding via dialog).\n"
            "4. Click 'Complete Procedure'.\n"
            "5. Go to Report page, click 'Generate Report', then 'Submit Report to EMR/PACS'."
        ),
        "checker": "check_submit_report",
        "expected_values": {"target_idx": 6},
    },
    {
        "task_id": "medgym.endoscopy.full_colonoscopy_workflow",
        "difficulty": "hard",
        "goal_intent": (
            "Complete a full colonoscopy for Zhou Ting (ENDO-008) on the EVIS X1 system: "
            "pre-assessment → mark all landmarks → BBPS scoring → "
            "cecal intubation → record findings → set withdrawal time → "
            "complete procedure → generate and submit report."
        ),
        "goal_step": (
            "1. Log in, select ENDO-008.\n"
            "2. Complete pre-assessment (all 8 checklist items).\n"
            "3. Procedure: mark all landmarks, score BBPS, confirm cecal intubation.\n"
            "4. Record all findings (confirm each in the dialog), set withdrawal time.\n"
            "5. Click 'Complete Procedure'.\n"
            "6. Go to Report, click 'Generate Report', then 'Submit Report to EMR/PACS'."
        ),
        "checker": "check_full_colonoscopy_workflow",
        "expected_values": {"target_idx": 7},
    },
    {
        "task_id": "medgym.endoscopy.multi_case_workflow",
        "difficulty": "hard",
        "goal_intent": (
            "Complete procedures and submit reports for two patients: "
            "Chen Jing (ENDO-004) and Liu Yang (ENDO-005)."
        ),
        "goal_step": (
            "1. Log in.\n"
            "2. Select ENDO-004, complete preassess → procedure → report → submit.\n"
            "3. Return to worklist.\n"
            "4. Select ENDO-005, complete preassess → procedure → report → submit."
        ),
        "checker": "check_multi_case_workflow",
        "expected_values": {"target_indices": [3, 4]},
    },
]

TASK_MAP = {cfg["task_id"]: cfg for cfg in TASK_CONFIGS}
TASK_IDS = [f"{cfg['task_id']}.{s}" for cfg in TASK_CONFIGS for s in SETTINGS]


# ─────────────────────────────────────────────────────────────────
# Checkers (all deterministic)
# ─────────────────────────────────────────────────────────────────

async def check_login(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    return {"passed": state.get("loggedIn", False) is True}


async def check_view_schedule(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    exp = task_cfg["expected_values"]["expected_count"]
    resp = get_agent_response(chat_messages)
    return {"passed": state.get("loggedIn", False) and str(exp) in (resp or "")}


async def check_select_case(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    return {"passed": state.get("selectedCaseIdx") == idx}


async def check_view_patient_info(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    exp_asa = task_cfg["expected_values"]["expected_asa"]
    resp = get_agent_response(chat_messages)
    return {"passed": str(exp_asa) in (resp or "")}


async def check_complete_preassess(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    cases = state.get("cases", [])
    if idx < len(cases):
        return {"passed": cases[idx].get("preAssessComplete", False)}
    return {"passed": False}


async def check_mark_landmarks(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    cases = state.get("cases", [])
    if idx < len(cases):
        c = cases[idx]
        total = len(c.get("landmarks", []))
        marked = len(c.get("landmarksMarked", []))
        return {"passed": marked == total and total > 0}
    return {"passed": False}


async def check_score_bbps(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    exp = task_cfg["expected_values"]["expected_bbps"]
    cases = state.get("cases", [])
    if idx < len(cases):
        bbps = cases[idx].get("bbps", {})
        return {
            "passed": (
                bbps.get("right") == exp["right"]
                and bbps.get("transverse") == exp["transverse"]
                and bbps.get("left") == exp["left"]
            )
        }
    return {"passed": False}


async def check_record_finding(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    cases = state.get("cases", [])
    if idx < len(cases):
        return {"passed": len(cases[idx].get("findingsRecorded", [])) > 0}
    return {"passed": False}


async def check_complete_procedure(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    cases = state.get("cases", [])
    if idx < len(cases):
        c = cases[idx]
        return {
            "passed": (
                c.get("status") == "completed"
                and c.get("preAssessComplete", False)
                and len(c.get("findingsRecorded", [])) > 0
            )
        }
    return {"passed": False}


async def check_submit_report(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    cases = state.get("cases", [])
    if idx < len(cases):
        return {"passed": cases[idx].get("reportSubmitted", False)}
    return {"passed": False}


async def check_full_colonoscopy_workflow(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    idx = task_cfg["expected_values"]["target_idx"]
    cases = state.get("cases", [])
    if idx < len(cases):
        c = cases[idx]
        bbps = c.get("bbps", {})
        return {
            "passed": (
                c.get("preAssessComplete", False)
                and c.get("status") == "completed"
                and c.get("cecalIntubation") is True
                and bbps.get("right") is not None
                and bbps.get("transverse") is not None
                and bbps.get("left") is not None
                and len(c.get("findingsRecorded", [])) > 0
                and c.get("reportSubmitted", False)
            )
        }
    return {"passed": False}


async def check_multi_case_workflow(page, chat_messages, task_cfg, **kw):
    state = await get_task_state(page)
    indices = task_cfg["expected_values"]["target_indices"]
    cases = state.get("cases", [])
    all_done = all(
        cases[i].get("reportSubmitted", False)
        for i in indices
        if i < len(cases)
    )
    return {"passed": all_done}
