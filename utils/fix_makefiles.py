#!/usr/bin/env python3
"""
Script to fix HypoDD Makefiles to use gfortran instead of g77
"""
import os
import glob

def fix_makefiles(working_dir):
    """
    Fix all Makefiles in the hypodd_src directory to use gfortran instead of g77
    """
    hypodd_src = os.path.join(working_dir, "hypodd_src")
    
    if not os.path.exists(hypodd_src):
        print(f"Directory {hypodd_src} does not exist yet. Run this after extraction.")
        return
    
    # Find all Makefiles
    makefiles = glob.glob(os.path.join(hypodd_src, "**", "Makefile"), recursive=True)
    
    print(f"Found {len(makefiles)} Makefiles to fix:")
    
    for makefile in makefiles:
        print(f"  Fixing: {makefile}")
        
        # Read the Makefile
        with open(makefile, 'r') as f:
            content = f.read()
        
        # Replace g77 with gfortran
        if 'g77' in content:
            content = content.replace('FC\t= g77', 'FC\t= gfortran')
            content = content.replace('g77 -', 'gfortran -')
            content = content.replace('f77 -', 'gfortran -')
            
            # Write back the fixed Makefile
            with open(makefile, 'w') as f:
                f.write(content)
            
            print(f"    Fixed: {makefile}")
        else:
            print(f"    No g77 found in: {makefile}")

if __name__ == "__main__":
    fix_makefiles("hypodd_working") 