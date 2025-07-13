import re
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

INPUT_FILE = 'hyp.out'
OUTPUT_FILE = 'hypoDD_quakeml.xml'

# Helper to parse event header line
def parse_event_header(line):
    # Example: 2016  8 3 0737 54.5 L  72.790 127.098 10.8  BER  4 0.3 0.5LBER 0.4CBER        1
    # Handle variable spacing and missing coordinates
    line = line.strip()
    
    # Extract date and time
    date_time_match = re.match(r'(\d{4})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{3,4})\s+([\d\.]+)', line)
    if not date_time_match:
        return None
    
    year = int(date_time_match.group(1))
    month = int(date_time_match.group(2))
    day = int(date_time_match.group(3))
    hrmm = date_time_match.group(4)
    sec = float(date_time_match.group(5))
    
    # Parse hour and minute from hrmm
    if len(hrmm) == 3:
        hour = int(hrmm[0])
        minute = int(hrmm[1:3])
    else:
        hour = int(hrmm[0:2])
        minute = int(hrmm[2:4])
    
    # Extract coordinates if present
    lat = None
    lon = None
    depth = None
    agency = None
    
    # Look for coordinates pattern: L  lat  lon  depth
    coord_match = re.search(r'L\s+([\d\.-]+)\s+([\d\.-]+)\s+([\d\.-]+)', line)
    if coord_match:
        lat = float(coord_match.group(1))
        lon = float(coord_match.group(2))
        depth = float(coord_match.group(3))
    
    # Extract agency (3-letter code after depth)
    agency_match = re.search(r'L\s+[\d\.-]+\s+[\d\.-]+\s+[\d\.-]+\s+(\w{3})', line)
    if not agency_match:
        # Try without coordinates
        agency_match = re.search(r'L\s+(\w{3})', line)
    
    if agency_match:
        agency = agency_match.group(1)
    
    # Extract magnitudes
    mag_ml = None
    mag_md = None
    mag_ml_match = re.search(r'(\d+\.\d+)L', line)
    mag_md_match = re.search(r'(\d+\.\d+)C', line)
    if mag_ml_match:
        mag_ml = float(mag_ml_match.group(1))
    if mag_md_match:
        mag_md = float(mag_md_match.group(1))
    
    # Compose origin time
    origin_time = datetime(year, month, day, hour, minute, int(sec), int((sec%1)*1e6))
    origin_time_str = origin_time.strftime('%Y-%m-%dT%H:%M:%S')
    if sec % 1:
        origin_time_str += f".{int((sec%1)*10):01d}"
    origin_time_str += 'Z'
    
    # For publicID
    public_id = f"{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}{sec:04.1f}".replace('.','')
    
    return {
        'year': year, 'month': month, 'day': day, 'hour': hour, 'minute': minute, 'sec': sec,
        'lat': lat, 'lon': lon, 'depth': depth, 'agency': agency,
        'mag_ml': mag_ml, 'mag_md': mag_md,
        'origin_time': origin_time, 'origin_time_str': origin_time_str,
        'public_id': public_id
    }

# Helper to parse pick lines
def parse_pick_line(line, event_date):
    # Example: 628  0Z IP     C  738  1.68   16 ...
    m = re.match(r'\s*(\d{3})\s+(\w{2})\s+(\w{2})\s+\w\s+(\d{3,4})\s+([\d\.]+)', line)
    if not m:
        return None
    station = m.group(1)
    channel = m.group(2)
    phase = m.group(3)
    hrmm = m.group(4)
    sec = float(m.group(5))
    # hrmm: e.g. 738 = 07:38, 1524 = 15:24
    if len(hrmm) == 3:
        hour = int(hrmm[0])
        minute = int(hrmm[1:3])
    else:
        hour = int(hrmm[0:2])
        minute = int(hrmm[2:4])
    # Compose pick time (use event date for Y/M/D)
    pick_time = datetime(event_date.year, event_date.month, event_date.day, hour, minute, int(sec), int((sec%1)*1e6))
    pick_time_str = pick_time.strftime('%Y-%m-%dT%H:%M:%S')
    if sec % 1:
        pick_time_str += f".{int((sec%1)*10):01d}"
    pick_time_str += 'Z'
    return {
        'station': station,
        'channel': channel,
        'phase': phase,
        'pick_time_str': pick_time_str
    }

def main():
    # Read file and split into events
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    events = []
    event = []
    for line in lines:
        if line.strip() == '' and event:
            events.append(event)
            event = []
        else:
            event.append(line.rstrip('\n'))
    if event:
        events.append(event)

    # Build XML with simple structure
    root = ET.Element('quakeml', {
        'xmlns': 'http://quakeml.org/xmlns/quakeml/1.2',
        'xmlns:q': 'http://quakeml.org/xmlns/quakeml/1.2'
    })
    eventParameters = ET.SubElement(root, 'eventParameters', publicID='smi:local/eventParameters')

    events_processed = 0
    events_skipped = 0
    
    for i, ev in enumerate(events):
        if not ev or not ev[0].strip():
            continue
        header = parse_event_header(ev[0])
        if not header:
            continue
            
        # Skip events without coordinates
        if header['lat'] is None or header['lon'] is None:
            events_skipped += 1
            continue
            
        events_processed += 1
        event_elem = ET.SubElement(eventParameters, 'event', publicID=f"smi:local/event/{header['public_id']}")
        
        # Origin
        origin_elem = ET.SubElement(event_elem, 'origin', publicID=f"smi:local/origin/{header['public_id']}")
        time_elem = ET.SubElement(origin_elem, 'time')
        ET.SubElement(time_elem, 'value').text = header['origin_time_str']
        
        # Add coordinates
        lat_elem = ET.SubElement(origin_elem, 'latitude')
        ET.SubElement(lat_elem, 'value').text = str(header['lat'])
        lon_elem = ET.SubElement(origin_elem, 'longitude')
        ET.SubElement(lon_elem, 'value').text = str(header['lon'])
        
        # Add depth if available
        if header['depth'] is not None:
            depth_elem = ET.SubElement(origin_elem, 'depth')
            ET.SubElement(depth_elem, 'value').text = str(int(header['depth']*1000))
        
        if header['agency']:
            creationInfo = ET.SubElement(origin_elem, 'creationInfo')
            ET.SubElement(creationInfo, 'agencyID').text = header['agency']
        
        # Magnitudes
        if header['mag_ml'] is not None:
            mag_elem = ET.SubElement(event_elem, 'magnitude', publicID=f"smi:local/mag/{header['public_id']}/ML")
            mag_val = ET.SubElement(mag_elem, 'mag')
            ET.SubElement(mag_val, 'value').text = str(header['mag_ml'])
            ET.SubElement(mag_elem, 'type').text = 'ML'
            if header['agency']:
                mag_creation = ET.SubElement(mag_elem, 'creationInfo')
                ET.SubElement(mag_creation, 'agencyID').text = header['agency']
        if header['mag_md'] is not None:
            mag_elem = ET.SubElement(event_elem, 'magnitude', publicID=f"smi:local/mag/{header['public_id']}/Md")
            mag_val = ET.SubElement(mag_elem, 'mag')
            ET.SubElement(mag_val, 'value').text = str(header['mag_md'])
            ET.SubElement(mag_elem, 'type').text = 'Md'
            if header['agency']:
                mag_creation = ET.SubElement(mag_elem, 'creationInfo')
                ET.SubElement(mag_creation, 'agencyID').text = header['agency']
        
        # Picks
        pick_idx = 1
        for line in ev:
            pick = parse_pick_line(line, header['origin_time'])
            if pick:
                # Map 'IP' to 'P', 'ES' to 'S', else keep as is
                phase_hint = pick['phase']
                if phase_hint.upper() == 'IP':
                    phase_hint = 'P'
                elif phase_hint.upper() == 'ES':
                    phase_hint = 'S'
                pick_elem = ET.SubElement(event_elem, 'pick', publicID=f"smi:local/e{i+1}p{pick_idx}")
                time_elem = ET.SubElement(pick_elem, 'time')
                ET.SubElement(time_elem, 'value').text = pick['pick_time_str']
                ET.SubElement(pick_elem, 'waveformID', networkCode='SI', stationCode=pick['station'], channelCode=pick['channel'])
                ET.SubElement(pick_elem, 'phaseHint').text = phase_hint
                pick_idx += 1

    # Write XML with proper formatting
    tree = ET.ElementTree(root)
    
    # Create a properly formatted XML string
    rough_string = ET.tostring(root, encoding='unicode')
    
    # Parse and pretty print
    reparsed = ET.fromstring(rough_string)
    ET.indent(reparsed, space="  ")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(ET.tostring(reparsed, encoding='unicode'))
    
    print(f'Wrote QuakeML to {OUTPUT_FILE}')
    print(f'Events processed: {events_processed}')
    print(f'Events skipped (no coordinates): {events_skipped}')

if __name__ == '__main__':
    main() 