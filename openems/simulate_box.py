"""simulate_box.py — skeleton for openEMS PEC box simulation

This script will attempt to use `rfems` or `pyopenems` if installed; otherwise it
will run a safe placeholder that writes a JSON report. It supports a minimal
CLI so CI can assert against placeholder output when real FDTD libraries are
not present.
"""

import os
import json
import importlib
import argparse
from datetime import datetime

TARGET_FREQS = [2.4e9, 5e9]

USE_REAL = False
real_lib = None

# Try to import an OpenEMS binding (if available in the environment)
for libname in ("rfems", "pyopenems", "openems"):
    try:
        real_lib = importlib.import_module(libname)
        USE_REAL = True
        print(f"Info: found simulation lib: {libname}")
        break
    except Exception:
        pass


def generate_frequency_sweep(center_hz, width_hz=100e6, points=101):
    """Return a list of frequencies (Hz) across center +/- width."""
    try:
        import numpy as _np
        freqs = _np.linspace(center_hz - width_hz, center_hz + width_hz, points)
        return freqs.tolist()
    except Exception:
        # fallback to pure Python
        start = center_hz - width_hz
        step = (2 * width_hz) / (points - 1)
        return [start + i * step for i in range(points)]


def compute_placeholder_attenuation(freqs_hz, center_hz, preset="generic"):
    """Compute a simple frequency-dependent placeholder attenuation (dB).

    This is a toy model (Gaussian-shaped notch) for demonstration and testing.
    """
    try:
        import math as _math
    except Exception:
        from math import exp as _math_exp

    # Preset-driven params (attenuation depth in dB, width factor)
    PRESET_PARAMS = {
        "xr-headset": {"depth": 60.0, "width_hz": 100e6},
        "xr-headset-5": {"depth": 50.0, "width_hz": 200e6},
        "ble": {"depth": 30.0, "width_hz": 5e6},
        "generic": {"depth": 40.0, "width_hz": 100e6},
    }
    params = PRESET_PARAMS.get(preset, PRESET_PARAMS["generic"])
    depth = params["depth"]
    width = params["width_hz"]

    sweep = []
    for f in freqs_hz:
        # Gaussian-ish attenuation centered at center_hz
        x = (f - center_hz) / width
        att = -(10.0 + depth * (1.0 / (1.0 + x * x)))  # negative dB (attenuation)
        sweep.append(float(att))
    return sweep


def simulate_placeholder(freq_hz, output_path="openems_results.json", preset="generic", box_dims=(0.3, 0.3, 0.2)):
    # create a sweep around the requested frequency
    center_hz = freq_hz
    freqs = generate_frequency_sweep(center_hz)
    atten = compute_placeholder_attenuation(freqs, center_hz, preset=preset)

    # prepare sweep data (MHz, dB)
    sweep_data = [{
        "freq_mhz": float(f) / 1e6,
        "attenuation_db": a
    } for f, a in zip(freqs, atten)]

    out = {
        "mode": "placeholder",
        "frequency_ghz": center_hz / 1e9,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "note": f"Placeholder run (preset={preset}) — replace with real openEMS simulation on provisioned runners",
        "box_dims_m": box_dims,
        "sweep": sweep_data
    }

    # write JSON
    with open(output_path, "w") as f:
        json.dump(out, f, indent=2)

    # write CSV
    csv_path = os.path.splitext(output_path)[0] + ".csv"
    with open(csv_path, "w") as cf:
        cf.write("freq_mhz,attenuation_db\n")
        for row in sweep_data:
            cf.write(f"{row['freq_mhz']},{row['attenuation_db']}\n")

    print(f"Wrote placeholder simulation JSON: {output_path}")
    print(f"Wrote sweep CSV: {csv_path}")

    # attempt to plot if matplotlib available
    try:
        import matplotlib.pyplot as plt
        freqs_mhz = [r["freq_mhz"] for r in sweep_data]
        atts = [r["attenuation_db"] for r in sweep_data]
        plt.figure(figsize=(6,3))
        plt.plot(freqs_mhz, atts, '-r')
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Attenuation (dB)')
        plt.title(f'Placeholder attenuation (preset={preset}, center={center_hz/1e9} GHz)')
        plt.grid(True)
        png_path = os.path.splitext(output_path)[0] + f"_attenuation_{preset.replace(' ','_')}_{int(center_hz/1e6)}MHz.png"
        plt.tight_layout()
        plt.savefig(png_path)
        plt.close()
        print(f"Wrote attenuation plot: {png_path}")
    except Exception:
        print("matplotlib not available; skipping plot generation")


def simulate_with_real_lib(freq_hz, output_path="openems_results.json", preset="generic", box_dims=(0.3, 0.3, 0.2)):
    # This is a minimal example scaffold. Implementation depends on the
    # actual Python binding API. Users should replace with the correct calls.
    print(f"Running a real simulation at {freq_hz/1e9} GHz using {real_lib.__name__} (example)")

    try:
        sim = real_lib.Simulation()
        sim.set_box(box_dims)
        sim.set_frequency(freq_hz)
        results = sim.run()
        s11_db = results.get("s11_db", None)
    except Exception as e:
        print("Real library invocation failed (placeholder):", e)
        s11_db = None

    out = {
        "mode": f"real ({real_lib.__name__})",
        "frequency_ghz": freq_hz / 1e9,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "s11_db": s11_db
    }
    with open(output_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote real-sim report: {output_path}")


def parse_args():
    p = argparse.ArgumentParser(description="openEMS box simulation (placeholder-capable)")
    p.add_argument("--frequency-ghz", type=float, help="Frequency (GHz) to simulate", default=None)
    p.add_argument("--output", type=str, help="Output JSON file", default="openems_results.json")
    p.add_argument("--preset", type=str, help="Preset (xr-headset, xr-headset-5, ble, generic)", default="generic")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    preset = args.preset or "generic"

    # mapping presets to default center freqs if frequency not supplied
    PRESET_CENTER = {
        "xr-headset": 2.4e9,
        "xr-headset-5": 5.0e9,
        "ble": 2.402e9,
    }

    if args.device:
        # device-driven generation: map device to bands and run for each
        device = args.device.lower()
        devices = {
            "oculus-quest-2": {"bands": [2.4e9, 5.0e9], "preset": "xr-headset"},
            "pico-neo-3": {"bands": [2.4e9, 5.0e9], "preset": "xr-headset"},
            "meta-quest-pro": {"bands": [2.4e9, 5.0e9], "preset": "xr-headset-5"},
            "htc-vive": {"bands": [5.0e9], "preset": "xr-headset-5"},
            "ble-headset": {"bands": [2.402e9], "preset": "ble"}
        }
        spec = devices.get(device)
        if not spec:
            print(f"Unknown device '{device}'. Known devices: {', '.join(devices.keys())}")
            raise SystemExit(2)
        out_files = []
        for b in spec["bands"]:
            fname = f"{device}_{int(b/1e6)}MHz_results.json"
            csvname = f"{device}_{int(b/1e6)}MHz_results.csv"
            if not USE_REAL:
                simulate_placeholder(b, output_path=fname, preset=spec["preset"])
            else:
                simulate_with_real_lib(b, output_path=fname, preset=spec["preset"])
            # also ensure CSV exists at predictable name
            # simulate_placeholder writes JSON and CSV with same base; move/rename if needed
            base = os.path.splitext(fname)[0]
            if os.path.exists(base + ".csv"):
                os.rename(base + ".csv", csvname)
            elif os.path.exists(args.output.replace('.json', '.csv')):
                os.rename(args.output.replace('.json', '.csv'), csvname)
            out_files.append((fname, csvname))
        print("Generated device reports:")
        for j,c in out_files:
            print(" -", j, c)
    else:
        if args.frequency_ghz is not None:
            freq_hz = args.frequency_ghz * 1e9
        else:
            freq_hz = PRESET_CENTER.get(preset, None)

        if freq_hz is None:
            # default: run both target freqs
            for f in TARGET_FREQS:
                if not USE_REAL:
                    simulate_placeholder(f, output_path=f"simulation_{int(f/1e6)}MHz_report.json", preset=preset)
                else:
                    simulate_with_real_lib(f, output_path=f"simulation_{int(f/1e6)}MHz_report.json", preset=preset)
        else:
            if not USE_REAL:
                simulate_placeholder(freq_hz, output_path=args.output, preset=preset)
            else:
                simulate_with_real_lib(freq_hz, output_path=args.output, preset=preset)

    print("Done.")