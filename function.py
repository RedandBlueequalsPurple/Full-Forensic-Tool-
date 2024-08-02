import fitz
from pdfminer.high_level import extract_text
import pdfplumber
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.high_level import extract_text
import re
import requests
import whois

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

def whois_lookup(domain):
    try:
        domain_info = whois.whois(domain)
        return domain_info
    except Exception as e:
        return f"An error occurred: {e}"

def is_valid_url(url):
    """Simple URL validation"""
    import re
    pattern = re.compile(r'http[s]?://\S+')
    return pattern.match(url) is not None
