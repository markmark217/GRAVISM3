# 🛰️ GRAVISM — Labeled File Architecture & NASA Data Guide

**Project:** *Development of an Interactive Computational Simulation of Gravitational Lensing Using Python for Physics Education*  
**Tagline:** *"Exploring the Universe Through Computational Physics."*

Every file in this project is cleanly separated, arranged by layer, and labeled so you can immediately locate the Python computational physics code, NASA astronomical datasets, 360° 3D WebGL/GLSL shaders, or UI styles.

---

## 📁 Arranged & Labeled File Directory

```text
GRAVISM/
├── index.html                    # [PAGE: HOME] Hero, constants strip, directory of the 6 workspaces
├── pages/                        # 📄 ONE FILE PER SECTION (each opens as its own page)
│   ├── spacetime.html            # [PAGE 01] 360° WebGL/GLSL spacetime lab
│   ├── simulator.html            # [PAGE 02] Parameter controls, sky-plane ray-tracer, telemetry cards
│   ├── analysis.html             # [PAGE 03] Magnification map, validation charts, model limitations
│   ├── tester.html               # [PAGE 04 · NEW] Accuracy Tester & Possible Checker (SciPy benchmarks)
│   ├── catalog.html              # [PAGE 05] NASA / HST / JWST / EHT datasets (8 systems) + experiment log
│   └── equations.html            # [PAGE 06] Governing equations, lens models, constants table
├── server.py                     # [LABEL: PYTHON COMPUTE SERVER] Threaded HTTP + NumPy/SciPy REST API on port 8000
├── serve.bat                     # [LABEL: 1-CLICK LAUNCHER] Starts `python server.py 8000`
├── DATA_GUIDE.md                 # [LABEL: FILE & DATA INDEX] This file
├── GRAVISM.md                    # [LABEL: PROJECT SUMMARY]
│
├── assets/
│   └── blackhole_hero.mp4        # [LABEL: HERO BLACK HOLE VIDEO] 854×480 (16:9) relativistic black hole video stream
│
├── python_engine/                # 🐍 PYTHON COMPUTATIONAL PHYSICS KERNEL
│   ├── constants.py              # [LABEL: PHYSICAL CONSTANTS] CODATA 2022 SI & Planck 2018 ΛCDM distances
│   ├── lens_models.py            # [LABEL: NUMERICAL SOLVER] Point-Mass, SIS, Quadrupole Shear + magnification maps
│   ├── validator.py              # [LABEL: ACCURACY TESTER & CHECKER] 6-stage SciPy benchmark suite + possible checker
│   ├── video_pipeline.py         # [LABEL: VIDEO TELEMETRY & LOOP SCHEDULE] MP4 ISO-BMFF parser & Hermite crossfade LUT
│   └── nasa_catalog.py           # [LABEL: NASA / HST / JWST / EHT DATA] 8 verified lens systems & formal citations
│
├── css/
│   └── styles.css                # [LABEL: STYLES] Dark theme, LIGHT-MODE overrides, page transitions
│
└── js/
    ├── blackhole-engine.js       # [LABEL: WEBGL GLSL VIDEO LOOP ENGINE] Dual-deck ping-pong video crossfade + GLSL optical shader
    ├── theme.js                  # [LABEL: THEME BOOTSTRAP] Applies saved dark/light mode before first paint
    ├── layout.js                 # [LABEL: SHARED NAV / FOOTER / THEME TOGGLE] Edit nav links in ONE place (PAGES array)
    ├── tailwind-config.js        # [LABEL: THEME TOKENS] Colors, fonts, radii, glow shadows
    ├── data.js                   # [LABEL: FRONTEND DATA] Equations, model notes, NASA catalog mirror (8 systems)
    ├── physics-client.js         # [LABEL: PYTHON API BRIDGE] Calls `/api/*` + 60fps real-time mirror + validator client
    ├── scene3d.js                # [LABEL: 360° 3D ENGINE] Three.js + GLSL shaders (spacetime page only)
    ├── plots2d.js                # [LABEL: 2D PLOTS] Sky plane, heatmap, validation curves
    └── main.js                   # [LABEL: PAGE CONTROLLER] Shared by all pages; features activate only where their elements exist
```

## 🌗 Dark / White Mode
- Toggle button sits in the top bar of every page; the choice is saved in `localStorage` (`gravism-theme`).
- Light-mode colors live at the bottom of `css/styles.css` under **LIGHT (WHITE) MODE**.
- Scientific viewports (3D stage, sky plane, heatmap, charts) carry the class `keep-dark` and stay dark in both themes.

## 🔗 State shared between pages
The selected NASA system and every slider value are stored in `localStorage` (`gravism-sim-state`), so loading a system on the Catalog page opens the 3D lab or simulator already configured.

## ➕ Add a new page
1. Copy any file in `pages/` and change `data-page`.
2. Add `{ id, label, href }` to the `PAGES` array in `js/layout.js` — the nav, mobile menu and footer update everywhere.


---

## 📍 Where Each Type of Data Lives

### 1. Verified NASA / Hubble / JWST / EHT Astronomical Data
* **Python Source (Authoritative):** [`python_engine/nasa_catalog.py`](file:///c:/Users/Jaek/GRAVISM/python_engine/nasa_catalog.py)
* **Frontend Fallback Mirror:** [`js/data.js`](file:///c:/Users/Jaek/GRAVISM/js/data.js) → `GRAVISM_DATA.nasaDatasets`
* **Included Peer-Reviewed Observations (8 Systems):**
  1. **LRG 3-757 (Cosmic Horseshoe)** — NASA/ESA Hubble WFC3 (`z_L = 0.4457`, `z_S = 2.379`, `θ_E = 5.10"`)
  2. **Q2237+0305 (Einstein Cross)** — NASA Hubble FOC/WFC3 & JWST (`z_L = 0.0395`, `z_S = 1.695`, `θ_E = 0.90"`, 4-image quasar)
  3. **SMACS J0723.3-7327 (Webb's First Deep Field)** — NASA JWST NIRCam (`z_L = 0.390`, `z_S = 1.95`, `θ_E = 16.50"`)
  4. **SPT0418-47 (JWST Molten Einstein Ring)** — NASA JWST NIRCam/MIRI & ALMA (`z_L = 0.263`, `z_S = 4.225`, `θ_E = 1.22"`)
  5. **SDSS J1004+4112 (Cluster Quasar Quintet)** — NASA Hubble ACS & Chandra (`z_L = 0.680`, `z_S = 1.734`, `θ_E = 7.10"`)
  6. **M87\* Supermassive Black Hole** — Event Horizon Telescope & NASA Chandra (`M = 6.5 × 10⁹ M_☉`, `D_L = 16.8 Mpc`)
  7. **Sagittarius A\* (Milky Way SMBH)** — EHT 2022 & NASA Chandra (`M = 4.154 × 10⁶ M_☉`, `D_L = 8.178 kpc`, `θ_E = 1.45"`)
  8. **B1938+666 (JWST / HST Dwarf Ring)** — NASA/ESA Hubble & JWST NIRCam (`z_L = 0.881`, `z_S = 2.059`, `θ_E = 0.46"`, dark matter dwarf satellite discovery)

### 2. Fundamental Physical Constants (SI & Cosmological)
* **Python Source:** [`python_engine/constants.py`](file:///c:/Users/Jaek/GRAVISM/python_engine/constants.py)
  * `G_SI = 6.67430e-11` m³ kg⁻¹ s⁻² (CODATA 2022)
  * `C_SI = 299792458.0` m/s (SI Exact)
  * `M_SUN_KG = 1.98847e30` kg (IAU 2015)
  * `H0_KM_S_MPC = 67.4`, `OMEGA_M = 0.315` (Planck 2018 Flat ΛCDM)

### 3. Relativistic Equations & Educational Explanations
* **Location:** [`js/data.js`](file:///c:/Users/Jaek/GRAVISM/js/data.js) → `GRAVISM_DATA.equations` and `GRAVISM_DATA.lensModels`
* Rendered automatically using **KaTeX** scientific typography.

### 4. 360° 3D Shaders & Camera Presets
* **Location:** [`js/scene3d.js`](file:///c:/Users/Jaek/GRAVISM/js/scene3d.js)
  * `spacetimeVertexShader` / `spacetimeFragmentShader`: Custom **GLSL** shader computing Flamm's paraboloid gravitational well displacement and Einstein ring metric highlight.
  * `accretionVertexShader` / `accretionFragmentShader`: Custom **GLSL** shader simulating Keplerian differential swirl and relativistic Doppler beaming.
  * `photonSphereVertexShader` / `photonSphereFragmentShader`: Custom **GLSL** Fresnel photon-ring glow around the black hole event horizon.

---

## ➕ How to Add a New Astronomical System Later

Open [`python_engine/nasa_catalog.py`](file:///c:/Users/Jaek/GRAVISM/python_engine/nasa_catalog.py) and append a dictionary to `raw_systems`:

```python
{
    "id": "b1938_666",
    "name": "JVAS B1938+666 (Infrared Einstein Ring)",
    "category": "Complete Galaxy Ring",
    "mission": "NASA Hubble Space Telescope (NICMOS)",
    "lens_model": "point_mass",      # "point_mass" | "sis" | "elliptical_shear"
    "z_lens": 0.881,                 # Python automatically computes Planck-2018 D_L, D_S, D_LS!
    "z_source": 2.059,
    "mass_solar": 2.4e11,
    "default_beta_arcsec": 0.01,
    "default_shear": 0.02,
    "observed_theta_e_arcsec": 0.45,
    "uncertainty_note": "±0.02 arcsec (HST NICMOS)",
    "description": "Near-infrared complete Einstein ring imaged by Hubble NICMOS.",
    "citation": "King et al. (1998), MNRAS 295, L41; NASA HST"
}
```
Restart `serve.bat` and refresh **[http://localhost:8000/](http://localhost:8000/)** — the new card, cosmological distances, 3D geometry, and Python solver bindings appear automatically!
