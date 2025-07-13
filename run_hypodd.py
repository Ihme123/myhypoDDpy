import os
import sys
from setup_velocity_model import setup_hypodd_velocity_model
import os, logging, logging.handlers, pathlib
import builtins
import warnings
import re

# Add the hypoDDpy directory to the path
sys.path.append('./hypoDDpy')

from hypoddpy.hypodd_relocator import HypoDDRelocator

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module=r"obspy\.io\.mseed\.util"
)

working_dir = "hypodd_working"             # whatever you pass to HypoDDRelocator
logfile = pathlib.Path(working_dir) / "hypodd_debug.log"

logging.basicConfig(          # this sets the *root* logger
    level=logging.DEBUG,      # capture everything – DEBUG, INFO, …
    handlers=[
        logging.handlers.RotatingFileHandler(
            logfile, maxBytes=50_000_000, backupCount=3  # ~50 MB × 3 files
        ),
        logging.StreamHandler()   # still see the coloured “>>> …” lines
    ],
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
old_print = builtins.print
def print_and_log(*args, **kwargs):
    message = " ".join(str(a) for a in args)
    logging.debug(message)    # goes to the file
    old_print(*args, **kwargs)  # still shows in terminal
builtins.print = print_and_log

def main():
    """
    Complete HypoDD setup and run script
    """
    print("HypoDD Earthquake Relocation Setup")
    print("=" * 50)
    
    # Working directory for HypoDD
    working_dir = "hypodd_working"
    
    # Initialize HypoDD relocator
    print("Initializing HypoDD relocator...")
    relocator = HypoDDRelocator(
        working_dir=working_dir,
        cc_time_before=2.0,      # Time before pick for cross-correlation
        cc_time_after=2.0,       # Time after pick for cross-correlation
        cc_maxlag=0.8,           # Maximum lag time for cross-correlation
        cc_filter_min_freq=6.0,  # Lower frequency for bandpass filter
        cc_filter_max_freq=16.0, # Upper frequency for bandpass filter
        cc_p_phase_weighting={"Z": 1.0},  # P-phase channel weights
        cc_s_phase_weighting={"Z": 1.0},  # S-phase channel weights
        cc_min_allowed_cross_corr_coeff=0.5,  # Minimum cross-correlation coefficient
        shift_stations=True  # Shift stations so deepest is at elev=0
    )
    
    # Add event files (QuakeML)
    print("\nAdding event files...")
    relocator.add_event_files("hypoDD_quakeml_fixed.xml")
    
    # Add station files (StationXML)
    print("Adding station files...")
    relocator.add_station_files("stations.xml")
    
    # Add waveform files (mseed)
    print("Adding waveform files...")
    waveform_files = []
    if os.path.exists("waveforms"):
        for file in os.listdir("waveforms"):
            waveform_files.append(os.path.join("waveforms", file))
    
    if waveform_files:
        relocator.add_waveform_files(waveform_files)
        print("Number of waveform files:", len(relocator.waveform_files))
        for f in relocator.waveform_files:
            if "2017-03-23-1612" in f and "622" in f:
                print(">>> FOUND the 16-12 file in relocator.waveform_files:", f)
    else:
        print("Warning: No waveform files found!")
    
    # Setup velocity model
    print("\nSetting up velocity model...")
    success = setup_hypodd_velocity_model(relocator, "STATION0.hyp", 1.73)
    if not success:
        print("Error setting up velocity model!")
        return
    
    # Optional: Set forced configuration values if needed
    print("\nSetting configuration parameters...")
    relocator.set_forced_configuration_value("MINWGHT", 0.0)
    relocator.set_forced_configuration_value("MAXDIST", 200.0)  # km
    relocator.set_forced_configuration_value("MAXSEP", 20.0)    # km
    relocator.set_forced_configuration_value("MAXNGH", 15)
    relocator.set_forced_configuration_value("MINLNK", 4)
    relocator.set_forced_configuration_value("MINOBS", 4)
    relocator.set_forced_configuration_value("MAXOBS", 100)
    
    # Start the relocation process
    print("\nStarting HypoDD relocation...")
    output_file = "hypodd_relocated_events.xml"
    cross_corr_file = "hypodd_cross_correlation_results.json"
    
    try:
        relocator.start_relocation(
            output_event_file=output_file,
            output_cross_correlation_file=cross_corr_file,
            create_plots=True
        )
        print(f"\nRelocation completed successfully!")
        print(f"Output file: {output_file}")
        print(f"Cross-correlation results: {cross_corr_file}")
        
    except Exception as e:
        print(f"Error during relocation: {e}")
        print("Check the log file in the working directory for details.")

if __name__ == "__main__":
    main() 
