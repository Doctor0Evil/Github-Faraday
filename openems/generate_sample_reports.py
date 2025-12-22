"""Generate sample attenuation reports for a list of XR devices.

This script imports `simulate_placeholder` from `simulate_box.py` and runs
placeholder simulations for a set of devices, writing JSON/CSV output into
`openems/samples/` and producing a combined summary CSV.
"""
import os
import csv
from datetime import datetime

from simulate_box import simulate_placeholder

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'samples')
os.makedirs(SAMPLE_DIR, exist_ok=True)

DEVICES = {
    'oculus-quest-2': {'bands': [2.4e9, 5.0e9], 'preset': 'xr-headset'},
    'pico-neo-3': {'bands': [2.4e9, 5.0e9], 'preset': 'xr-headset'},
    'meta-quest-pro': {'bands': [2.4e9, 5.0e9], 'preset': 'xr-headset-5'},
    'htc-vive': {'bands': [5.0e9], 'preset': 'xr-headset-5'},
    'ble-headset': {'bands': [2.402e9], 'preset': 'ble'}
}

summary_rows = []

for dev, spec in DEVICES.items():
    for b in spec['bands']:
        base = f"{dev}_{int(b/1e6)}MHz"
        json_out = os.path.join(SAMPLE_DIR, base + '_results.json')
        csv_out = os.path.join(SAMPLE_DIR, base + '_results.csv')

        print(f"Generating sample for {dev} @ {int(b/1e6)} MHz -> {json_out}")
        # simulate_placeholder will create JSON and CSV in current dir; call with target path
        simulate_placeholder(b, output_path=json_out, preset=spec['preset'])
        # ensure CSV exists at csv_out location (simulate_placeholder writes base csv)
        basecsv = os.path.splitext(json_out)[0] + '.csv'
        if os.path.exists(basecsv) and basecsv != csv_out:
            os.replace(basecsv, csv_out)

        # simple summary entry
        summary_rows.append({'device': dev, 'freq_mhz': int(b/1e6), 'json': json_out, 'csv': csv_out, 'generated_at': datetime.utcnow().isoformat()+'Z'})

# write a combined summary
summary_csv = os.path.join(SAMPLE_DIR, 'samples_summary.csv')
with open(summary_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['device','freq_mhz','json','csv','generated_at'])
    writer.writeheader()
    for r in summary_rows:
        writer.writerow(r)

print('Sample generation complete. See', SAMPLE_DIR)