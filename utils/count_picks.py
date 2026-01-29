#!/usr/bin/env python3
"""
Script to count different types of picks (IP, ES, IAML) for each event
"""
from obspy import read_events
from collections import Counter

def count_pick_types(quakeml_file):
    """
    Count IP, ES, and IAML picks for each event
    """
    cat = read_events(quakeml_file)
    
    print(f"Number of events: {len(cat)}")
    print("\nPick counts per event:")
    print("Event | Date       | Total | IP | ES | IAML | Other")
    print("-" * 55)
    
    for i, ev in enumerate(cat):
        # Get event date
        if ev.origins and ev.origins[0].time:
            event_date = ev.origins[0].time.strftime('%Y-%m-%d')
        else:
            event_date = "Unknown"
        
        # Count pick types
        pick_types = []
        for pick in ev.picks:
            phase = pick.phase_hint
            if phase:
                pick_types.append(phase)
        
        # Count occurrences
        counts = Counter(pick_types)
        
        total = len(ev.picks)
        ip_count = counts.get('IP', 0)
        es_count = counts.get('ES', 0)
        iaml_count = counts.get('IAML', 0)
        other_count = total - ip_count - es_count - iaml_count
        
        print(f"{i:5d} | {event_date} | {total:5d} | {ip_count:2d} | {es_count:2d} | {iaml_count:4d} | {other_count:5d}")
    
    # Summary
    print("\nSummary:")
    total_events = len(cat)
    total_picks = sum(len(ev.picks) for ev in cat)
    total_ip = sum(sum(1 for pick in ev.picks if pick.phase_hint == 'IP') for ev in cat)
    total_es = sum(sum(1 for pick in ev.picks if pick.phase_hint == 'ES') for ev in cat)
    total_iaml = sum(sum(1 for pick in ev.picks if pick.phase_hint == 'IAML') for ev in cat)
    
    print(f"Total events: {total_events}")
    print(f"Total picks: {total_picks}")
    print(f"Total IP picks: {total_ip}")
    print(f"Total ES picks: {total_es}")
    print(f"Total IAML picks: {total_iaml}")

if __name__ == "__main__":
    count_pick_types("hypoDD_quakeml_fixed.xml") 