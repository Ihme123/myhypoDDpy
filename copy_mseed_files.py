import os
import shutil
import glob
from pathlib import Path

def copy_mseed_files(years=None):
    """
    Copy mseed files from SEISAN directory to HypoDD working directory
    """
    if years is None:
        years = [2016, 2017]
    
    # Source directory
    source_base = r"C:\Seismo\WAV\SPRC1"
    
    # Destination directory (create if it doesn't exist)
    dest_dir = "waveforms"
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created directory: {dest_dir}")
    
    total_files = 0
    copied_files = 0
    
    for year in years:
        year_path = os.path.join(source_base, str(year))
        if not os.path.exists(year_path):
            print(f"Year {year} directory not found: {year_path}")
            continue
            
        print(f"\nProcessing year: {year}")
        
        # Get all month directories
        month_dirs = []
        for i in range(1, 13):
            month_path = os.path.join(year_path, f"{i:02d}")
            if os.path.exists(month_path):
                month_dirs.append(month_path)
        
        print(f"Found {len(month_dirs)} month directories for {year}")
        
        for month_dir in month_dirs:
            month_name = os.path.basename(month_dir)
            print(f"\nProcessing {year}-{month_name}")
            
            # Get all files in the month directory
            files = os.listdir(month_dir)
            
            for file in files:
                file_path = os.path.join(month_dir, file)
                
                # Check if it's a file (not directory)
                if os.path.isfile(file_path):
                    total_files += 1
                    
                    # Copy the file to destination
                    dest_path = os.path.join(dest_dir, file)
                    
                    try:
                        shutil.copy2(file_path, dest_path)
                        copied_files += 1
                        print(f"  Copied: {file}")
                    except Exception as e:
                        print(f"  Error copying {file}: {e}")
    
    print(f"\nSummary:")
    print(f"Total files found: {total_files}")
    print(f"Files copied: {copied_files}")
    print(f"Destination: {os.path.abspath(dest_dir)}")

def list_mseed_files(years=None):
    """
    List all mseed files in the source directory for verification
    """
    if years is None:
        years = [2016, 2017]
    
    source_base = r"C:\Seismo\WAV\SPRC1"
    
    print("Scanning for mseed files...")
    
    for year in years:
        year_path = os.path.join(source_base, str(year))
        if not os.path.exists(year_path):
            print(f"\nYear {year}: Directory not found")
            continue
            
        print(f"\nYear {year}:")
        
        for month in range(1, 13):
            month_path = os.path.join(year_path, f"{month:02d}")
            if os.path.exists(month_path):
                files = os.listdir(month_path)
                mseed_files = [f for f in files if os.path.isfile(os.path.join(month_path, f))]
                if mseed_files:
                    print(f"  Month {month:02d}: {len(mseed_files)} files")
                    for file in mseed_files[:3]:  # Show first 3 files
                        print(f"    {file}")
                    if len(mseed_files) > 3:
                        print(f"    ... and {len(mseed_files) - 3} more files")

if __name__ == "__main__":
    print("SEISAN to HypoDD mseed file copier")
    print("=" * 40)
    
    # First, list the files to see what we're working with
    list_mseed_files()
    
    print("\n" + "=" * 40)
    print("Options:")
    print("1. Copy 2016 files only")
    print("2. Copy 2017 files only") 
    print("3. Copy both 2016 and 2017 files")
    print("4. Cancel")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        copy_mseed_files([2016])
    elif choice == "2":
        copy_mseed_files([2017])
    elif choice == "3":
        copy_mseed_files([2016, 2017])
    elif choice == "4":
        print("Operation cancelled.")
    else:
        print("Invalid choice. Operation cancelled.") 