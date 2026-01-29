# myhypoDDpy

HypoDD earthquake relocation workflow for SEISAN data.

## Overview

This package provides a complete workflow to relocate earthquakes using the HypoDD double-difference algorithm. It includes preprocessing scripts to convert SEISAN format data to HypoDD-compatible formats.

**Features:**
- Convert SEISAN hyp.out (Nordic format) to QuakeML
- Convert SEISAN STATION0.hyp to StationXML
- Cross-correlation based differential times
- Support for layered velocity models

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

Main dependencies:
- ObsPy >= 1.4.0
- NumPy >= 1.20.0
- Matplotlib >= 3.5.0

### Compiling HypoDD

HypoDD requires a Fortran compiler (gfortran). On Linux/macOS:

```bash
cd HYPODD/src
# Fix Makefiles for your system (if needed)
python ../../utils/fix_makefiles.py
make
```

On Windows, use WSL or MinGW with gfortran.

## Quick Start

### 1. Prepare Input Data

You need:
- `hyp.out` - SEISAN location file (Nordic format)
- `STATION0.hyp` - SEISAN station file with coordinates and velocity model
- Waveform files (miniSEED format)

### 2. Convert SEISAN Data

```bash
# Step 1: Convert hyp.out to QuakeML
cd preprocessing
python nordic2quakeml.py

# Step 2: Fix namespace issues
python fix_quakeml.py

# Step 3: Remove events without picks (optional)
python filter_events.py

# Step 4: Create StationXML from STATION0.hyp
python seisan2stationxml.py
```

### 3. Copy Waveforms

```bash
python copy_mseed_files.py
```

This copies waveforms from SEISAN WAV directory to local `waveforms/` folder.

### 4. Run HypoDD

```bash
cd ..
python run_hypodd.py
```

## Workflow Steps

### Data Flow

```
SEISAN hyp.out ──► nordic2quakeml.py ──► fix_quakeml.py ──► events.xml
                                                               │
STATION0.hyp ──────► seisan2stationxml.py ─────────────► stations.xml
                                                               │
SEISAN WAV/ ───────► copy_mseed_files.py ──────────────► waveforms/
                                                               │
                                                               ▼
                                                        run_hypodd.py
                                                               │
                                                               ▼
                                                    relocated_events.xml
```

### Preprocessing Scripts

| Script | Description |
|--------|-------------|
| `nordic2quakeml.py` | Convert SEISAN hyp.out to QuakeML format |
| `fix_quakeml.py` | Fix namespace prefixes in QuakeML |
| `filter_events.py` | Remove events without phase picks |
| `seisan2stationxml.py` | Convert STATION0.hyp to StationXML |
| `setup_velocity_model.py` | Extract velocity model from STATION0.hyp |
| `copy_mseed_files.py` | Copy waveforms from SEISAN directory |

## Configuration

### HypoDD Parameters

Key parameters in `run_hypodd.py`:

```python
relocator = HypoDDRelocator(
    working_dir="hypodd_working",
    cc_time_before=2.0,        # seconds before pick for cross-correlation
    cc_time_after=2.0,         # seconds after pick
    cc_maxlag=0.8,             # maximum lag time (s)
    cc_filter_min_freq=6.0,    # bandpass filter low frequency (Hz)
    cc_filter_max_freq=16.0,   # bandpass filter high frequency (Hz)
    cc_min_allowed_cross_corr_coeff=0.5,  # minimum CC coefficient
)
```

### Velocity Model

The velocity model is extracted from STATION0.hyp. Format:

```
Vp  Depth
5.0  0.0
6.0  10.0
6.5  25.0
8.0  40.0
```

Vp/Vs ratio is set in `run_hypodd.py` (default: 1.73).

## Output Files

| File | Description |
|------|-------------|
| `hypodd_relocated_events.xml` | Relocated event catalog (QuakeML) |
| `hypodd_cross_correlation_results.json` | CC differential times |
| `hypodd_working/` | Working directory with intermediate files |

## Troubleshooting

### "No waveform files found"

Ensure waveforms are in `waveforms/` directory. Run `copy_mseed_files.py` first.

### "Could not extract velocity model"

Check STATION0.hyp format. Velocity model should have two columns: Vp and depth.

### Cross-correlation fails

- Check waveform sampling rate matches filter frequencies
- Increase `cc_time_before/after` for longer windows
- Decrease `cc_min_allowed_cross_corr_coeff` threshold

## Project Structure

```
myhypoDDpy/
├── README.md
├── requirements.txt
├── .gitignore
├── run_hypodd.py           # Main entry point
│
├── preprocessing/          # Data preparation scripts
│   ├── nordic2quakeml.py
│   ├── fix_quakeml.py
│   ├── filter_events.py
│   ├── seisan2stationxml.py
│   ├── setup_velocity_model.py
│   └── copy_mseed_files.py
│
├── utils/                  # Utility scripts
│   ├── analyze_correlation.py
│   ├── count_picks.py
│   └── fix_makefiles.py
│
├── example_data/           # Example files
│   ├── STATION0.hyp
│   ├── hyp.out
│   ├── stations.xml
│   └── events.xml
│
├── hypoDDpy/              # Core library
│
└── HYPODD/                # HypoDD Fortran source
```

## License

This project uses:
- [hypoDDpy](https://github.com/krischer/hypoDDpy) - MIT License
- [HypoDD](https://www.ldeo.columbia.edu/~felixw/hypoDD.html) - See HYPODD/doc for license

## References

- Waldhauser, F., & Ellsworth, W. L. (2000). A double-difference earthquake location algorithm: Method and application to the northern Hayward fault, California. BSSA, 90(6), 1353-1368.
