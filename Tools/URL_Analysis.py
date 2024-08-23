import requests
import xml.etree.ElementTree as ET
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def fetch_data_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve data: {response.status_code}")
            exit(1)
        logger.info(f"Successfully retrieved data from URL: {url}")
        return response.content
    except requests.RequestException as e:
        logger.error(f"RequestException: {e}")
        exit(1)

def parse_xml_data(xml_content):
    try:
        root = ET.fromstring(xml_content)
        logger.info(f"Successfully parsed XML data. Root Element: {root.tag}")
        return root
    except ET.ParseError as e:
        logger.error(f"ParseError: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)

def print_element_metadata(element, indent=0):
    spacing = ' ' * indent
    logger.info(f"{spacing}Element: {element.tag}, Attributes: {element.attrib}")

    # Example of handling specific elements
    if element.tag.endswith('NetworkSection'):
        logger.info(f"{spacing}  Network Section:")
        for network in element.findall('.//{*}Network'):
            logger.info(f"{spacing}    Network: {network.attrib}")

    if element.tag.endswith('DiskSection'):
        logger.info(f"{spacing}  Disk Section:")
        for disk in element.findall('.//{*}Disk'):
            logger.info(f"{spacing}    Disk: {disk.attrib}")

    for child in element:
        print_element_metadata(child, indent + 4)

def main():
    logger.info("URL Analysis tool execution started.")
    try:
        # URL input
        url = input("Enter the URL of the XML data: ").strip()

        # Fetch data from URL
        xml_content = fetch_data_from_url(url)

        # Parse XML data
        root = parse_xml_data(xml_content)

        # Print metadata for all elements
        print_element_metadata(root)

        logger.info("URL Analysis tool action completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("URL Analysis tool execution finished.")

if __name__ == "__main__":
    main()
