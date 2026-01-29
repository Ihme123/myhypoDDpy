import os
import sys
import shutil
from pathlib import Path
from preprocessing.setup_velocity_model import setup_hypodd_velocity_model
import logging, logging.handlers
import builtins
import warnings
import re

# Базовый путь относительно расположения скрипта
BASE_PATH = Path(__file__).parent / "example_data"

# Флаг для очистки рабочей директории перед запуском
CLEAN_WORKDIR = False

# Add the hypoDDpy directory to the path
sys.path.append('./hypoDDpy')

from hypoddpy.hypodd_relocator import HypoDDRelocator

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module=r"obspy\.io\.mseed\.util"
)

working_dir = "hypodd_working"             # whatever you pass to HypoDDRelocator


def delete_hypoddworking(workdir: str = working_dir) -> None:
    """Очистить рабочую директорию HypoDD."""
    workdir_path = Path(workdir)
    if workdir_path.exists():
        shutil.rmtree(workdir_path)
        print(f"Рабочая директория '{workdir}' очищена")
    workdir_path.mkdir(parents=True, exist_ok=True)


def setup_logging(workdir: str = working_dir) -> None:
    """Настройка логирования."""
    logfile = Path(workdir) / "hypodd_debug.log"

    # Файловый handler - пишет всё (DEBUG и выше)
    file_handler = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=50_000_000, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)

    # Консольный handler - только INFO и выше (без DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler],
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


old_print = builtins.print
def print_and_log(*args, **kwargs):
    message = " ".join(str(a) for a in args)
    logging.debug(message)
    old_print(*args, **kwargs)
builtins.print = print_and_log

def main():
    """
    Complete HypoDD setup and run script
    """
    # Очистка рабочей директории если нужно
    if CLEAN_WORKDIR:
        delete_hypoddworking(working_dir)
    else:
        Path(working_dir).mkdir(parents=True, exist_ok=True)

    # Настройка логирования
    setup_logging(working_dir)

    print("HypoDD Earthquake Relocation Setup")
    print("=" * 50)
    
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
    relocator.add_event_files(str(BASE_PATH / "events.xml"))

    # Add station files (StationXML)
    print("Adding station files...")
    relocator.add_station_files(str(BASE_PATH / "stations.xml"))

    # Add waveform files (mseed)
    print("Adding waveform files...")
    waveform_files = []
    waveforms_dir = BASE_PATH / "waveforms"
    if waveforms_dir.exists():
        for file in os.listdir(waveforms_dir):
            waveform_files.append(str(waveforms_dir / file))
    
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
    success = setup_hypodd_velocity_model(relocator, str(BASE_PATH / "STATION0.hyp"), 1.73)
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
