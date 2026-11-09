# GRAVISM — Interactive Computational Simulation of Gravitational Lensing Using Python

> *"Exploring the Universe Through Computational Physics."*

An interactive computational physics platform developed with **Python (NumPy & SciPy)**, **Three.js + Custom GLSL Shaders (360° WebGL)**, and **verified NASA / Hubble / JWST / Event Horizon Telescope datasets**—styled in GRAVISM's deep-space minimalist glassmorphic aesthetic.

## 🚀 Live Localhost Server
- **Open Application:** [http://localhost:8000/](http://localhost:8000/)
- **Launcher Script:** [serve.bat](file:///c:/Users/Jaek/GRAVISM/serve.bat) (`python server.py 8000`)
- **Complete Labeled File & Data Guide:** [DATA_GUIDE.md](file:///c:/Users/Jaek/GRAVISM/DATA_GUIDE.md)

## 🔬 Key Capabilities
1. **Python Relativistic Lensing Kernel (`python_engine/`)**: Solves Point-Mass (Schwarzschild), Singular Isothermal Sphere (SIS), and Quadrupole Tidal Shear (4-image Einstein Cross) models, validated against exact SciPy elliptic geodesic quadrature.
2. **360° Interactive 3D WebGL + GLSL Spacetime Lab (`js/scene3d.js`)**: Full 360° spherical orbit, custom GLSL Flamm's paraboloid spacetime curvature shader, Doppler-beamed accretion halo, and real-time 3D curved photon geodesics.
3. **Interactive Sky-Plane & NumPy Magnification Maps (`js/plots2d.js`)**: Real-time inverse ray-traced Einstein rings/arcs with click-and-drag source positioning, `log10|μ|` Jacobian heatmaps, critical curves, caustics, and analytical validation plots.
4. **Verified NASA / HST / JWST / EHT Datasets (`python_engine/nasa_catalog.py`)**: 1-click loading for *LRG 3-757 (Cosmic Horseshoe)*, *Q2237+0305 (Einstein Cross)*, *SMACS J0723.3-7327 (Webb Deep Field)*, *SPT0418-47 (JWST Molten Ring)*, *SDSS J1004+4112*, and *M87\**.
