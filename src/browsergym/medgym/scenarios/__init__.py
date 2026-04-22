# -*- coding: utf-8 -*-
"""MedGym Scenarios Package — each submodule defines one clinical scenario.

10 Scenes × 19 Sub-workflows:
  1. Outpatient:    emergency_triage, outpatient_pharmacy, doctor_prescription
  2. Inpatient:     (OpenEMR), bed_management
  3. Nursing:       nurse_station, nursing_documentation, nursing_assessment
  4. ICU:           icu_central, icu_bedside, infusion_pump
  5. PACS/Path:     pacs_radiology, pathology_viewer  (OHIF)
  6. Imaging:       imaging_console
  7. RadTherapy:    radiation_tps
  8. ECG:           ecg_workstation
  9. Endoscopy:     endoscopy
 10. Ultrasound:    ultrasound
"""

from . import (
    bed_management,
    doctor_prescription,
    ecg_workstation,
    emergency_triage,
    endoscopy,
    icu_bedside,
    icu_central,
    imaging_console,
    infusion_pump,
    nurse_station,
    nursing_assessment,
    nursing_documentation,
    outpatient_pharmacy,
    pacs_radiology,
    pathology_viewer,
    radiation_tps,
    ultrasound,
)

# Ordered list of all scenario module objects
ALL_SCENARIO_MODULES = [
    bed_management,
    doctor_prescription,
    ecg_workstation,
    emergency_triage,
    endoscopy,
    icu_bedside,
    icu_central,
    imaging_console,
    infusion_pump,
    nurse_station,
    nursing_assessment,
    nursing_documentation,
    outpatient_pharmacy,
    pacs_radiology,
    pathology_viewer,
    radiation_tps,
    ultrasound,
]
