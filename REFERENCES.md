# MedGym — Real-World Reference Sources

Every MedGym scenario is grounded in one of: (1) a real open-source medical UI,
(2) published product documentation / user manuals, or (3) peer-reviewed
clinical standards and assessment tools.

This file lists, for each of the **18 scenarios**, the system or standard the UI
mock-up is based on, the version used (where applicable), and the canonical citations.

---

## Open-Source UI Backends (fully functional real applications)

### OpenEMR — Inpatient EMR & CPOE
- **Scenarios**: `medgym.openemr.*` (12 tasks)
- **Source**: https://github.com/openemr/openemr (5.1k+ ⭐, GPL-3.0)
- **Version**: 7.0.2 (Docker image `openemr/openemr:7.0.2`)
- **Features used**: Patient registration, demographics, encounter creation,
  prescriptions (e-prescribing), procedure/lab orders, allergy documentation,
  medical problem lists, medication review, drug-allergy checking, vitals
- **Certification**: ONC Health IT Certified (21st Century Cures Act)
- **Documentation**: https://www.open-emr.org/wiki/

### OHIF Viewer — Medical Imaging & Pathology
- **Scenarios**: `medgym.pacs_radiology.*`, `medgym.pathology_viewer.*` (24 tasks)
- **Source**: https://github.com/OHIF/Viewers (5.9k+ ⭐, MIT)
- **Features used**: CT/MR DICOM viewing, window/level, measurements,
  whole-slide microscopy navigation
- **DICOMweb backend**: https://d14fa38qiwhyfd.cloudfront.net/dicomweb (public OHIF demo)

---

## HTML Scenarios — Product Documentation & Clinical Standard References

### emergency_triage (急诊分诊)
- **Primary reference**: AHRQ ESI Implementation Handbook v4
  - Gilboy N, Tanabe T, Travers D, Rosenau AM. *Emergency Severity Index (ESI):
    A Triage Tool for Emergency Department Care, Version 4. Implementation
    Handbook.* AHRQ Publication No. 12-0014. Rockville, MD: 2012.
  - URL: https://www.ahrq.gov/patient-safety/settings/emergency/esi.html
- **ESI 5-Level Algorithm**: Standardized ED triage protocol used in >85% of US
  emergency departments (ACEP/ENA endorsed)
- **UI reference**: Epic Emergency Department module (Triage workflow)
- **Clinical standard**: Joint Commission Emergency Management Standards (EM.02.02.01)

### outpatient_pharmacy (门诊药房)
- **Primary reference**: ASHP (American Society of Health-System Pharmacists)
  Best Practices for Hospital & Health-System Pharmacy
  - URL: https://www.ashp.org/pharmacy-practice/policy-positions-and-best-practices/best-practices
- **Prescription processing workflow**: NCPDP (National Council for Prescription
  Drug Programs) SCRIPT Standard v2017071
- **Drug interaction checking**: FDA Drug Interactions database
  - URL: https://www.fda.gov/drugs/drug-interactions-labeling
- **UI reference**: Baxter DoseEdge pharmacy workflow system
- **Dispensing workflow**: USP Chapter 795 (Pharmaceutical Compounding — Nonsterile)

### doctor_prescription (医师处方 — SmartCare Rx)
- **Primary reference**: CalMHSA Specialty Mental Health Services Clinical
  Documentation User Guide — Prescription Support Services (SmartCare Rx module)
- **Secondary reference**: IHS RPMS EHR Surescripts eRx documentation
  (Renewal Queue, Cancel Order, Mailbox)
- **Workflow features**: Patient search, medication list, allergy/intolerance
  documentation, preferred-pharmacy configuration, new prescription, outside
  medication, dual-signature consent, change/discontinue order, renewal handling,
  full prescription workflow
- **Standards**: NCPDP SCRIPT, Joint Commission MM.05.01

### bed_management (床位管理)
- **Primary reference**: Epic BedTracking / Bed Management module
  - Commercial reference: Epic Systems Corporation, Verona, WI
  - Feature set: Real-time bed status, admission/discharge/transfer (ADT),
    bed request management, environmental services coordination
- **ADT standards**: HL7 v2.x ADT message types (A01-A13)
  - URL: https://www.hl7.org/implement/standards/product_brief.cfm?product_id=185
- **Patient-flow methodology**: IHI (Institute for Healthcare Improvement)
  Patient Flow improvement program

### nurse_station (护士工作站 — PowerChart / Care Compass)
- **Primary references**:
  - Cerner (Oracle Health) PowerChart Manual — Task List Tab (May 2023)
  - Care Compass Quick Reference Guide (Oct 2023)
- **Features used**: Care Compass multi-patient overview, nurse-patient
  relationships, task completion (Done / Not Done / Document), specimen
  collection sign-off, new/STAT order review, patient snapshot, overdue task
  management, batch order review, full shift workflow
- **Clinical standards**:
  - ANA Nursing Informatics: Scope & Standards, 3rd Ed.
  - Joint Commission NPSG.01.01.01, NPSG.03.04.01

### nursing_documentation (护理记录与体征)
- **Primary reference**: ANA (American Nurses Association) Nursing Informatics:
  Scope and Standards of Practice, 3rd Edition (2022)
- **Vital signs charting**: CDC NHANES vital sign measurement protocols
- **I&O recording**: AACN Procedure Manual for High Acuity, Progressive, and
  Critical Care, 7th Edition
- **SBAR handoff**: IHI SBAR Technique for Communication
  - URL: https://www.ihi.org/resources/Pages/Tools/SBARTechniqueforCommunicationASituationalBriefingModel.aspx
- **Note templates**: HL7 CDA Nursing Note template
- **Wound assessment**: WOCN Society Wound Assessment Guidelines

### nursing_assessment (护理评估量表)
- **Braden Pressure Ulcer Scale**:
  - Bergstrom N, Braden BJ, Laguzza A, Holman V. *The Braden Scale for
    Predicting Pressure Sore Risk.* Nursing Research. 1987;36(4):205-210.
  - 6 subscales, total score 6-23, cutoff ≤18 = at-risk
- **Morse Fall Scale**:
  - Morse JM, Morse RM, Tylko SJ. *Development of a Scale to Identify the
    Fall-Prone Patient.* Canadian Journal of Aging. 1989;8(4):366-377.
  - 6 items, total 0-125, cutoff ≥45 = high risk
- **Glasgow Coma Scale (GCS)**:
  - Teasdale G, Jennett B. *Assessment of coma and impaired consciousness:
    A practical scale.* The Lancet. 1974;304(7872):81-84.
- **NRS Pain Scale (0-10)**:
  - McCaffery M, Beebe A. *Pain: Clinical Manual for Nursing Practice.* Mosby, 1989.
  - Joint Commission Pain Management Standards (PC.01.02.07)
- **Nutrition screening**: MUST (Malnutrition Universal Screening Tool, BAPEN 2003)

### icu_central (ICU 中央监护站)
- **Primary reference**: Philips IntelliVue Patient Information Center iX (PIIC iX)
  - User manual: IntelliVue PIIC iX Rev. M, Document 4536 642 28541
- **Secondary reference**: Mindray BeneVision Central Monitoring System (CMS)
- **Alarm management**: IEC 60601-1-8:2020 — Medical electrical equipment,
  Part 1-8: General requirements for basic safety and essential performance —
  Collateral standard: Alarm systems
- **Clinical alarm standards**: AAMI/ANSI/IEC 60601-1-8 Clinical Alarm Conditions
- **Waveform display**: 12-lead ECG, SpO2 plethysmography, invasive arterial
  pressure, capnography, respiratory impedance

### icu_bedside (ICU 床旁终端)
- **Primary reference**: Philips IntelliVue MX800/MX850 Patient Monitor
  - Documentation: Release M.00.03, Document 4536 642 25441
  - Features: Waveform display, alarm management, trending, drug calculations
- **Secondary reference**: Dräger Infinity Acute Care System (IACS)
- **Ventilator integration**: AARC Clinical Practice Guidelines for ventilator management
- **Fluid balance**: AACN Procedure Manual — Intake/Output monitoring
- **ETCO2 monitoring**: AHA Guidelines — Confirming advanced airway placement

### infusion_pump (输液泵管理)
- **Primary reference**: BD Alaris Infusion System
  - Model: Alaris 8100 Series (PC Unit + pump modules)
  - Features: Drug library with dose limits, DERS (Dose Error Reduction System),
    titration controls, infusion history logging
- **Secondary references**:
  - Baxter Sigma Spectrum Infusion Pump
  - B. Braun Space Infusion System
- **Drug library standards**: ISMP Guidelines for Optimizing Safe Implementation
  and Use of Smart Infusion Pumps
  - URL: https://www.ismp.org/guidelines/safe-implementation-smart-pumps
- **Dose limit enforcement**: IEC 60601-2-24:2012 — Particular requirements for
  infusion pumps and controllers
- **Safety**: FDA Guidance: Infusion Pumps — Total Product Life Cycle (2014)

### imaging_console (影像扫描控制台)
- **Primary reference**: Siemens Healthineers syngo CT/MR scanner console
  - Product line: SOMATOM (CT), MAGNETOM (MRI)
- **Secondary references**: GE Healthcare Centricity, Philips IntelliSpace Portal
- **Dose monitoring**: ACR Dose Index Registry (DIR)
- **CT parameters**: AAPM Report No. 96 — *The Measurement, Reporting, and
  Management of Radiation Dose in CT*
- **MRI safety**: ACR Manual on MR Safety (2020)
- **QC protocols**: ACR CT Quality Control Manual

### radiation_tps (放疗计划系统)
- **Primary reference**: Varian Eclipse Treatment Planning System
  - Documentation: Varian Medical Systems (now Siemens Healthineers), Palo Alto, CA
- **Secondary references**: Elekta Monaco TPS, RaySearch RayStation TPS
- **Open-source reference**: matRad — Open-Source Treatment Planning System
  - Source: https://github.com/e0404/matRad
  - Wieser HP, et al. *Development of the open-source dose calculation and
    optimization toolkit matRad.* Med Phys. 2017;44(6):2556-2568.
- **Clinical standards**:
  - AAPM TG-53: *Quality assurance for clinical radiotherapy treatment planning*
  - ICRU Report 83: IMRT prescribing/recording/reporting
- **DVH constraints**: QUANTEC — Marks LB, et al. Int J Radiat Oncol Biol Phys. 2010;76(3).

### ecg_workstation (心电工作站)
- **Primary reference**: Generic cardiology ECG review workstation
  ("CardioView" — modeled after Philips IntelliSpace ECG and GE MUSE)
  - Features: Worklist, 12-lead waveform display, paper-speed/gain settings,
    Cabrera lead sequence, automated measurements (HR, PR, QRS, QT/QTc),
    auto-analysis, report submission, critical alert workflow
- **Clinical standards**:
  - AHA/ACCF/HRS Recommendations for the Standardization and Interpretation of
    the Electrocardiogram (Kligfield P, et al. Circulation 2007;115:1306-1324.)
  - Universal Definition of Myocardial Infarction (Fourth Edition, 2018)
- **Cabrera sequence**: Recommended by AHA/ACC for systematic axis review

### endoscopy (内镜工作站 — EVIS X1)
- **Primary reference**: Olympus EVIS X1 System (CV-1500 / CLV-S200)
  - Documentation: Olympus Corporation, Tokyo, Japan
  - Imaging modes: ENDO-AID CADe, NBI (Narrow Band Imaging), TXI (Texture and
    Color Enhancement Imaging), RDI (Red Dichromatic Imaging), EDOF
- **Quality indicators**: ASGE Quality Indicators for GI Endoscopy (2015, 2020)
- **Bowel preparation scoring**: Boston Bowel Preparation Scale (BBPS)
  - Lai EJ, et al. *The Boston Bowel Preparation Scale.* Gastrointest Endosc.
    2009;69(3 Pt 2):620-625.
- **Lesion classification**:
  - Paris Classification of Superficial Neoplastic Lesions (2002)
  - NICE Classification for colorectal polyps

### ultrasound (超声工作站)
- **Primary reference**: GE Healthcare LOGIQ E10s Ultrasound System
  - Operator Manual: GE Healthcare, Chicago, IL
- **Secondary reference**: Philips EPIQ Elite Ultrasound System
- **Reporting**: ACR (American College of Radiology) Ultrasound Accreditation
  Program requirements
  - URL: https://www.acraccreditation.org/modalities/ultrasound
- **BI-RADS / TI-RADS classification**:
  - ACR BI-RADS Atlas, 5th Edition (2013) — Breast ultrasound
  - ACR TI-RADS: Tessler FN, et al. *ACR Thyroid Imaging, Reporting and Data
    System (TI-RADS).* J Am Coll Radiol. 2017;14(5):587-595.
- **Probe selection**: AIUM Practice Parameters for ultrasound examinations

---

## Summary

| Scenario | Reference Type | Primary Reference |
|----------|---------------|-------------------|
| `openemr` | **Open-source UI** | OpenEMR v7.0.2 (GPL-3.0) |
| `pacs_radiology` | **Open-source UI** | OHIF Viewer (MIT) |
| `pathology_viewer` | **Open-source UI** | OHIF Viewer (MIT) |
| `emergency_triage` | Clinical standard | AHRQ ESI Handbook v4 |
| `outpatient_pharmacy` | Product doc + standard | ASHP Best Practices + NCPDP SCRIPT |
| `doctor_prescription` | Product doc | SmartCare Rx + IHS RPMS Surescripts eRx |
| `bed_management` | Product doc + standard | Epic BedTracking + HL7 ADT |
| `nurse_station` | Product doc | Cerner PowerChart + Care Compass |
| `nursing_documentation` | Clinical standard | ANA Nursing Informatics + IHI SBAR |
| `nursing_assessment` | Peer-reviewed scales | Braden / Morse / GCS / NRS / MUST |
| `icu_central` | Product doc + standard | Philips PIIC iX + IEC 60601-1-8 |
| `icu_bedside` | Product doc | Philips IntelliVue MX800 + Dräger IACS |
| `infusion_pump` | Product doc + standard | BD Alaris + IEC 60601-2-24 |
| `imaging_console` | Product doc | Siemens syngo + ACR DIR |
| `radiation_tps` | Product doc + open-source | Varian Eclipse + matRad + AAPM TG-53 |
| `ecg_workstation` | Product doc + guideline | CardioView + AHA/ACC ECG guidelines |
| `endoscopy` | Product doc + standard | Olympus EVIS X1 + ASGE QI + BBPS |
| `ultrasound` | Product doc + standard | GE LOGIQ E10s + ACR/AIUM guidelines |
