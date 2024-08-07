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
import socket

# API Key and Server Configuration
def get_config():
    return {
        'api_key': 'rgjdcvgm0a826723tesmchjz9f006785f4emp6r514d054e7xf3oukym060041a7',
        'api_secret': '66abc1bfd77c3ab09e0e2444',
        'server': 'https://www.hybrid-analysis.com'
    }

# Fetch API Key and Server
config = get_config()
API_KEY = config['api_key']
API_SECRET = config['api_secret']
SERVER = config['server']

# Get the input from the user
print("Please input the full path to the PDF file (including file extension): ")
PDF = input().strip()

# Wait for the user to press Enter to start the process
input("Press Enter to start the process...")

# Extract the content from the file
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
        response = requests.post(f'{SERVER}/v2/url/scan', headers=headers, data=data)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return f"Error: {response.status_code}, {response.text}"
    except requests.RequestException as e:
        return f"An error occurred: {e}"

# Test Hybrid Analysis endpoint
def test_hybrid_analysis_endpoint():
    test_url = 'http://example.com'
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    data = {
        'url': test_url
    }
    try:
        response = requests.post(f'{SERVER}/v2/url/scan', headers=headers, data=data)
        print(f"Hybrid Analysis test endpoint status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

# Check if a domain is resolvable
def check_domain_resolution(domain):
    try:
        ip = socket.gethostbyname(domain)
        print(f"Domain {domain} resolves to IP: {ip}")
        return True
    except socket.gaierror:
        print(f"Domain {domain} does not resolve.")
        return False

# Function to search for samples
def search_samples(query):
    url = f'{SERVER}/v2/search'
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    params = {
        'query': query
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code}, {response.text}"
    except requests.RequestException as e:
        return f"An error occurred: {e}"

# Function to get sample summary
def get_sample_summary(sample_id):
    url = f'{SERVER}/v2/sample/{sample_id}/summary'
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
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

# Check domain resolution for Hybrid Analysis API
if check_domain_resolution('www.hybrid-analysis.com'):
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

    # Example usage of search and summary functions
    search_query = 'similar-to:35047ad869607de0a52d54be5998f268c719bb655e168f9bff8356b1f1239c55'
    search_results = search_samples(search_query)
    print("Search Results:", search_results)

    sample_id = '01837d9b63b19d04125dfcce7941f7ac0e388f67b469ba8dea9c910d5cafe363'
    summary = get_sample_summary(sample_id)
    print("Sample Summary:", summary)
else:
    print("Skipping API checks due to domain resolution failure.")

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
    # Assuming data is the data you want to save
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
