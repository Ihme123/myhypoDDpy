# Velocity model setup code for HypoDD
# Extracted from STATION0.hyp

def get_velocity_model_code():
    """
    Returns the exact code to set up the velocity model in HypoDD
    """
    code = '''
# Velocity model extracted from STATION0.hyp
# Vp/Vs ratio: 1.73

relocator.setup_velocity_model(
    model_type="layered_p_velocity_with_constant_vp_vs_ratio",
    layer_tops=[
        (0.0, 5.01),        # Surface layer
        (-400.0, 6.31),     # 0.4 km depth
        (-9500.0, 6.39),    # 9.5 km depth
        (-15000.0, 6.41),   # 15.0 km depth
        (-20300.0, 6.82),   # 20.3 km depth
        (-31000.0, 7.34),   # 31.0 km depth
        (-35000.0, 8.08),   # 35.0 km depth
        (-38700.0, 8.25),   # 38.7 km depth
        (-42100.0, 8.50),   # 42.1 km depth
        (-60000.0, 8.50),   # 60.0 km depth
    ],
    vp_vs_ratio=1.73
)
'''
    return code

if __name__ == "__main__":
    print("HypoDD Velocity Model Setup Code")
    print("=" * 40)
    print(get_velocity_model_code())
    
    print("\nModel Summary:")
    print("10 velocity layers from 0 to 60 km depth")
    print("Vp ranges from 5.01 to 8.50 km/s")
    print("Vp/Vs ratio: 1.73")
    
    print("\nLayer details:")
    layers = [
        (0.0, 5.01), (-400.0, 6.31), (-9500.0, 6.39), (-15000.0, 6.41),
        (-20300.0, 6.82), (-31000.0, 7.34), (-35000.0, 8.08), (-38700.0, 8.25),
        (-42100.0, 8.50), (-60000.0, 8.50)
    ]
    
    for i, (depth, vp) in enumerate(layers):
        print(f"Layer {i+1:2d}: Depth = {depth/1000:5.1f} km, Vp = {vp:4.2f} km/s") 