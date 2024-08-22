import pycdlib
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def main():
    logger.info("ISO Analysis tool execution started.")
    try:
        # Tool logic here
        logger.debug("Executing ISO Analysis tool logic.")
        # Example action
        logger.info("ISO Analysis tool action completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("ISO Analysis tool execution finished.")

# Function to extract all files from ISO
def extract_all_from_iso(iso_path, extract_path):
    iso = pycdlib.PyCdlib()
    iso.open(iso_path)
    
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    def extract_dir(dir_path, extract_to):
        try:
            children = iso.list_children(iso_path=dir_path)
            for child in children:
                child_name = child.file_identifier().decode('utf-8').strip()
                child_path = os.path.join(dir_path, child_name).replace('\\', '/')
                
                # Check if path length exceeds a reasonable limit
                if len(child_path) > 255:
                    print(f"Skipping path due to length: {child_path}")
                    continue

                if child.is_dir():
                    new_extract_to = os.path.join(extract_to, os.path.basename(child_path))
                    if not os.path.exists(new_extract_to):
                        os.makedirs(new_extract_to, exist_ok=True)
                    extract_dir(child_path, new_extract_to)
                else:
                    destination_path = os.path.join(extract_to, os.path.basename(child_path))
                    try:
                        with open(destination_path, 'wb') as f:
                            iso.get_file_from_iso(child_path, f)
                    except Exception as e:
                        print(f"Error writing file {destination_path}: {e}")
        except Exception as e:
            print(f"An error occurred while processing {dir_path}: {e}")

    extract_dir('/', extract_path)
    
    iso.close()

# Function to parse XML file and extract metadata
def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        print(f"Metadata from {file_path}:")
        for child in root:
            print(child.tag, child.attrib)
    except ET.ParseError as e:
        print(f"ParseError: {e}")
    except FileNotFoundError:
        print("The file was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Please enter the file path to the ISO Image:")
    iso_file_path = input().strip()

    if not os.path.isfile(iso_file_path):
        print(f"The file {iso_file_path} does not exist.")
        return

    # Create extraction directory on Desktop
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    base_extract_dir = os.path.join(desktop_dir, "ISO_Analysis")
    os.makedirs(base_extract_dir, exist_ok=True)

    # Create a timestamped directory inside the base extraction directory
    iso_file_name = os.path.splitext(os.path.basename(iso_file_path))[0]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    extract_dir = os.path.join(base_extract_dir, f"{iso_file_name}_{timestamp}")
    os.makedirs(extract_dir, exist_ok=True)

    # Extract all files from the ISO
    extract_all_from_iso(iso_file_path, extract_dir)

    # Check for XML files and parse them
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.endswith(".xml"):
                xml_file_path = os.path.join(root, file)
                parse_xml(xml_file_path)

if __name__ == "__main__":
    main()
