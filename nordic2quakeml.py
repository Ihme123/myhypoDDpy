import re

from datetime import datetime, timedelta

import xml.etree.ElementTree as ET



INPUT_FILE = 'hyp.out'

OUTPUT_FILE = 'hypoDD_quakeml.xml'



# Helper to parse event header line

def parse_event_header(lines):
    """
    Build a dict with the key fields we need.
    • Date-time is taken from the ID line (safe).
    • Seconds, lat, lon, depth still come from the type-1 header line.
    """
    hdr = lines[0]                         # first (type-1) line

    # --- date & time -------------------------------------------------
    id_line = next((l for l in lines if 'ID:' in l), None)
    m = re.search(r'ID:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})',
                  id_line or '')
    if not m:
        return None                        # malformed event
    yr, mo, dy, hr, mi, sec_id = map(int, m.groups())

    # seconds (keep decimal part from hdr if it is there)
    try:
        sec = float(hdr[15:21].strip())    # cols 16-21 (1-based)
    except ValueError:
        sec = sec_id

    try:
    origin = datetime(yr, mo, dy, hr, mi, int(sec),
                         int((sec - int(sec)) * 1e6))
    except ValueError as e:
        print(f"ValueError in parse_event_header: {e}")
        print(f"Header line: {hdr if hdr else 'N/A'}")
        print(f"Parsed values: yr={yr}, mo={mo}, dy={dy}, hr={hr}, mi={mi}, sec={sec}")
        raise
    origin_str = origin.isoformat(timespec='seconds')
    if sec % 1:
        origin_str = origin_str[:-1] + f"{sec%1:.1f}"[1:]
    origin_str += 'Z'

    # --- coordinates -------------------------------------------------
    def f(s):
        try:
            return float(s.strip())
        except ValueError:
            return None
    lat   = f(hdr[23:30])   # cols 24-30
    lon   = f(hdr[30:38])   # cols 31-38
    depth = f(hdr[38:44])   # cols 39-43 (km)

    agency = (re.search(r'\s([A-Z]{3})\s', hdr) or [None])[1]

    # --- magnitudes -------------------------------------------------
    mag_ml = None
    mag_md = None
    mag_ml_match = re.search(r'(\d+\.\d+)L', hdr)
    mag_md_match = re.search(r'(\d+\.\d+)C', hdr)
    if mag_ml_match:
        mag_ml = float(mag_ml_match.group(1))
    if mag_md_match:
        mag_md = float(mag_md_match.group(1))

    return {
        'lat': lat, 'lon': lon, 'depth': depth,
        'origin_time': origin,
        'origin_time_str': origin_str,
        'public_id': origin.strftime('%Y%m%d%H%M%S%f')[:-4],
        'agency': agency,
        'mag_ml': mag_ml,
        'mag_md': mag_md,
    }


# Helper to parse pick lines

def parse_pick_line(line, event_date):

    # Only parse lines that start with a station code (first 3 chars are digits)

    if not line[:3].strip().isdigit():

        return None



    if len(line) < 29:

        return None



    station = line[0:5].strip()

    channel = line[6:9].strip()

    phase = line[9:15].strip()

    polarity = line[16] if len(line) > 16 else ' '  # D, C, or space

    hour_str = line[18:20].strip()  # chars 19-20

    minute_str = line[20:22].strip()  # chars 21-22

    seconds = line[23:29].strip()



    if not station or not channel or not phase or not hour_str or not minute_str or not seconds:

        return None



    try:

        hour = int(hour_str)

        minute = int(minute_str)

        sec = float(seconds)

    except ValueError:

        return None



    if not (0 <= hour <= 23 and 0 <= minute <= 59):

        return None



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



    # DEBUG: Print the first 5 event headers as seen by the parser

    print("First 5 event headers as seen by the parser:")

    for i, ev in enumerate(events[:5]):

        # Find the first line that looks like a year (event header)

        header_line = next((l for l in ev if re.match(r'^\s*\d{4}', l)), None)

        header_line_short = header_line[:44] if header_line else None

        print(f"Event {i} header: {header_line_short}")

    print()



    # Build XML with proper formatting

    NSMAP = {

        'q': 'http://quakeml.org/xmlns/quakeml/1.2',

        None: 'http://quakeml.org/xmlns/bed/1.2',

        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',

    }

    ET.register_namespace('q', NSMAP['q'])

    ET.register_namespace('xsi', NSMAP['xsi'])

    root = ET.Element('{http://quakeml.org/xmlns/quakeml/1.2}quakeml', attrib={

        '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation':

            'http://quakeml.org/xmlns/quakeml/1.2 http://quakeml.org/schema/quakeml-1.2.xsd'

    })

    eventParameters = ET.SubElement(root, 'eventParameters', publicID='smi:local/eventParameters')



    events_processed = 0

    events_skipped = 0

    

    for i, ev in enumerate(events):

        if not ev or not ev[0].strip():

            continue

        header = parse_event_header(ev)

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

    

    # Parse and pretty print (remove indent for older Python versions)

    reparsed = ET.fromstring(rough_string)

    

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')

        f.write(ET.tostring(reparsed, encoding='unicode'))

    

    print(f'Wrote QuakeML to {OUTPUT_FILE}')

    print(f'Events processed: {events_processed}')

    print(f'Events skipped (no coordinates): {events_skipped}')



if __name__ == '__main__':

    main() 