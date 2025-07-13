#!/usr/bin/env python3
"""
Script to filter out events without picks from QuakeML file
"""
from obspy import read_events

def filter_events(input_file, output_file):
    """
    Filter out events without picks
    """
    # Read the catalog
    cat = read_events(input_file)
    print(f"Original catalog: {len(cat)} events")
    
    # Filter events with picks
    filtered_events = []
    for i, ev in enumerate(cat):
        if len(ev.picks) > 0:
            filtered_events.append(ev)
            print(f"Keeping event {i}: {len(ev.picks)} picks")
        else:
            print(f"Removing event {i}: 0 picks")
    
    # Create new catalog
    from obspy.core.event import Catalog
    filtered_cat = Catalog(events=filtered_events)
    
    print(f"Filtered catalog: {len(filtered_cat)} events")
    
    # Write filtered catalog
    filtered_cat.write(output_file, format="QUAKEML")
    print(f"Filtered catalog saved as: {output_file}")

if __name__ == "__main__":
    filter_events("hypoDD_quakeml_fixed.xml", "hypoDD_quakeml_filtered.xml") 