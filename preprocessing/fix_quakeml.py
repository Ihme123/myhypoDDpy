#!/usr/bin/env python3
"""
Script to fix QuakeML file by removing namespace prefixes
"""
import re
from pathlib import Path

# Базовый путь относительно расположения скрипта
BASE_PATH = Path(__file__).parent.parent / "example_data"

def fix_quakeml(input_file, output_file):
    """
    Fix QuakeML file by removing namespace prefixes
    """
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Remove namespace prefixes (handle both ns0: and q:)
    content = re.sub(r'ns0:', '', content)
    content = re.sub(r'q:', '', content)
    content = re.sub(r'xmlns:ns0="[^"]*"', 'xmlns="http://quakeml.org/xmlns/quakeml/1.2"', content)
    content = re.sub(r'xmlns:q="[^"]*"', 'xmlns="http://quakeml.org/xmlns/quakeml/1.2"', content)
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Fixed QuakeML file saved as: {output_file}")

if __name__ == "__main__":
    fix_quakeml(BASE_PATH / "events.xml", BASE_PATH / "events_fixed.xml") 