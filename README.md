# MedCUA-BenchMark

> **MedCUA** — a Medical-domain Computer-Use Agent benchmark built on top of
> [BrowserGym](https://github.com/ServiceNow/BrowserGym).

This repository publishes the **benchmark standard** only — the task
definitions, scenario UIs, checker / scoring logic and safety rubric used to
evaluate Computer-Use Agents (CUA) on clinical GUI workflows.

It does **not** ship model weights, agent implementations, run logs or
result tables. The benchmark is meant to be used to evaluate *your* agent.

- 18 clinical scenarios across 10 medical domains
- 216 base tasks × 2 goal settings = **432 registered gymnasium environments**
- Pure CUA setup: agents receive **only browser screenshots** and use
  coordinate/keyboard and browser-control actions — no DOM, accessibility
  tree, or element-ID actions
- Safety-aware scoring (5 dimensions × 3 severities) so violations
  *reduce* the reward below what inaction would receive
  (Primum Non Nocere)

---

## Benchmark Structure

| Domain | Scenario | Tasks | UI Backend |
|--------|----------|------:|------------|
| **Outpatient / ED** | `emergency_triage` | 12 | Self-contained HTML |
| | `outpatient_pharmacy` | 12 | Self-contained HTML |
| | `doctor_prescription` | 12 | Self-contained HTML (RPMS-EHR e-Prescribing) |
| **Inpatient** | `openemr` (EMR + CPOE) | 12 | **OpenEMR v7.0.2** (Docker) |
| | `bed_management` | 12 | Self-contained HTML |
| **Nursing** | `nurse_station` | 12 | Self-contained HTML |
| | `nursing_documentation` | 12 | Self-contained HTML |
| | `nursing_assessment` | 12 | Self-contained HTML |
| **ICU / Critical Care** | `icu_central` | 12 | Self-contained HTML |
| | `icu_bedside` | 12 | Self-contained HTML |
| | `infusion_pump` | 12 | Self-contained HTML |
| **Imaging — PACS / Pathology** | `pacs_radiology` | 12 | **OHIF Viewer** (DICOM) |
| | `pathology_viewer` | 12 | **OHIF Viewer** (WSI) |
| **Imaging — Acquisition** | `imaging_console` | 12 | Self-contained HTML |
| **Radiation Therapy** | `radiation_tps` | 12 | Self-contained HTML |
| **Cardiology** | `ecg_workstation` | 12 | Self-contained HTML |
| **Endoscopy** | `endoscopy` | 12 | Self-contained HTML |
| **Ultrasound** | `ultrasound` | 12 | Self-contained HTML |

**Total: 18 scenarios × 12 tasks × 2 settings = 432 registered environments**

### Three UI Backends

| Backend | Scenarios | How it works |
|---------|-----------|--------------|
| **Self-contained HTML** | 15 | Single HTML files with embedded JS, served via `file://` |
| **OpenEMR** (Docker) | 1 (`openemr`) | Real open-source certified EHR on Docker (port 8300) |
| **OHIF Viewer** | 2 (`pacs_radiology`, `pathology_viewer`) | Real DICOM viewer with public DICOMweb server (port 3001) |

### Goal Settings

Each task is registered under two goal settings:

- **`intent`** — high-level clinical goal only
  *(e.g. "Triage the patient and assign an ESI level")*
- **`step`** — explicit step-by-step instructions
  *(e.g. "1. Log in 2. Open patient 3. Record vitals 4. Assign ESI 3")*

### Safety Evaluation

All tasks are graded with a safety-aware scoring system:

- **5 Safety Dimensions** — Patient Identity, Data Accuracy, Information
  Fidelity, Record Integrity, Workflow Safety
- **3 Severity Levels** — CRITICAL (−1.0), MAJOR (−0.3), MINOR (−0.05)
- **Primum Non Nocere** — safety violations can reduce the reward below
  what doing nothing would have scored

See [SCENARIOS.md](SCENARIOS.md) for the per-scenario task list and
checker logic.

> [!IMPORTANT]
> MedCUA-Bench is a research benchmark, not a clinical decision-support
> system or a safety certification. It contains synthetic demonstration
> patients only and must not be connected to production clinical systems or
> real patient data.

---

## Repository Layout

```
MedCUA-BenchMark/
├── README.md
├── SCENARIOS.md                     # Per-scenario task & checker documentation
├── LICENSE                          # Apache-2.0
├── NOTICE
├── pyproject.toml
├── requirements.txt
├── CITATION.cff
├── tests/test_release.py            # Registration, resource, and scoring checks
│
├── scenarios/                       # HTML apps for the 15 self-contained scenarios
│   ├── doctor_prescription/         # ← RPMS-EHR e-Prescribing (latest version)
│   ├── emergency_triage/
│   ├── endoscopy/
│   ├── …
│   └── ultrasound/
│
├── ohif/                            # Pinned OHIF data-source configuration
├── openemr/                         # OpenEMR deployment for inpatient EMR + CPOE
│   ├── docker-compose.yml           #   Start:  docker compose up -d
│   └── seed_demo_data.py            #   Seeds 5 demo patients with clinical data
│
└── src/browsergym/medgym/
    ├── __init__.py                  # Task registration (all 432 IDs)
    ├── safety.py                    # SafetyEvalResult, SafetyViolation, dimensions
    ├── answer_match.py              # Free-text answer matching helpers
    ├── protocol.py                  # Official screenshot-only protocol
    │
    ├── base_task.py                 # MedGymScenarioTask — base for HTML scenarios
    ├── ohif_task.py                 # MedGymOHIFTask     — base for OHIF scenarios
    ├── openemr_task.py              # OpenEMRTask        — inpatient EMR + CPOE
    │
    └── scenarios/
        ├── __init__.py              # Module registry (ALL_SCENARIO_MODULES)
        ├── doctor_prescription.py   # 12 tasks + checkers (RPMS-EHR e-Prescribing)
        ├── emergency_triage.py      # 12 tasks + checkers (HTML)
        ├── pacs_radiology.py        # 12 tasks + checkers (OHIF)
        ├── pathology_viewer.py      # 12 tasks + checkers (OHIF)
        ├── …
        └── ultrasound.py
```

> The OHIF Viewer source tree is **not** vendored here (it is a multi-GB
> upstream project). See [Starting UI backends](#starting-ui-backends) below
> to fetch it on demand.

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/Jia7878/MedCUA-BenchMark.git
cd MedCUA-BenchMark
python -m pip install -e .
python -m playwright install chromium
```

This installs `browsergym-medgym`, which pulls in
[`browsergym-core`](https://pypi.org/project/browsergym-core/) from PyPI.

### 2. Verify task registration

```python
import browsergym.medgym
print(len(browsergym.medgym.ALL_MEDGYM_TASK_IDS))   # → 432
```

### 3. Launch a benchmark-conformant task

```python
import browsergym.medgym
from browsergym.medgym import make_env

env = make_env("medgym.emergency_triage.login.intent", headless=True)
obs, info = env.reset(seed=42)
# obs["screenshot"] — browser screenshot (numpy array)
# obs["goal"]       — task description

obs, reward, done, truncated, info = env.step('mouse_click(350, 200)')
env.close()
```

Use `make_env` for reported benchmark results. BrowserGym's lower-level
`gym.make(...)` entry point retains DOM, accessibility-tree, URL, and
element-ID fields for debugging; `make_env` removes those fields and restricts
the agent to one action per step from the paper's action set: coordinate and
keyboard primitives, browser navigation/tab controls, user messaging, and
infeasibility reporting. Element-ID actions such as `click(bid)` and
`fill(bid, ...)` are excluded.

---

## Starting UI Backends

### Self-contained HTML scenarios (15)

No server is needed. Pages are loaded via the `file://` protocol from the
scenario resources included with the source checkout or installed wheel.

### OpenEMR (`openemr` scenario — requires Docker)

```bash
# macOS with Homebrew (one-time)
brew install colima docker docker-compose
colima start --cpu 2 --memory 4

# Bring up OpenEMR
cd openemr
docker compose up -d                  # OpenEMR at http://localhost:8300
python seed_demo_data.py              # Seeds 5 demo patients

# Default credentials: admin / pass
# Override URL: export MEDGYM_OPENEMR_URL=http://localhost:8300
```

### OHIF Viewer (`pacs_radiology`, `pathology_viewer` — requires Node.js)

The OHIF Viewer is fetched from upstream (not vendored). The benchmark was
validated against tag `v3.13.0-beta.56`. Its public DICOMweb endpoint is
mutable, so MedCUA-Bench includes a local QIDO proxy that fixes the study list
to the 30-study cohort used by the task definitions while forwarding image
requests to the public endpoint.

Start the QIDO proxy in one terminal:

```bash
python ohif/qido_proxy.py
```

In a second terminal, start the pinned OHIF Viewer with the supplied
configuration:

```bash
git clone --depth 1 --branch v3.13.0-beta.56 \
  https://github.com/OHIF/Viewers.git ohif-viewer
cp ohif/medcua.js ohif-viewer/platform/app/public/config/medcua.js
cd ohif-viewer
yarn install --frozen-lockfile
OHIF_PORT=3001 APP_CONFIG=config/medcua.js yarn run dev
# Override URL: export MEDGYM_OHIF_URL=http://localhost:3001
```

---

## Programmatic Examples

```python
import browsergym.medgym
from browsergym.medgym import make_env

# Self-contained HTML scenario
env = make_env("medgym.emergency_triage.assign_esi.step", headless=True)

# RPMS-EHR e-Prescribing
env = make_env("medgym.doctor_prescription.new_prescription.step", headless=True)

# OpenEMR inpatient scenario (requires Docker — see above)
env = make_env("medgym.openemr.find_patient.step", headless=True)

# OHIF Viewer scenario (requires OHIF on localhost:3001)
env = make_env("medgym.pacs_radiology.open_ct_study.step", headless=True)
```

All registered task IDs are available as
`browsergym.medgym.ALL_MEDGYM_TASK_IDS`.

---

## Reproducibility Checks

The release supports Python 3.10--3.12 and is tested with
`browsergym-core==0.14.2`.
Before running an agent sweep, verify the package and all task definitions:

```bash
python -m unittest discover -s tests -v
```

The OpenEMR credentials and database passwords in `openemr/docker-compose.yml`
are intentionally fixed for the isolated benchmark deployment. Its published
ports bind to `127.0.0.1` only. Do not expose this deployment to a public
network.

## Citation

Please cite the EMNLP 2026 paper described in [CITATION.cff](CITATION.cff).

---


## License

Apache-2.0 — see [LICENSE](LICENSE).
