import requests
import xml.etree.ElementTree as ET
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
    logger.info("URL Analysis tool execution started.")
    try:
        # Tool logic here
        logger.debug("Executing URL Analysis tool logic.")
        # Example action
        logger.info("URL Analysis tool action completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("URL Analysis tool execution finished.")

# URL of the XML data
url = input()

# Fetch the data from the URL
response = requests.get(url)
if response.status_code != 200:
    print(f"Failed to retrieve data: {response.status_code}")
    exit(1)

# Parse the XML data
try:
    root = ET.fromstring(response.content)

    # Print the root element
    print(f"Root Element: {root.tag}")

    # Function to recursively print element metadata
    def print_element_metadata(element, indent=0):
        spacing = ' ' * indent
        print(f"{spacing}Element: {element.tag}, Attributes: {element.attrib}")

        # Example of handling specific elements
        if element.tag.endswith('NetworkSection'):
            print(f"{spacing}  Network Section:")
            for network in element.findall('.//{*}Network'):
                print(f"{spacing}    Network: {network.attrib}")

        if element.tag.endswith('DiskSection'):
            print(f"{spacing}  Disk Section:")
            for disk in element.findall('.//{*}Disk'):
                print(f"{spacing}    Disk: {disk.attrib}")

        for child in element:
            print_element_metadata(child, indent + 4)

    # Print metadata for all elements
    print_element_metadata(root)

except ET.ParseError as e:
    print(f"ParseError: {e}")
except Exception as e:
    print(f"Error: {e}")