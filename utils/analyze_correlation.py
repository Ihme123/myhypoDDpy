#!/usr/bin/env python3

import json

# Load the cross-correlation results
with open('hypodd_cross_correlation_results.json', 'r') as f:
    data = json.load(f)

# Extract all correlation coefficients
coeffs = []
for pick_data in data.values():
    for target_pick, result in pick_data.items():
        if isinstance(result, list) and len(result) == 2:
            coeffs.append(result[1])

print(f"Total correlation coefficients: {len(coeffs)}")
if coeffs:
    print(f"Max correlation: {max(coeffs):.3f}")
    print(f"Min correlation: {min(coeffs):.3f}")
    print(f"Mean correlation: {sum(coeffs)/len(coeffs):.3f}")
    print(f"Correlations > 0.5: {sum(1 for c in coeffs if c > 0.5)}")
    print(f"Correlations > 0.4: {sum(1 for c in coeffs if c > 0.4)}")
    print(f"Correlations > 0.3: {sum(1 for c in coeffs if c > 0.3)}")
    print(f"Correlations > 0.2: {sum(1 for c in coeffs if c > 0.2)}")

# Check how many events were processed
unique_events = set()
for pick_id in data.keys():
    event_id = pick_id.split('/')[1].split('p')[0]  # Extract event ID from pick ID
    unique_events.add(event_id)

print(f"\nUnique events processed: {len(unique_events)}")

# Check the HypoDD output
print(f"\nHypoDD relocation results:")
print("Only 2 events were relocated, which means:")
print("1. Most event pairs had correlation coefficients below 0.5 (your threshold)")
print("2. Events may be too far apart or not well-connected")
print("3. Waveform quality may be poor for cross-correlation")
print("4. Your HypoDD parameters may be too restrictive") 