import json
import random
import csv
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Transmitters: (transmitterId, transmitterIdType)
# transmittersignature = f"{transmitterId}/{transmitterIdType}"
TRANSMITTERS = [
    ("bada55beac04", 3),
    ("bada55beac05", 3),
    ("bada55beac06", 3),
    ("aabbccddeeff", 3),
    ("aabbccddee01", 3),
    ("aabbccddee02", 3),
    ("cafe00112233", 2),
    ("cafe00112244", 2),
    ("deadbeef0001", 3),
    ("deadbeef0002", 3),
    ("112233445566", 3),
    ("ffeeddccbbaa", 3),
]

RECEIVERS = [
    ("001bc50940810000", 1),
    ("001bc50940820000", 1),
    ("001bc50940830000", 1),
    ("001bc50940840000", 1),
    ("001bc50940850000", 1),
]
NB_ROWS           = 1000     # number of rows to generate
BEACON_INTERVAL_MS = 5000   # ~5 seconds between packets per transmitter
JITTER_MS         = 200     # ±200ms jitter on each interval

# Each transmitter gets a random window width between 5 min and 6 hours
#BASE_START_UTC = datetime(2026, 4, 18, 14, 0, 0, tzinfo=timezone.utc)  # 10:00 EDT
BASE_START_UTC = datetime.now(tz=timezone.utc).replace(hour=14, minute=0, second=0, microsecond=0)  # today at 14:00 UTC

# ---------------------------------------------------------------------------
# Build per-transmitter time windows
# ---------------------------------------------------------------------------

random.seed(42)  # remove for different data on each run

transmitter_windows = {}
for tx_id, tx_type in TRANSMITTERS:
    offset_min   = random.randint(0, 120)    
    window_sec = random.randint(1, 800)  # 1 second to 15 min
    start      = BASE_START_UTC + timedelta(seconds=random.randint(0, 7200))
    end        = start + timedelta(seconds=window_sec)
    transmitter_windows[(tx_id, tx_type)] = (start, end)

# ---------------------------------------------------------------------------
# Distribute 100 rows across transmitters
# ---------------------------------------------------------------------------

tx_pool = []
for tx in TRANSMITTERS:
    count = random.randint(5, 12)
    tx_pool.extend([tx] * count)

random.shuffle(tx_pool)
tx_pool = tx_pool[:NB_ROWS]
while len(tx_pool) < NB_ROWS:
    tx_pool.append(random.choice(TRANSMITTERS))
random.shuffle(tx_pool)
tx_pool = tx_pool[:NB_ROWS]

# ---------------------------------------------------------------------------
# Generate rows
# ---------------------------------------------------------------------------

rows = []
for (tx_id, tx_type) in tx_pool:
    start, end = transmitter_windows[(tx_id, tx_type)]
    delta_s    = (end - start).total_seconds()
    ts_dt      = start + timedelta(seconds=random.uniform(0, delta_s))

    # Add realistic jitter to milliseconds
    jitter_ms  = random.randint(-JITTER_MS, JITTER_MS)
    ts_ms      = int(ts_dt.timestamp() * 1000) + jitter_ms

    rx_id, rx_type = random.choice(RECEIVERS)
    rssi           = random.randint(-95, -35)
    n_decodings    = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
    n_receivers    = random.choices([1, 2, 3], weights=[70, 20, 10])[0]

    signature = f"{tx_id}/{tx_type}"

    raddec = {
        "rssi":               rssi,
        "timestamp":          ts_ms,
        "receiverId":         rx_id,
        "transmitterId":      tx_id,
        "receiverIdType":     rx_type,
        "numberOfDecodings":  n_decodings,
        "numberOfReceivers":  n_receivers,
        "transmitterIdType":  tx_type,
    }

    # Reconstruct timezone-aware timestamp string for the 'timestamp' column
    ts_aware = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

    rows.append({
        "transmittersignature": signature,
        "timestamp":            ts_aware.isoformat(),
        "raddec":               json.dumps(raddec),
    })

# Sort by timestamp for a cleaner dataset
rows.sort(key=lambda r: r["timestamp"])

# ---------------------------------------------------------------------------
# Write CSV
# ---------------------------------------------------------------------------

output_path = "./raddec_for_testing.csv"
with open(output_path, "w", newline="") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(["transmittersignature", "timestamp", "raddec"])
    for row in rows:
        writer.writerow([row["transmittersignature"], row["timestamp"], row["raddec"]])

print(f"Generated {len(rows)} rows -> {output_path}\n")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

 
from collections import defaultdict
windows_actual = defaultdict(list)
for row in rows:
    windows_actual[row["transmittersignature"]].append(row["timestamp"])
 
print(f"{'Signature':<20} {'# rows':>6}  {'First seen':<35} {'Last seen':<35} {'Window'}")
print("-" * 115)
for sig in sorted(windows_actual):
    times  = sorted(windows_actual[sig])
    first  = times[0]
    last   = times[-1]
    dt1    = datetime.fromisoformat(first)
    dt2    = datetime.fromisoformat(last)
    width  = dt2 - dt1
    total_s = int(width.total_seconds())
    h, rem  = divmod(total_s, 3600)
    m, s    = divmod(rem, 60)
    width_str = f"{h}h {m:02d}m {s:02d}s"
    print(f"{sig:<20} {len(times):>6}  {first:<35} {last:<35} {width_str}")