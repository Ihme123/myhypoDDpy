def extract_velocity_model_from_station_hyp(filename="STATION0.hyp"):
    """
    Extract velocity model from SEISAN station file
    Returns layer_tops list for HypoDD
    """
    layer_tops = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Find velocity model section (lines 25-34 in this case)
    # Look for lines with velocity and depth values
    for line in lines:
        line = line.strip()
        if line and not line.startswith('RESET') and not line.startswith('BER'):
            # Check if line contains velocity model data
            parts = line.split()
            if len(parts) == 2:
                try:
                    vp = float(parts[0])
                    depth = float(parts[1])
                    # Convert depth from km to meters and make it negative (depth below surface)
                    depth_m = -depth * 1000.0
                    layer_tops.append((depth_m, vp))
                except ValueError:
                    continue
    
    return layer_tops

def setup_hypodd_velocity_model(relocator, station_file="STATION0.hyp", vp_vs_ratio=1.73):
    """
    Setup velocity model for HypoDD from SEISAN station file
    """
    print("Extracting velocity model from SEISAN station file...")
    
    # Extract velocity model
    layer_tops = extract_velocity_model_from_station_hyp(station_file)
    
    if not layer_tops:
        print("Error: Could not extract velocity model from station file")
        return False
    
    # Sort by depth (ascending)
    layer_tops.sort(key=lambda x: x[0])
    
    print(f"Found {len(layer_tops)} velocity layers:")
    for depth, vp in layer_tops:
        print(f"  Depth: {depth/1000:.1f} km, Vp: {vp:.2f} km/s")
    
    print(f"Vp/Vs ratio: {vp_vs_ratio}")
    
    # Setup the velocity model in HypoDD
    relocator.setup_velocity_model(
        model_type="layered_p_velocity_with_constant_vp_vs_ratio",
        layer_tops=layer_tops,
        vp_vs_ratio=vp_vs_ratio
    )
    
    print("Velocity model successfully set up for HypoDD!")
    return True

# Example usage
if __name__ == "__main__":
    # This is just for testing the extraction
    print("Testing velocity model extraction...")
    layer_tops = extract_velocity_model_from_station_hyp()
    
    print(f"\nExtracted {len(layer_tops)} layers:")
    for depth, vp in layer_tops:
        print(f"  Depth: {depth/1000:.1f} km, Vp: {vp:.2f} km/s")
    
    print(f"\nVp/Vs ratio: 1.73")
    
    print("\nHypoDD setup code:")
    print("relocator.setup_velocity_model(")
    print("    model_type=\"layered_p_velocity_with_constant_vp_vs_ratio\",")
    print("    layer_tops=[")
    for depth, vp in layer_tops:
        print(f"        ({depth}, {vp}),")
    print("    ],")
    print("    vp_vs_ratio=1.73")
    print(")") 