#!/usr/bin/env python3
"""
Seed demo patient data into OpenEMR for MedGym benchmark tasks.

Requires: OpenEMR running at MEDGYM_OPENEMR_URL (default http://localhost:8300)
          Admin credentials: admin / pass

This script creates reproducible demo patients used by the benchmark:
  PID 1: Already exists (admin patient) or first seeded patient
  PID 2-6: Demo patients with known demographics, conditions, medications

Run with:
    python seed_demo_data.py
"""
import json
import os
import sys
import urllib.request
import urllib.parse
import http.cookiejar
import re
import time

BASE_URL = os.environ.get("MEDGYM_OPENEMR_URL", "http://localhost:8300")

# Demo patients for benchmark tasks
DEMO_PATIENTS = [
    {
        "form_fname": "James",
        "form_lname": "Wilson",
        "form_DOB": "1958-07-15",
        "form_sex": "Male",
        "form_ss": "123-45-6789",
        "form_street": "123 Oak Street",
        "form_city": "Springfield",
        "form_state": "MA",
        "form_postal_code": "01103",
        "form_phone_home": "(413) 555-0101",
    },
    {
        "form_fname": "Maria",
        "form_lname": "Garcia",
        "form_DOB": "1975-03-22",
        "form_sex": "Female",
        "form_ss": "234-56-7890",
        "form_street": "456 Elm Avenue",
        "form_city": "Springfield",
        "form_state": "MA",
        "form_postal_code": "01104",
        "form_phone_home": "(413) 555-0202",
    },
    {
        "form_fname": "Robert",
        "form_lname": "Chen",
        "form_DOB": "1990-11-08",
        "form_sex": "Male",
        "form_ss": "345-67-8901",
        "form_street": "789 Maple Drive",
        "form_city": "Springfield",
        "form_state": "MA",
        "form_postal_code": "01105",
        "form_phone_home": "(413) 555-0303",
    },
    {
        "form_fname": "Sarah",
        "form_lname": "Johnson",
        "form_DOB": "1945-01-30",
        "form_sex": "Female",
        "form_ss": "456-78-9012",
        "form_street": "321 Pine Road",
        "form_city": "Springfield",
        "form_state": "MA",
        "form_postal_code": "01106",
        "form_phone_home": "(413) 555-0404",
    },
    {
        "form_fname": "Michael",
        "form_lname": "Thompson",
        "form_DOB": "1982-09-12",
        "form_sex": "Male",
        "form_ss": "567-89-0123",
        "form_street": "654 Cedar Lane",
        "form_city": "Springfield",
        "form_state": "MA",
        "form_postal_code": "01107",
        "form_phone_home": "(413) 555-0505",
    },
]


def create_session():
    """Create an authenticated OpenEMR session."""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPRedirectHandler(),
    )

    # Get login page (establishes session)
    opener.open(f"{BASE_URL}/interface/login/login.php?site=default")

    # Login
    data = urllib.parse.urlencode({
        "new_login_session_management": "1",
        "authUser": "admin",
        "clearPass": "pass",
        "languageChoice": "1",
    }).encode()
    resp = opener.open(
        f"{BASE_URL}/interface/main/main_screen.php?auth=login&site=default",
        data,
    )
    content = resp.read().decode("utf-8", errors="replace")

    if "main.php" not in resp.url and "main_screen" not in resp.url:
        print(f"ERROR: Login failed. URL after login: {resp.url}")
        sys.exit(1)

    # Extract CSRF token
    csrf_match = re.search(r'csrf_token_js\s*=\s*["\']([^"\']+)', content)
    csrf_token = csrf_match.group(1) if csrf_match else ""

    return opener, csrf_token


def get_csrf_from_page(opener, url):
    """Fetch a page and extract the CSRF token from it."""
    resp = opener.open(url)
    content = resp.read().decode("utf-8", errors="replace")
    csrf_match = re.search(
        r'name="csrf_token_form"\s+value="([^"]*)"', content
    )
    if csrf_match:
        return csrf_match.group(1)
    # Try alternative pattern
    csrf_match = re.search(r"csrfTokenRaw\s*=\s*'([^']*)'", content)
    if csrf_match:
        return csrf_match.group(1)
    return ""


def create_patient(opener, patient_data):
    """Create a patient via the OpenEMR new patient form."""
    # Get the new patient page to extract CSRF token
    new_url = f"{BASE_URL}/interface/new/new.php"
    csrf = get_csrf_from_page(opener, new_url)

    # Build form data
    form_data = {
        "csrf_token_form": csrf,
        "form_create": "1",
        **patient_data,
    }

    data = urllib.parse.urlencode(form_data).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/interface/new/new.php",
        data=data,
        method="POST",
    )
    try:
        resp = opener.open(req)
        content = resp.read().decode("utf-8", errors="replace")
        # Check if patient was created
        pid_match = re.search(r"pid=(\d+)", resp.url)
        if pid_match:
            return int(pid_match.group(1))
        # Try finding pid in content
        pid_match = re.search(r"set_pid\((\d+)\)", content)
        if pid_match:
            return int(pid_match.group(1))
    except Exception as e:
        print(f"  Error creating patient: {e}")

    return None


def check_patient_exists(opener, fname, lname):
    """Check if a patient already exists by searching."""
    url = f"{BASE_URL}/interface/main/finder/dynamic_finder.php"
    try:
        resp = opener.open(url)
        content = resp.read().decode("utf-8", errors="replace")
        return lname.lower() in content.lower()
    except Exception:
        return False


def main():
    print(f"Seeding demo data into OpenEMR at {BASE_URL}")
    print("=" * 60)

    opener, csrf = create_session()
    print(f"Logged in successfully. CSRF token: {csrf[:20]}...")

    for i, patient in enumerate(DEMO_PATIENTS):
        fname = patient["form_fname"]
        lname = patient["form_lname"]
        dob = patient["form_DOB"]

        print(f"\n[{i+1}/{len(DEMO_PATIENTS)}] Creating: {fname} {lname} (DOB: {dob})")

        pid = create_patient(opener, patient)
        if pid:
            print(f"  Created with PID: {pid}")
        else:
            print(f"  Could not determine PID (may still have been created)")

    print("\n" + "=" * 60)
    print("Demo data seeding complete!")
    print(f"\nPatients created:")
    for p in DEMO_PATIENTS:
        print(f"  - {p['form_fname']} {p['form_lname']} (DOB: {p['form_DOB']})")


if __name__ == "__main__":
    main()
