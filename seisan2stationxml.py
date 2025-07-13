import re
from obspy.core.inventory import Inventory, Network, Station, Channel, Site
from obspy.core.inventory.util import Equipment
import xml.etree.ElementTree as ET

def parse_seisan_coordinates(coord_str):
    """
    Parse SEISAN coordinate format like '7239.24N12420.82E'
    Returns (lat, lon) in decimal degrees
    """
    # Extract latitude part (before longitude)
    lat_match = re.match(r'(\d{2})(\d{2}\.\d{2})([NS])', coord_str)
    if not lat_match:
        return None, None
    
    lat_deg = int(lat_match.group(1))
    lat_min = float(lat_match.group(2))
    lat_dir = lat_match.group(3)
    
    # Extract longitude part (after latitude)
    lon_str = coord_str[lat_match.end():]
    lon_match = re.match(r'(\d{3})(\d{2}\.\d{2})([EW])', lon_str)
    if not lon_match:
        return None, None
    
    lon_deg = int(lon_match.group(1))
    lon_min = float(lon_match.group(2))
    lon_dir = lon_match.group(3)
    
    # Convert to decimal degrees
    lat = lat_deg + lat_min / 60.0
    if lat_dir == 'S':
        lat = -lat
    
    lon = lon_deg + lon_min / 60.0
    if lon_dir == 'W':
        lon = -lon
    
    return lat, lon

def convert_seisan_to_stationxml(input_file, output_file):
    """
    Convert SEISAN station file to StationXML format
    """
    # Create inventory
    inv = Inventory(
        networks=[],
        source="SEISAN station file conversion"
    )
    
    # Create network
    network = Network(
        code="SI",
        description="Converted from SEISAN station file"
    )
    
    stations = []
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('RESET') or line.startswith('5.01') or line.startswith('BER'):
            continue
        
        # Parse station line: "620 7239.24N12420.82E 12"
        parts = line.split()
        if len(parts) >= 2:
            station_code = parts[0]
            coord_str = parts[1]
            elevation = float(parts[2]) if len(parts) > 2 else 0.0
            
            # Parse coordinates
            lat, lon = parse_seisan_coordinates(coord_str)
            if lat is not None and lon is not None:
                # Create station
                station = Station(
                    code=station_code,
                    latitude=lat,
                    longitude=lon,
                    elevation=elevation * 1000.0,  # Convert km to meters
                    site=Site(name=f"Station {station_code}")
                )
                
                # Add a dummy channel (HypoDD doesn't need specific channels)
                channel = Channel(
                    code="HHZ",
                    location_code="00",
                    latitude=lat,
                    longitude=lon,
                    elevation=elevation * 1000.0,
                    depth=0.0,
                    azimuth=0.0,
                    dip=0.0,
                    sample_rate=100.0
                )
                
                station.channels.append(channel)
                stations.append(station)
    
    # Add stations to network
    network.stations = stations
    
    # Add network to inventory
    inv.networks.append(network)
    
    # Write StationXML file
    inv.write(output_file, format="STATIONXML")
    print(f"Converted {len(stations)} stations to {output_file}")
    
    return inv

def main():
    input_file = "STATION0.hyp"
    output_file = "stations.xml"
    
    try:
        inv = convert_seisan_to_stationxml(input_file, output_file)
        print(f"Successfully converted {len(inv.networks[0].stations)} stations")
        print(f"Output file: {output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 