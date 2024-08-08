import fitz  # PyMuPDF
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import json
from datetime import datetime
import os
import base64

def extract_pdf_data(pdf_path):
    data = {
        "text": "",
        "images": [],
        "metadata": {},
        "pdfminer_text": ""
    }
    
    # Extract text and images using PyMuPDF
    pdf_document = fitz.open(pdf_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Extract text
        data["text"] += page.get_text()

        # Extract images
        image_list = page.get_images(full=True)
        for img_index, image in enumerate(image_list):
            xref = image[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            data["images"].append(image_bytes)
    
    # Extract metadata using PyMuPDF
    data["metadata"] = pdf_document.metadata
    
    # Extract text using PyPDF2 (PdfReader)
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        pdf2_text = ""
        for page in reader.pages:
            pdf2_text += page.extract_text()
        data["text"] += pdf2_text  # Append PyPDF2 text to the existing text

        # Extract metadata using PyPDF2
        pdf2_metadata = reader.metadata
        data["metadata"].update({
            "pdf2_" + k: v for k, v in pdf2_metadata.items()
        })
    
    # Extract text and metadata using pdfminer.six
    data["pdfminer_text"] = extract_text(pdf_path)
    
    with open(pdf_path, "rb") as file:
        parser = PDFParser(file)
        document = PDFDocument(parser)
        pdfminer_metadata = document.info[0]
        data["metadata"].update({
            "pdfminer_" + k: v for k, v in pdfminer_metadata.items()
        })
    
    return data

def export_to_json(data, pdf_path):
    # Convert image bytes to base64 strings
    if "images" in data:
        data["images"] = [base64.b64encode(img).decode('utf-8') for img in data["images"]]
    
    # Create the JSON directory if it does not exist
    json_dir = "JSON"
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    
    # Generate filename with PDF name and current date
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json_filename = os.path.join(json_dir, f"{base_name}_{date_str}.json")
    
    # Export data to JSON file
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Data exported to {json_filename}")

def main():
    # Prompt user for the file path
    pdf_path = input("Please enter the path to the PDF file: ")
    
    # Prompt to press Enter to continue
    input("Press Enter to continue...")
    
    # Extract data from the specified PDF file
    pdf_data = extract_pdf_data(pdf_path)
    
    # Display results
    print("Text extracted:")
    print(pdf_data["text"])

    print("\nNumber of images extracted:", len(pdf_data["images"]))

    print("\nMetadata extracted:")
    for key, value in pdf_data["metadata"].items():
        print(f"{key}: {value}")

    print("\nText extracted by pdfminer:")
    print(pdf_data["pdfminer_text"])
    
    # Ask user if they want to export data to JSON
    export_option = input("\nWould you like to export the data to a JSON file? (yes/no): ").strip().lower()
    if export_option == 'yes':
        export_to_json(pdf_data, pdf_path)

if __name__ == "__main__":
    main()
