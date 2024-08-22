import os
import hashlib
import re
import vt
from pdfminer.high_level import extract_text
import fitz
from datetime import datetime
import json
import logging

# Configure logging for event history
event_logger = logging.getLogger('event_logger')
event_logger.setLevel(logging.DEBUG)

# Avoid adding multiple handlers
if not event_logger.hasHandlers():
    event_handler = logging.FileHandler('event_history.log')
    event_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    event_handler.setFormatter(formatter)
    event_logger.addHandler(event_handler)

# Directory for saving JSON data
JSON_DIR = 'JSON'

# VirusTotal API Key
VT_API_KEY = '9bcb54f31badf1de44a5ea1b0f501f02a42ac46389133cf554b80409219dbdd8'

def main():
    """
    Main function to handle the PDF analysis process.
    """
    event_logger.info("PDF Analysis tool execution started.")
    try:
        # Get the input from the user
        event_logger.debug("Requesting PDF file path from user.")
        PDF = get_pdf_file_path()

        # Check if the file exists
        if not validate_file_exists(PDF):
            return

        # Extract the content from the file
        text = extract_text_from_pdf(PDF)
        line_count = count_lines_in_pdf(PDF)
        metadata = get_pdf_metadata(PDF)
        urls = extract_urls_from_pdf(PDF)

        # Print the content and metadata of the PDF
        print(text, line_count)
        if metadata:
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

        event_logger.info("PDF Analysis tool execution completed successfully.")
    except Exception as e:
        event_logger.error(f"An unexpected error occurred: {e}")
    finally:
        event_logger.info("PDF Analysis tool execution finished.")

def get_pdf_file_path():
    """
    Requests the PDF file path from the user.
    """
    try:
        print("Please input the full path to the PDF file (including file extension): ")
        PDF = input().strip()
        if not PDF:
            raise ValueError("File path cannot be empty.")
        return PDF
    except Exception as e:
        event_logger.error(f"Error requesting PDF file path: {e}")
        print(f"Error: {e}")
        return None

def validate_file_exists(file_path):
    """
    Validates if the provided file path exists.
    """
    if not os.path.isfile(file_path):
        error_message = f"The file '{file_path}' does not exist. Please check the path and try again."
        event_logger.error(error_message)
        print(error_message)
        return False
    return True

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.
    """
    try:
        text = extract_text(file_path)
        event_logger.debug(f"Extracted text from PDF: {file_path}")
        return text
    except FileNotFoundError:
        error_message = f"The file '{file_path}' does not exist."
        event_logger.error(error_message)
        print(error_message)
        return None
    except Exception as e:
        event_logger.error(f"An error occurred while extracting text: {e}")
        print(f"An error occurred: {e}")
        return None

def count_lines_in_pdf(file_path):
    """
    Counts the number of lines in a PDF file.
    """
    try:
        pdf_document = fitz.open(file_path)
        line_count = 0
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            line_count += text.count('\n')
        pdf_document.close()
        event_logger.debug(f"Counted {line_count} lines in PDF: {file_path}")
        return line_count
    except FileNotFoundError:
        error_message = f"The file '{file_path}' does not exist."
        event_logger.error(error_message)
        print(error_message)
        return None
    except Exception as e:
        event_logger.error(f"An error occurred while counting lines: {e}")
        print(f"An error occurred: {e}")
        return None

def get_pdf_metadata(file_path):
    """
    Retrieves metadata from a PDF file.
    """
    try:
        with fitz.open(file_path) as doc:
            metadata = doc.metadata
            event_logger.debug(f"Extracted metadata from PDF: {metadata}")
            return metadata
    except FileNotFoundError:
        error_message = f"The file '{file_path}' does not exist."
        event_logger.error(error_message)
        print(error_message)
        return None
    except Exception as e:
        event_logger.error(f"An error occurred while extracting metadata: {e}")
        print(f"An error occurred: {e}")
        return None

def extract_urls_from_pdf(file_path):
    """
    Extracts URLs from the text content of a PDF file.
    """
    urls = []
    try:
        text = extract_text(file_path)
        urls = re.findall(r'http[s]?://\S+', text)
        event_logger.debug(f"Extracted URLs from PDF: {urls}")
    except FileNotFoundError:
        error_message = f"The file '{file_path}' does not exist."
        event_logger.error(error_message)
        print(error_message)
    except Exception as e:
        event_logger.error(f"An error occurred while extracting URLs: {e}")
        print(f"An error occurred: {e}")
    
    return urls

def calculate_file_hash(file_path):
    """
    Calculates the SHA-256 hash of a file.
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        event_logger.debug(f"Calculated SHA-256 hash for the file: {file_hash}")
        return file_hash
    except FileNotFoundError:
        error_message = f"The file '{file_path}' does not exist."
        event_logger.error(error_message)
        print(error_message)
        return None
    except Exception as e:
        event_logger.error(f"An error occurred while calculating file hash: {e}")
        print(f"An error occurred: {e}")
        return None

def check_file_hash_virustotal(file_hash):
    """
    Checks the file hash on VirusTotal.
    """
    client = vt.Client(VT_API_KEY)
    try:
        file = client.get_object(f"/files/{file_hash}")
        name = file.get("meaningful_name", "N/A")
        scan_date = file.get("last_analysis_date", "N/A")
        last_analysis_stats = file.get("last_analysis_stats", {})
        malicious = last_analysis_stats.get('malicious', 0)
        total = sum(last_analysis_stats.values())

        event_logger.debug(f"VirusTotal file scan - Name: {name}, Date: {scan_date}, Malicious: {malicious}, Total: {total}")
        print(f"File: {name}")
        print(f"Scan Date: {scan_date}")
        print(f"Malicious: {malicious}")
        print(f"Total Scans: {total}")
    except vt.error.APIError as e:
        if e.code == 'NotFoundError':
            error_message = f"File with hash '{file_hash}' not found in VirusTotal."
            event_logger.error(error_message)
            print(error_message)
        else:
            event_logger.error(f"API error occurred: {e}")
            print(f"API error occurred: {e}")
    except Exception as e:
        event_logger.error(f"Error checking file hash: {e}")
        print(f"Error checking file hash: {e}")
    finally:
        client.close()

def check_url_virustotal(url):
    """
    Checks a URL on VirusTotal.
    """
    client = vt.Client(VT_API_KEY)
    try:
        url_obj = client.get_object(f"/urls/{url}")
        scan_date = url_obj.get("last_analysis_date", "N/A")
        last_analysis_stats = url_obj.get("last_analysis_stats", {})
        malicious = last_analysis_stats.get('malicious', 0)
        total = sum(last_analysis_stats.values())

        event_logger.debug(f"VirusTotal URL scan - URL: {url}, Date: {scan_date}, Malicious: {malicious}, Total: {total}")
        print(f"URL: {url}")
        print(f"Scan Date: {scan_date}")
        print(f"Malicious: {malicious}")
        print(f"Total Scans: {total}")
    except vt.error.APIError as e:
        event_logger.error(f"API error occurred: {e}")
        print(f"API error occurred: {e}")
    except Exception as e:
        event_logger.error(f"Error checking URL: {e}")
        print(f"Error checking URL: {e}")
    finally:
        client.close()

def save_to_json(data, filename):
    """
    Saves data to a JSON file.
    """
    try:
        if not os.path.exists(JSON_DIR):
            os.makedirs(JSON_DIR)
        
        file_path = os.path.join(JSON_DIR, filename)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        event_logger.debug(f"Saved analysis results to JSON file: {file_path}")
    except Exception as e:
        event_logger.error(f"Error saving data to JSON file: {e}")

def get_current_datetime():
    """
    Returns the current date and time as a string.
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

if __name__ == "__main__":
    main()
