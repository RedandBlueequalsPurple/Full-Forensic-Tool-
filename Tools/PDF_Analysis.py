import requests
import re
import fitz
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import whois

# API Key for Hybrid Analysis
API_KEY = 'yvtl3enod5f6cf1bu7b0jdmm47309335hzhtsqsrc85756f94sxvhltsf3427177'

# Get the input from the user
print("Please input the path to the PDF file: ")
PDF = input()

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
