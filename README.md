# Axiom AI

Axiom AI is an evidence-gated government technology evaluation and procurement platform that converts high-level government problem statements into measurable Outcome Contracts, evaluates startup solutions against realistic Government Pilot Twins across orthogonal deployment strata, independently validates evidence with cryptographic provenance, maps localized failure points via Failure Cartography, generates forensic diagnostic intelligence, and provides deterministic procurement and scale-up recommendations while keeping final authorization exclusively with human officers.

## The Problem

Government departments struggle to discover, evaluate, pilot, validate, and scale innovative startup solutions through transparent and evidence-based procurement. Traditional procurement relies on unverified vendor claims, subjective evaluations, and static compliance checklists, leading to high failure rates when solutions are deployed in challenging, real-world rural conditions (intermittent connectivity, low-end devices, regional vernaculars, and degraded inputs).

## Core Architecture

```
Problem Statement
      ↓
Outcome Contract
      ↓
Government Pilot Twin
      ↓
Private Test Matrix
      ↓
Self-Verified Evaluator (Golden Reference Suite)
      ↓
Independent Evaluation
      ↓
Evidence (Cryptographic Provenance)
      ↓
Failure Cartography
      ↓
Diagnostic Intelligence
      ↓
Procurement Recommendation (Deterministic Gates)
      ↓
Human Authorization (Maker-Checker Boundary)
      ↓
Safe Scale-Up (Regional Re-Gating)
```

## Core Principle

> **"AI assists. Evidence proves. Rules gate. Humans authorize."**

---

## Quickstart

### 1. Environment Setup (Windows PowerShell)

```powershell
# Create virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt
```

*(On Linux / macOS: `source .venv/bin/activate`)*

### 2. Run Test Suite

Run the full offline governance, API, and demo scenario test suite:
```powershell
python -m pytest -v
```

### 3. Start the API Server

```powershell
python -m uvicorn app.main:app --reload
```

- **Interactive API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Canonical Demonstration Scenario

Axiom AI provides a ready-to-run demonstration scenario:

- **Scenario ID:** `AXIOM-DEMO-001`
- **Title:** `"Rural Agricultural Logistics — Evidence-Gated Procurement"`
- **Department:** `"Department of Agricultural Logistics"`
- **District:** `"Rural Demonstration District"`
- **Problem Statement:**
  > *"Improve last-mile delivery of agricultural supplies across rural districts while reducing delivery delays and maintaining reliable service under intermittent connectivity, low-end devices, regional languages, and degraded input conditions."*

### Evaluated Vendors (Fictional Demonstration Profiles)

1. **Vendor A (`VendorA`):** *"AgriRoute Systems"* — High-throughput route optimizer with standard device focus. Exhibits performance degradation under noisy regional conditions.
2. **Vendor B (`VendorB`):** *"RuralFlow AI"* — Offline-first resilient routing engine designed for intermittent connectivity. Satisfies all baseline rural pilot criteria.
3. **Vendor C (`VendorC`):** *"KrishiLink Technologies"* — Deep learning vernacular voice/text dispatch platform. Achieves high overall benchmark accuracy (91.67%), but exhibits an acute compound failure under `NOISY + LOW_END + REGIONAL` conditions.

*(Note: These are fictional demonstration vendors designed to illustrate varied deployment profiles.)*

### Running the Demo via API

1. **Inspect Scenario Metadata:**
   ```http
   GET /api/v1/demo/scenario
   ```
2. **Execute Demonstration Pipeline:**
   ```http
   POST /api/v1/demo/evaluate
   ```

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Operational health and service identity verification |
| `GET` | `/api/v1/demo/scenario` | Retrieves public metadata and configuration for the canonical demo |
| `POST` | `/api/v1/demo/evaluate` | Runs the canonical demonstration scenario and returns the complete frontend contract |
| `POST` | `/api/v1/evaluate` | Submits a custom problem statement and executes the 14-stage evaluation pipeline |
| `GET` | `/api/v1/evaluations/{evaluation_id}` | Retrieves full stored evaluation record by evaluation ID |
| `GET` | `/api/v1/evaluations/{evaluation_id}/vendors` | Returns frontend-friendly vendor scorecards, metrics, and recommendations |
| `GET` | `/api/v1/evaluations/{evaluation_id}/diagnostics` | Returns forensic Diagnostic Intelligence explaining multi-factor failure interactions |
| `GET` | `/api/v1/evaluations/{evaluation_id}/failure-map` | Returns sanitized Failure Cartography mapping operational hotspots and severity levels |
| `GET` | `/api/v1/evaluations/{evaluation_id}/decision` | Returns deterministic procurement gate results (strictly read-only) |
| `POST` | `/api/v1/evaluations/{evaluation_id}/authorization` | Records human authorization decision with maker-checker and override governance |

---

## Key Governance Principles

1. **Outcome Contract Locking:** Outcome contracts and KPI thresholds are locked and hashed prior to vendor evaluation.
2. **Pilot Twin Evidence Levels:** Pilot Twin parameters carry verifiable evidence levels (`OBSERVED`, `DECLARED`, `UNVERIFIED`).
3. **Private Matrix Protection:** Test methodology is public (24 strata), but private seeds and test instances are never exposed.
4. **Self-Verifying Evaluator:** Evaluators must pass the Golden Reference Suite before evaluating any vendor artifact.
5. **Cryptographic Artifact Integrity:** Vendor build artifacts are frozen via SHA-256 hashes to guarantee provenance.
6. **Traceable Evidence Records:** Evidence records carry cryptographic bindings and explicit validity expiration windows.
7. **Failure Cartography:** Maps multi-stratum performance to pinpoint exact conditions under which solutions break.
8. **Evidence Confidence Gating:** Multi-factor weighted confidence calculation acts as a mandatory procurement gate.
9. **Deterministic Decision Logic:** Procurement eligibility is evaluated through strict, deterministic rule gates with zero LLM bias.
10. **Advisory Diagnostic Intelligence:** Forensic AI diagnostic reports provide qualitative explanation but cannot alter metrics or decisions.
11. **Mandatory Human Authorization:** AI never executes procurement or releases funds; final authorization requires a human officer.
12. **Maker-Checker Override Review:** Overriding an AI rejection requires dual-officer concurrence or higher-authority escalation.
13. **Re-Gated Regional Scale-Up:** Passing District A does not grant automatic scaling to District B; scaling is re-evaluated against the target district's Pilot Twin.
14. **Zero Sensitive Leaks:** Private parameters, raw seeds, model weights, and internal secrets are strictly excluded from API outputs.

---

## Environment & Offline Resilience

Axiom AI functions completely offline with zero external network or database requirements.

- If `OPENAI_API_KEY` is not provided in `.env`, the system automatically activates `DETERMINISTIC_FALLBACK` for contract extraction and forensic diagnostics.
- To enable optional live LLM diagnostic reasoning:
  ```bash
  cp .env.example .env
  # Add your OPENAI_API_KEY in .env
  ```
