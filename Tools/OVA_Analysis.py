import os
import tarfile
import xml.etree.ElementTree as ET
import json
import subprocess
import hashlib
from datetime import datetime
from tqdm import tqdm
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')  # Use the same log file
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def main():
    logger.info("OVA Analysis tool execution started.")
    try:
        # Tool logic here
        logger.debug("Executing OVA Analysis tool logic.")
        # Example action
        logger.info("OVA Analysis tool action completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("OVA Analysis tool execution finished.")

def element_to_dict(element):
    """Recursively convert an XML element to a dictionary."""
    return {
        "tag": element.tag,
        "attrib": element.attrib,
        "children": [element_to_dict(child) for child in element]
    }

def print_element_metadata(element, indent=0):
    """Recursively print XML element metadata."""
    spacing = ' ' * indent
    print(f"{spacing}Element: {element.tag}, Attributes: {element.attrib}")
    for child in element:
        print_element_metadata(child, indent + 4)

def calculate_hashes(file_path):
    """Calculate and return the MD5, SHA1, and SHA256 hashes of a file."""
    hashes = {
        "md5": hashlib.md5(),
        "sha1": hashlib.sha1(),
        "sha256": hashlib.sha256()
    }

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            for algo in hashes.values():
                algo.update(chunk)

    return {name: algo.hexdigest() for name, algo in hashes.items()}

# Take user input for the ISO file path
print("Please enter the file path to the OVA Image:")
FilePath = input().strip()

# Check if the file exists
if not os.path.isfile(FilePath):
    print(f"The file path {FilePath} does not exist.")
    exit(1)

# Directory to extract the OVA file
extractDir = "extracted_ova"
os.makedirs(extractDir, exist_ok=True)

# Extract the OVA file with a progress bar
with tarfile.open(FilePath, 'r') as tar:
    members = tar.getmembers()
    total_members = len(members)
    next_print_percentage = 10
    
    for i, member in enumerate(tqdm(members, desc="Extracting OVA")):
        tar.extract(member, path=extractDir)
        current_percentage = (i + 1) * 100 / total_members
        if current_percentage >= next_print_percentage:
            print(f"Extraction progress: {int(current_percentage)}%")
            next_print_percentage += 10

# Locate the OVF file in the extracted directory
OvfFilePath = None
for root, dirs, files in os.walk(extractDir):
    for file in files:
        if file.endswith('.ovf'):
            OvfFilePath = os.path.join(root, file)
            break

if OvfFilePath is None:
    print("No OVF file found in the extracted OVA.")
    exit(1)

# Create the JSON directory if it doesn't exist
jsonDir = "JSON"
os.makedirs(jsonDir, exist_ok=True)

# Generate a timestamp for the JSON file name
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Extract file name without extension from OVF file path
file_name_without_extension = os.path.splitext(os.path.basename(OvfFilePath))[0]

# Construct JSON file name
jsonFileName = f"{file_name_without_extension}_{timestamp}.json"
jsonFilePath = os.path.join(jsonDir, jsonFileName)

# Loop until a valid choice is made
while True:
    print("Choose an option:")
    print("1. Print metadata")
    print("2. Convert metadata to JSON and send to another script")

    choice = input().strip()

    if choice == "1" or choice == "2":
        break
    else:
        print("Invalid choice. Please enter 1 or 2.")

try:
    tree = ET.parse(OvfFilePath)
    root = tree.getroot()

    # Calculate file hashes
    file_hashes = calculate_hashes(OvfFilePath)

    # Prepare metadata
    metadata = {
        "xml_metadata": element_to_dict(root),
        "file_hashes": file_hashes
    }

    if choice == "1":
        # Print metadata for all elements
        print_element_metadata(root)
        # Print hashes
        print("File Hashes:")
        for algo, hash_value in file_hashes.items():
            print(f"{algo.upper()}: {hash_value}")
    elif choice == "2":
        # Convert the dictionary to JSON
        metadata_json = json.dumps(metadata, indent=4)

        # Print JSON data
        print(metadata_json)

        # Write JSON data to a file in the JSON directory
        with open(jsonFilePath, 'w') as json_file:
            json_file.write(metadata_json)

        # Use absolute path or handle spaces in the path
        script_path = os.path.join("/Users/mymac/Desktop/VS /python/Full Forensic Tool", "OVA_DB_AFTER_ANALYSIS.py")
        
        # Debugging: Print the script path
        print(f"Script path: {script_path}")
        print(f"JSON file path: {jsonFilePath}")
        
        # Properly handle spaces in the script path
        subprocess.run(["python3", script_path, jsonFilePath], check=True)
except ET.ParseError as e:
    print(f"ParseError: {e}")
except Exception as e:
    print(f"Error: {e}")
