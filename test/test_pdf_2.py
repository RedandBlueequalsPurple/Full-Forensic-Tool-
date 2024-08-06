import requests
import re
import fitz
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import whois
import os
import json
from datetime import datetime

# API Key for Hybrid Analysis
API_KEY = 'yvtl3enod5f6cf1bu7b0jdmm47309335hzhtsqsrc85756f94sxvhltsf3427177'

# Get the input from the user
print("Please input the path to the PDF file: ")
PDF = input()

# Wait for the user to press Enter to start the process
input("Press Enter to start the process...")

# Extract the content from the file
def extract_text_from_pdf(file_path):
    text = extract_text(file_path)
    return text

# Get the number of lines from the file
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

# Get the metadata from the PDF
def get_pdf_metadata(file_path):
    try:
        with open(file_path, 'rb') as file:
            parser = PDFParser(file)
            document = PDFDocument(parser)
            metadata = document.info[0]
            # Convert bytes to strings in metadata
            metadata = {key: (value.decode('utf-8', errors='ignore') if isinstance(value, bytes) else value) for key, value in metadata.items()}
            return metadata
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Extract URLs from the PDF
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

# Check the status of a URL
def check_url_status(url):
    try:
        response = requests.get(url)
        status_code = response.status_code
        if status_code == 200:
            return "URL is reachable and returned status 200 OK"
        else:
            return f"URL returned status code: {status_code}"
    except requests.RequestException as e:
        return f"An error occurred: {e}"

# WHOIS lookup for a domain
def whois_lookup(domain):
    try:
        domain_info = whois.whois(domain)
        return domain_info
    except Exception as e:
        return f"An error occurred: {e}"

# Simple URL validation
def is_valid_url(url):
    pattern = re.compile(r'http[s]?://\S+')
    return pattern.match(url) is not None

# Hybrid Analysis URL check
def check_url_hybrid_analysis(url):
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    data = {
        'url': url
    }
    try:
        response = requests.post('https://api.hybrid-analysis.com/v2/url/scan', headers=headers, data=data)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return f"Error: {response.status_code}, {response.text}"
    except requests.RequestException as e:
        return f"An error occurred: {e}"

# Main logic
text = extract_text_from_pdf(PDF)
line_count = count_lines_in_pdf(PDF)
metadata = get_pdf_metadata(PDF)
urls = extract_urls_from_pdf(PDF)

# Print the content and metadata of the PDF
print(text, line_count)
if metadata is not None:
    for key, value in metadata.items():
        print(f"{key}: {value}")

# Check URL status and Hybrid Analysis
for url in urls:
    if is_valid_url(url):
        status = check_url_status(url)
        print(f"Status of {url}: {status}")
        result = check_url_hybrid_analysis(url)
        print(f"Hybrid Analysis result for {url}: {result}")
    else:
        print(f"{url} is not a valid URL")

# WHOIS lookup
for url in urls:
    if is_valid_url(url):
        domain_info = whois_lookup(url)
        print(f"WHOIS info for {url}: {domain_info}")

def save_to_json(data, filename):
    """
    Save data to a JSON file.
    
    :param data: The data to save.
    :param filename: The name of the file to save the data to.
    """
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data has been saved to {filename}")

def get_current_datetime():
    """
    Get the current date and time formatted as YYYYMMDD_HHMMSS.
    """
    now = datetime.now()
    return now.strftime('%Y%m%d_%H%M%S')

def main():
    # Assuming `data` is the data you want to save
    data = {
        'text': text,
        'line_count': line_count,
        'metadata': metadata,
        'urls': urls
        # your data structure
    }
    
    print("Prompting for user input...")
    save_as_json = input("Do you want to save the data as JSON? (yes/no): ").strip().lower()
    print(f"User input: {save_as_json}")
    
    if save_as_json == 'yes':
        # Define the JSON output directory
        json_output_dir = os.path.join('JSON')
        os.makedirs(json_output_dir, exist_ok=True)
        
        # Define the JSON file name
        base_filename = os.path.basename(PDF)
        base_name, _ = os.path.splitext(base_filename)
        current_datetime = get_current_datetime()
        json_filename = os.path.join(json_output_dir, f'{base_name}_{current_datetime}.json')
        
        # Save the data to JSON
        save_to_json(data, json_filename)
    else:
        print("Data was not saved as JSON.")

if __name__ == "__main__":
    main()
