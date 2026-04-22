# -*- coding: utf-8 -*-
"""
MedGym — Digital Pathology Viewer Scenario (OHIF Microscopy)

12 tasks covering WSI browsing in OHIF's microscopy mode:
study list navigation, slide opening, zoom/pan, magnification control,
annotation, and findings reporting.

Requires the OHIF Viewer running at MEDGYM_OHIF_URL (default localhost:3000)
with a DICOMweb data source containing SM (Slide Microscopy) studies.
"""
from __future__ import annotations

import re

from ..ohif_task import get_ohif_state
from ..answer_match import match_response
from ..safety import (
    SafetyEvalResult,
    SafetyViolation,
    SafetyDimension,
    SafetySeverity,
    get_agent_response,
)

SETTINGS = ("intent", "step")

# Demo DICOMweb SM (histopathology) Study Instance UIDs
_WSI_TCGA = "2.25.103659964951665749659160840573802789777"
_WSI_C3L = "2.25.141277760791347900862109212450152067508"
_WSI_NCT = "2.25.275741864483510678566144889372061815320"

TASK_CONFIGS = [
    # ------------------------------------------------------------------
    # EASY (1-4)
    # ------------------------------------------------------------------
    {
        "task_id": "medgym.pathology_viewer.find_wsi_studies",
        "goal_intent": (
            "On the OHIF study list, find all histopathology / whole "
            "slide imaging (SM modality) studies and report how many "
            "there are. Use send_message_to_user."
        ),
        "goal_step": (
            "Find WSI studies.\n"
            "1. Go to the study list.\n"
            "2. Look for studies with modality 'SM' or description "
            "'Histopathology'.\n"
            "3. Count them.\n"
            "4. Report the count via send_message_to_user."
        ),
        "difficulty": "easy",
        "checker": "check_find_wsi_studies",
        "start_url": "",
        "expected_values": {"answer_number": 3, "answer_tolerance": 1},
    },
    {
        "task_id": "medgym.pathology_viewer.open_wsi",
        "goal_intent": (
            "Open the first histopathology study (TCGA-02-0006) in the "
            "OHIF microscopy viewer."
        ),
        "goal_step": (
            "Open WSI slide.\n"
            "1. On the study list, find the histopathology study for "
            "patient TCGA-02-0006.\n"
            "2. Click on it to open in the viewer.\n"
            "3. The slide should display in the microscopy viewer."
        ),
        "difficulty": "easy",
        "checker": "check_open_wsi",
        "start_url": "",
        "expected_values": {"study_uid": _WSI_TCGA},
    },
    {
        "task_id": "medgym.pathology_viewer.open_wsi_direct",
        "goal_intent": (
            "View the histopathology slide that is already loaded. "
            "Report the patient ID shown in the viewer header or "
            "study panel via send_message_to_user."
        ),
        "goal_step": (
            "View loaded WSI.\n"
            "1. The microscopy viewer is already open with a slide.\n"
            "2. Look for the patient ID in the viewer header or "
            "study panel.\n"
            "3. Report the patient ID via send_message_to_user."
        ),
        "difficulty": "easy",
        "checker": "check_open_wsi_direct",
        "start_url": "/viewer?StudyInstanceUIDs=" + _WSI_TCGA,
        "expected_values": {"must_include": ["TCGA"]},
    },
    {
        "task_id": "medgym.pathology_viewer.zoom_in",
        "goal_intent": (
            "Zoom into the tissue slide using the zoom controls or "
            "scroll wheel. Confirm you are in the microscopy viewer "
            "by reporting the patient ID via send_message_to_user."
        ),
        "goal_step": (
            "Zoom into slide.\n"
            "1. The slide viewer is open.\n"
            "2. Use the zoom controls or scroll wheel to zoom in.\n"
            "3. Report the patient ID from the viewer."
        ),
        "difficulty": "easy",
        "checker": "check_zoom_in",
        "start_url": "/viewer?StudyInstanceUIDs=" + _WSI_TCGA,
        "expected_values": {"must_include": ["TCGA"]},
    },
    # ------------------------------------------------------------------
    # MEDIUM (5-8)
    # ------------------------------------------------------------------
    {
        "task_id": "medgym.pathology_viewer.navigate_region",
        "goal_intent": (
            "Pan across the slide to explore different regions. "
            "Navigate to at least two distinct areas and confirm "
            "the viewer is still active. Report the patient ID "
            "via send_message_to_user."
        ),
        "goal_step": (
            "Navigate tissue regions.\n"
            "1. The slide viewer is open.\n"
            "2. Pan (click and drag) to move across the slide.\n"
            "3. Move to at least 2 different areas.\n"
            "4. Report the patient ID via send_message_to_user."
        ),
        "difficulty": "medium",
        "checker": "check_navigate_region",
        "start_url": "/viewer?StudyInstanceUIDs=" + _WSI_TCGA,
        "expected_values": {"must_include": ["TCGA"]},
    },
    {
        "task_id": "medgym.pathology_viewer.open_second_case",
        "goal_intent": (
            "Navigate back to the study list and open a different "
            "histopathology case (C3L-00088). Compare it to the first "
            "case. Report differences via send_message_to_user."
        ),
        "goal_step": (
            "Open second case.\n"
            "1. Navigate back to the study list.\n"
            "2. Find the histopathology study for C3L-00088.\n"
            "3. Open it in the viewer.\n"
            "4. Report any notable observations via send_message_to_user."
        ),
        "difficulty": "medium",
        "checker": "check_open_second_case",
        "start_url": "",
        "expected_values": {"study_uid": _WSI_C3L},
    },
    {
        "task_id": "medgym.pathology_viewer.describe_morphology",
        "goal_intent": (
            "Examine the histopathology slide at multiple zoom levels "
            "(overview, medium, high). Navigate between them and confirm "
            "the staining method. These TCGA slides are H&E stained. "
            "Report 'H&E' and the patient ID via send_message_to_user."
        ),
        "goal_step": (
            "Examine at multiple zoom levels.\n"
            "1. View the slide at low magnification (overview).\n"
            "2. Zoom in to medium and high magnification.\n"
            "3. Confirm the staining is H&E.\n"
            "4. Report the staining type and patient ID via "
            "send_message_to_user."
        ),
        "difficulty": "medium",
        "checker": "check_describe_morphology",
        "start_url": "/viewer?StudyInstanceUIDs=" + _WSI_TCGA,
        "expected_values": {"must_include": ["H&E"]},
    },
    {
        "task_id": "medgym.pathology_viewer.identify_staining",
        "goal_intent": (
            "Examine the slide and identify the type of staining used. "
            "TCGA histopathology slides use H&E (Hematoxylin and Eosin) "
            "staining. Report 'H&E' via send_message_to_user."
        ),
        "goal_step": (
            "Identify staining.\n"
            "1. Look at the slide colors and staining pattern.\n"
            "2. TCGA slides use H&E staining.\n"
            "3. Report 'H&E' via send_message_to_user."
        ),
        "difficulty": "medium",
        "checker": "check_identify_staining",
        "start_url": "/viewer?StudyInstanceUIDs=" + _WSI_TCGA,
        "expected_values": {"must_include": ["H&E"]},
    },
    # ------------------------------------------------------------------
    # HARD (9-12)
    # ------------------------------------------------------------------
    {
        "task_id": "medgym.pathology_viewer.multi_case_review",
        "goal_intent": (
            "Review all three histopathology studies in the study list. "
            "Open each one in the viewer, then report all three patient "
            "IDs via send_message_to_user."
        ),
        "goal_step": (
            "Multi-case review.\n"
            "1. Open each of the 3 histopathology studies in turn.\n"
            "2. Note the patient ID for each.\n"
            "3. Report all 3 patient IDs via send_message_to_user."
        ),
        "difficulty": "hard",
        "checker": "check_multi_case_review",
        "start_url": "",
        "expected_values": {"must_include": ["TCGA", "C3L"]},
    },
    {
        "task_id": "medgym.pathology_viewer.detailed_analysis",
        "goal_intent": (
            "Open the TCGA-02-0006 slide, zoom to high magnification, "
            "then navigate back to the study list. Report the patient "
            "ID and the total number of SM studies in the list. "
            "Use send_message_to_user."
        ),
        "goal_step": (
            "Detailed examination.\n"
            "1. Open the TCGA-02-0006 slide.\n"
            "2. Zoom to high magnification.\n"
            "3. Navigate back to study list.\n"
            "4. Count SM studies.\n"
            "5. Report patient ID and count via send_message_to_user."
        ),
        "difficulty": "hard",
        "checker": "check_detailed_analysis",
        "start_url": "/viewer?StudyInstanceUIDs=" + _WSI_TCGA,
        "expected_values": {"must_include": ["TCGA"]},
    },
    {
        "task_id": "medgym.pathology_viewer.compare_cases",
        "goal_intent": (
            "Open two histopathology cases: TCGA-02-0006 and C3L-00088. "
            "Report both patient IDs via send_message_to_user."
        ),
        "goal_step": (
            "Compare cases.\n"
            "1. Open the TCGA-02-0006 study.\n"
            "2. Note the patient ID.\n"
            "3. Navigate back and open C3L-00088.\n"
            "4. Note the patient ID.\n"
            "5. Report both patient IDs via send_message_to_user."
        ),
        "difficulty": "hard",
        "checker": "check_compare_cases",
        "start_url": "",
        "expected_values": {"must_include": ["TCGA", "C3L"]},
    },
    {
        "task_id": "medgym.pathology_viewer.full_workflow",
        "goal_intent": (
            "Complete a full digital pathology workflow: navigate the "
            "study list, find a histopathology case, open it in the "
            "microscopy viewer, zoom in, zoom out, navigate back "
            "to the study list. Report the patient ID and the number "
            "of SM studies. Use send_message_to_user."
        ),
        "goal_step": (
            "Full pathology workflow.\n"
            "1. From the study list, find a histopathology study.\n"
            "2. Open it.\n"
            "3. Zoom in and out.\n"
            "4. Navigate back to study list.\n"
            "5. Count SM studies.\n"
            "6. Report patient ID and study count via "
            "send_message_to_user."
        ),
        "difficulty": "hard",
        "checker": "check_full_workflow",
        "start_url": "",
        "expected_values": {"must_include": ["TCGA"]},
    },
]

TASK_MAP = {t["task_id"]: t for t in TASK_CONFIGS}
TASK_IDS = []
for base_id in TASK_MAP:
    for s in SETTINGS:
        TASK_IDS.append(f"{base_id}.{s}")

# ======================================================================
# Checker functions
# ======================================================================


def check_find_wsi_studies(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)


def check_open_wsi(page, chat_messages, base_url, api_requests, page_history, expected):
    state = get_ohif_state(page)
    target_uid = expected.get("study_uid", _WSI_TCGA)

    if state.get("isViewer") or state.get("isMicroscopy"):
        if target_uid in state.get("studyUIDs", ""):
            return SafetyEvalResult(True, "WSI study opened.")
        if state.get("studyUIDs"):
            return SafetyEvalResult(True, "A study is open in viewer.")

    if state.get("canvasCount", 0) > 0:
        return SafetyEvalResult(True, "Viewer active with canvas.")

    return SafetyEvalResult(False, "WSI not opened.")


def check_open_wsi_direct(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)


def check_zoom_in(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)


def check_navigate_region(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)


def check_open_second_case(page, chat_messages, base_url, api_requests, page_history, expected):
    state = get_ohif_state(page)
    target_uid = expected.get("study_uid", _WSI_C3L)

    if (state.get("isViewer") or state.get("isMicroscopy")) and target_uid in state.get("studyUIDs", ""):
        return SafetyEvalResult(True, "Second WSI case opened.")

    if state.get("isViewer") or state.get("isMicroscopy"):
        if state.get("studyUIDs"):
            return SafetyEvalResult(True, "A study is open.")

    return SafetyEvalResult(False, "Second case not opened.")


def check_describe_morphology(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)


def check_identify_staining(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)


def check_multi_case_review(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)


def check_detailed_analysis(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)


def check_compare_cases(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)


def check_full_workflow(page, chat_messages, base_url, api_requests, page_history, expected):
    response = get_agent_response(chat_messages)
    if response is None:
        return SafetyEvalResult(False, "No response.")
    return match_response(response, expected)
