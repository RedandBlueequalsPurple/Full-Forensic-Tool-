import os
import hashlib
import re
import vt
from pdfminer.high_level import extract_text
import fitz
from datetime import datetime
import json
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
    logger.info("PDF Analysis tool execution started.")
    try:
        # Tool logic here
        logger.debug("Executing PDF Analysis tool logic.")
        # Example action
        logger.info("PDF Analysis tool action completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("PDF Analysis tool execution finished.")

# Directory for saving JSON data
JSON_DIR = 'JSON'

# VirusTotal API Key
VT_API_KEY = '9bcb54f31badf1de44a5ea1b0f501f02a42ac46389133cf554b80409219dbdd8'

def main():
    # Get the input from the user
    print("Please input the full path to the PDF file (including file extension): ")
    PDF = input().strip()

    # Check if the file exists
    if not os.path.isfile(PDF):
        print(f"The file '{PDF}' does not exist. Please check the path and try again.")
        return  # Exit the function if the file doesn't exist

    # Wait for the user to press Enter to start the process
    input("Press Enter to start the process...")

    # Extract the content from the file
    text = extract_text_from_pdf(PDF)
    line_count = count_lines_in_pdf(PDF)
    metadata = get_pdf_metadata(PDF)
    urls = extract_urls_from_pdf(PDF)

    # Print the content and metadata of the PDF
    print(text, line_count)
    if metadata is not None:
        for key, value in metadata.items():
            print(f"{key}: {value}")

    # Calculate file hash and check on VirusTotal
    file_hash = calculate_file_hash(PDF)
    if file_hash:
        print(f"File Hash: {file_hash}")
        check_file_hash_virustotal(file_hash)

    # Check URLs on VirusTotal
    for url in urls:
        check_url_virustotal(url)

    # Save the results to a JSON file
    result_data = {
        "text": text,
        "line_count": line_count,
        "metadata": metadata,
        "urls": urls,
        "hash": file_hash,
        "timestamp": get_current_datetime()
    }
    save_to_json(result_data, f"analysis_result_{get_current_datetime()}.json")


def extract_text_from_pdf(file_path):
    try:
        text = extract_text(file_path)
        return text
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def count_lines_in_pdf(file_path):
    try:
        pdf_document = fitz.open(file_path)
        line_count = 0
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            line_count += text.count('\n')
        pdf_document.close()
        return line_count
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_pdf_metadata(file_path):
    try:
        with fitz.open(file_path) as doc:
            metadata = doc.metadata
            return metadata
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extract_urls_from_pdf(file_path):
    urls = []
    try:
        text = extract_text(file_path)
        urls = re.findall(r'http[s]?://\S+', text)
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return urls

def calculate_file_hash(file_path):
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def check_file_hash_virustotal(file_hash):
    client = vt.Client(VT_API_KEY)
    try:
        file = client.get_object(f"/files/{file_hash}")
        name = file.get("meaningful_name", "N/A")
        scan_date = file.get("last_analysis_date", "N/A")
        last_analysis_stats = file.get("last_analysis_stats", {})
        malicious = last_analysis_stats.get('malicious', 0)
        total = sum(last_analysis_stats.values())

        print(f"File: {name}")
        print(f"Scan Date: {scan_date}")
        print(f"Malicious: {malicious}")
        print(f"Total Scans: {total}")
    except vt.error.APIError as e:
        if e.code == 'NotFoundError':
            print(f"File with hash '{file_hash}' not found in VirusTotal.")
        else:
            print(f"API error occurred: {e}")
    except Exception as e:
        print(f"Error checking file hash: {e}")
    finally:
        client.close()

def check_url_virustotal(url):
    client = vt.Client(VT_API_KEY)
    try:
        url_id = vt.url_id(url)
        url_obj = client.get_object(f"/urls/{url_id}")
        last_analysis_stats = url_obj.get("last_analysis_stats", {})
        malicious = last_analysis_stats.get('malicious', 0)
        total = sum(last_analysis_stats.values())

        print(f"URL: {url}")
        print(f"Malicious: {malicious}")
        print(f"Total Scans: {total}")
    except vt.error.APIError as e:
        if e.code == 'NotFoundError':
            print(f"URL '{url}' not found in VirusTotal.")
        else:
            print(f"API error occurred: {e}")
    except Exception as e:
        print(f"Error checking URL: {e}")
    finally:
        client.close()

def save_to_json(data, filename):
    os.makedirs(JSON_DIR, exist_ok=True)
    json_file_path = os.path.join(JSON_DIR, filename)
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data has been saved to {json_file_path}")

def get_current_datetime():
    now = datetime.now()
    return now.strftime('%Y%m%d_%H%M%S')

if __name__ == "__main__":
    main()
