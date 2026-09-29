# GLOF-SAFE Backend

AI-Driven Geospatial Intelligence for GLOF Prediction, Cascading Hazard
Detection, Transboundary Flood Monitoring & Resilient Disaster Response.

This is the FastAPI backend for the GLOF-SAFE prototype (Aavishkar demo).

## Project layout

```
project-root/
├── ml/                     # risk scoring + anomaly detection models
│   ├── risk_model.py
│   └── anomaly_detector.py
└── backend/                # this folder - the API
    ├── main.py              # app entrypoint, registers all routers
    ├── data/
    │   ├── lakes/glacial_lake.geojson
    │   └── dem/*.hgt, *.tif
    ├── requirements.txt
    └── ... (feature modules + *_api.py routers)
```

`main.py` expects the `ml/` folder to sit one level above this backend
folder (i.e. as a sibling), because of this line:

```python
sys.path.append(str(Path(__file__).resolve().parent.parent / "ml"))
```

So keep the two folders side by side, exactly as shown above.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open:
- http://127.0.0.1:8000/docs — interactive Swagger UI for every endpoint
- http://127.0.0.1:8000/health — quick liveness check

The SQLite database (`glofsafe.db`) is already seeded with real glacial
lake records, so `/lakes`, `/risk-summary`, `/dashboard/{lake_id}`, etc.
work immediately with no extra setup.

## What's live data vs. simulated

To be transparent for the demo/judging:

- **Real, working today:** lake CRUD, DEM-based inundation modelling
  (`/dem/inundation`) using bundled elevation tiles in `data/dem/`,
  population-impact estimation, evacuation routing, alerting, and the
  rule-weighted risk model in `ml/risk_model.py`.
- **Real but network-dependent:** the `/satellite/*` endpoints call the
  Copernicus/Planetary Computer STAC APIs, and `/population/{lake_id}`
  calls the WorldPop API. Both need outbound internet access at demo
  time. If the network call fails (no wifi, rate limit, API outage),
  these endpoints degrade gracefully:
  - `/satellite/*` returns `"status": "SATELLITE_UNAVAILABLE"` with an
    error message instead of crashing.
  - `/population/{lake_id}` falls back to a rough area-based population
    estimate and reports `"population_source": "ESTIMATED_FALLBACK"`.
- **Simulated for the demo:** `/advanced-hazard/*`, `/risk-summary`'s
  per-lake sensor snapshot, `/sensors`, and `/simulate` generate
  plausible values with `random.*` rather than reading real river
  gauges/sensors - clearly labelled `"data_type": "SIMULATED_..."` in
  their responses so it's obvious in a demo/judging context.

## Notes

- `main.backup.py`, `main_backup_phase3.py`, `satellite_area_backup.py`,
  etc. are old snapshots kept during development. They aren't imported
  by anything and can be safely deleted before submission if you want a
  cleaner repo.
- The `venv/` folder that shipped in the original zip was a Windows
  virtual environment and shouldn't be committed - regenerate it
  locally with the Setup steps above instead.

## Gap-analysis modules (Module 1-9)

Nine additional modules were added to close the gaps identified against
the full "AI-Driven Geospatial Intelligence" brief. Each is a genuinely
working, tested endpoint - but where the brief calls for a trained deep
learning model (cGAN, PINN, GNN, Transformer) that would need labelled
training data and GPU time this project doesn't have, a real classical
algorithm (empirical physics formulas, DEM terrain analysis, Bayesian
inference, statistical regression, rule-based NLP) stands in instead.
Every module's file has an "HONEST SCOPE NOTE" docstring explaining
exactly what's real vs. a lightweight substitute, and a `future_work`
field in its API response pointing at the real upgrade path.

| Module | Endpoints | What it actually does |
|---|---|---|
| 1 - Data & Bathymetry | `/module1/bathymetry/{lake_id}`, `/module1/cloud-composite/{lake_id}` | Empirical area-volume lake depth/volume estimate (DEM-corrected); cloud-ranked multi-temporal scene search |
| 2 - Precursor & Cascading Hazard | `/module2/slope-instability/{lake_id}`, `/module2/debris-flow-runout` | DEM slope/roughness terrain susceptibility; empirical volume-based debris-flow runout distance |
| 3 - Transboundary Tracker | `/module3/discharge`, `/module3/upstream-release-check` | Manning's-equation river discharge from real DEM channel slope; z-score spike detection for sudden upstream releases |
| 4 - Zero-Latency Decision Pipeline | `/module4/verify-alarm`, `/module4/cap-alert/{lake_id}` | Real Bayesian (Naive Bayes) multi-sensor alarm fusion; genuine OASIS CAP v1.2 XML alert generation |
| 5 - Crowd-Sourced & Last-Mile | `/module5/crowd-report`, `/module5/crowd-reports`, `/module5/siren-trigger` | Rule-based NLP hazard-report classifier with GPS-tagged storage; satellite/LoRa siren dispatch interface (hardware bridge simulated) |
| 6 - Structural Vulnerability | `/module6/analyze-default/{lake_id}`, `/module6/analyze` | Graph-based flood-arrival propagation + real hydrodynamic drag-force structural failure scoring |
| 7 - Silt & Turbidity Forecaster | `/module7/turbidity`, `/module7/sediment-lead-time` | NDTI turbidity-index scene lookup (real Sentinel-2 catalogue); kinematic sediment-plume lead-time calc |
| 8 - Damage Mapping & Route AI | `/module8/damage-proxy-map`, `/module8/route-replan` | Optical pre/post change-detection Damage Proxy Map; real-time OSRM-based constrained rerouting around blocked points |
| 9 - Climate Projection | `/module9/project-growth-default`, `/module9/project-growth` | Polynomial regression time-series extrapolation of lake growth to a target year, with confidence bands |

Modules 1, 7, and 8's satellite-dependent endpoints, and Module 8's
route-replan, need outbound internet to the Copernicus/Planetary
Computer STAC APIs and the OSRM routing API respectively - they degrade
gracefully (`"status": "SATELLITE_UNAVAILABLE"` / `"ROUTING_UNAVAILABLE"`)
rather than crashing if that network isn't available.
