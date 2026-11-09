"""
==============================================================================
[LABEL: PYTHON COMPUTATIONAL SERVER & API] — server.py
==============================================================================
Threaded HTTP & Scientific Computing Server for GRAVISM Gravitational Lensing.
Serves static frontend assets at http://localhost:8000/ and exposes live
Python NumPy/SciPy computational endpoints:
  - GET  /api/status             -> Python runtime, NumPy/SciPy & CODATA constants
  - GET  /api/datasets           -> Verified NASA / HST / JWST / EHT lens catalog
  - GET  /api/history            -> Logged computational simulation runs
  - POST /api/simulate           -> Run gravitational lens solver & validation
  - POST /api/magnification-map  -> Generate 2D NumPy Jacobian magnification map
  - POST /api/export/csv         -> Export numerical results & profiles as CSV
"""

import csv
import io
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import numpy as np
import scipy

from python_engine.constants import get_constants_metadata
from python_engine.lens_models import compute_lens_simulation, compute_magnification_map
from python_engine.nasa_catalog import build_nasa_catalog
from python_engine.validator import check_possible_lensing, run_accuracy_suite
from python_engine.video_pipeline import inspect_mp4_container

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_START_TIME = time.time()
NASA_CATALOG_CACHE = build_nasa_catalog()
SIMULATION_HISTORY: list[dict] = []
MAX_HISTORY = 40


class GravismRequestHandler(SimpleHTTPRequestHandler):
    """Serves frontend assets and handles Python computational physics API requests."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def log_message(self, fmt, *args):
        # Clean concise server log
        sys.stdout.write(f"[GRAVISM-PY] {self.address_string()} - {fmt % args}\n")
        sys.stdout.flush()

    def _send_json(self, data: dict | list, status: int = 200) -> None:
        raw = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _serve_video_range(self, file_path: str) -> None:
        """Serves MP4 video files with full RFC 7233 HTTP 206 Partial Content byte-range support."""
        file_size = os.path.getsize(file_path)
        range_header = self.headers.get("Range")

        start = 0
        end = file_size - 1
        status = 200

        if range_header and range_header.startswith("bytes="):
            status = 206
            parts = range_header.replace("bytes=", "").split("-", 1)
            if parts[0].strip():
                start = int(parts[0].strip())
            if len(parts) > 1 and parts[1].strip():
                end = min(file_size - 1, int(parts[1].strip()))

        start = max(0, min(start, file_size - 1))
        end = max(start, min(end, file_size - 1))
        chunk_len = (end - start) + 1

        try:
            self.send_response(status)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(chunk_len))
            if status == 206:
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = chunk_len
                while remaining > 0:
                    buf = f.read(min(65536, remaining))
                    if not buf:
                        break
                    self.wfile.write(buf)
                    remaining -= len(buf)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self._send_json({
                "online": True,
                "python_version": sys.version.split()[0],
                "numpy_version": np.__version__,
                "scipy_version": scipy.__version__,
                "uptime_sec": round(time.time() - SERVER_START_TIME, 1),
                "constants": get_constants_metadata(),
                "dataset_count": len(NASA_CATALOG_CACHE)
            })
            return

        if parsed.path == "/api/datasets":
            self._send_json({
                "datasets": NASA_CATALOG_CACHE,
                "constants": get_constants_metadata()
            })
            return

        if parsed.path == "/api/history":
            self._send_json({"history": list(reversed(SIMULATION_HISTORY))})
            return

        if parsed.path == "/api/accuracy-suite":
            try:
                report = run_accuracy_suite()
                self._send_json(report)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return

        if parsed.path == "/api/video-telemetry":
            self._send_json(inspect_mp4_container())
            return

        if parsed.path.endswith(".mp4"):
            rel = parsed.path.lstrip("/")
            video_path = os.path.normpath(os.path.join(ROOT_DIR, rel))
            if video_path.startswith(ROOT_DIR) and os.path.isfile(video_path):
                self._serve_video_range(video_path)
                return

        if parsed.path in ("/favicon.ico", "/favicon.svg"):
            fav_path = os.path.join(ROOT_DIR, "favicon.svg")
            if os.path.exists(fav_path):
                with open(fav_path, "rb") as f:
                    raw = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/svg+xml")
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(raw)
                return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            payload = self._read_json_body()
        except Exception as exc:
            self._send_json({"error": f"Invalid JSON payload: {exc}"}, status=400)
            return

        if parsed.path == "/api/simulate":
            try:
                sim = compute_lens_simulation(payload)
                if payload.get("record_history", False):
                    entry = {
                        "run_id": len(SIMULATION_HISTORY) + 1,
                        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
                        "preset_name": payload.get("preset_name", "Custom Configuration"),
                        "lens_model": sim["model_metadata"]["name"],
                        "mass_solar": sim["inputs"]["mass_solar"],
                        "d_lens_mpc": sim["inputs"]["d_lens_mpc"],
                        "d_source_mpc": sim["inputs"]["d_source_mpc"],
                        "beta_arcsec": sim["inputs"]["beta_mag_arcsec"],
                        "theta_e_arcsec": sim["results"]["einstein_radius_arcsec"],
                        "total_magnification": sim["results"]["total_magnification"],
                        "image_count": sim["results"]["image_count"],
                        "compute_time_ms": sim["compute_time_ms"]
                    }
                    SIMULATION_HISTORY.append(entry)
                    if len(SIMULATION_HISTORY) > MAX_HISTORY:
                        SIMULATION_HISTORY.pop(0)
                sim["history_count"] = len(SIMULATION_HISTORY)
                self._send_json(sim)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return

        if parsed.path == "/api/magnification-map":
            try:
                mmap = compute_magnification_map(payload)
                self._send_json(mmap)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return

        if parsed.path == "/api/check-possible":
            try:
                verdict = check_possible_lensing(payload)
                self._send_json(verdict)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return

        if parsed.path == "/api/export/csv":
            try:
                sim = compute_lens_simulation(payload)
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerow(["# GRAVISM — Python Gravitational Lensing Computational Report"])
                writer.writerow(["# Engine", sim["engine"]])
                writer.writerow(["# Model", sim["model_metadata"]["name"]])
                writer.writerow([])
                writer.writerow(["PARAMETER / QUANTITY", "VALUE", "UNIT"])
                writer.writerow(["Lens Mass (M)", sim["inputs"]["mass_solar"], "M_sun"])
                writer.writerow(["Lens Distance (D_L)", sim["inputs"]["d_lens_mpc"], "Mpc"])
                writer.writerow(["Source Distance (D_S)", sim["inputs"]["d_source_mpc"], "Mpc"])
                writer.writerow(["Lens-Source Distance (D_LS)", sim["inputs"]["d_ls_mpc"], "Mpc"])
                writer.writerow(["Source Offset |beta|", sim["inputs"]["beta_mag_arcsec"], "arcsec"])
                writer.writerow(["Einstein Radius (theta_E)", sim["results"]["einstein_radius_arcsec"], "arcsec"])
                writer.writerow(["Physical Einstein Radius (R_E)", sim["results"]["einstein_radius_kpc"], "kpc"])
                writer.writerow(["Schwarzschild Radius (r_s)", f"{sim['results']['schwarzschild_radius_m']:.6e}", "m"])
                writer.writerow(["GR Deflection Angle (alpha_GR)", sim["results"]["deflection_gr_arcsec"], "arcsec"])
                writer.writerow(["Exact Geodesic Deflection", sim["results"]["deflection_exact_arcsec"], "arcsec"])
                writer.writerow(["Total Magnification (mu_tot)", sim["results"]["total_magnification"], "dimensionless"])
                writer.writerow(["Shapiro + Geometric Time Delay", sim["results"]["time_delay_days"], "days"])
                writer.writerow([])
                writer.writerow(["LENSED IMAGE", "THETA_X (arcsec)", "THETA_Y (arcsec)", "MAGNIFICATION (mu)", "PARITY"])
                for im in sim["images"]:
                    writer.writerow([
                        im["label"],
                        im["theta_x_arcsec"],
                        im["theta_y_arcsec"],
                        im["magnification"],
                        im["parity"]
                    ])
                raw_csv = buf.getvalue().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="gravism_lensing_report.csv"')
                self.send_header("Content-Length", str(len(raw_csv)))
                self.end_headers()
                self.wfile.write(raw_csv)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json({"error": "Endpoint not found"}, status=404)


class DualStackThreadingHTTPServer(ThreadingHTTPServer):
    """Supports both IPv6 (::1 localhost on Windows) and IPv4 (127.0.0.1) simultaneously."""

    address_family = socket.AF_INET6

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (AttributeError, OSError):
            pass
        return super().server_bind()


def run_server(port: int = 8000) -> None:
    try:
        server = DualStackThreadingHTTPServer(("::", port), GravismRequestHandler)
    except OSError:
        server = ThreadingHTTPServer(("0.0.0.0", port), GravismRequestHandler)
    print(f"GRAVISM Python Computational Server (Dual-Stack) listening on http://localhost:{port}/")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port_arg)
