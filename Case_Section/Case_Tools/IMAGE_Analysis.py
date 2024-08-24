from PIL import Image
import png
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import subprocess
import json
import os
import base64
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(filename='event_history.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_pillow_data(file_path):
    logging.info(f"Extracting Pillow data from {file_path}")
    img = Image.open(file_path)
    pillow_data = {
        "Format": img.format,
        "Size": img.size,
        "Mode": img.mode,
        "Info": img.info
    }
    return pillow_data

def extract_jpg_data(file_path):
    logging.info(f"Extracting JPG data from {file_path}")
    img = Image.open(file_path)
    pixels = list(img.getdata())
    jpg_data = {
        "Width": img.width,
        "Height": img.height,
        "First 10 Pixels": pixels[:10]
    }
    return jpg_data

def extract_pypng_data(file_path):
    logging.info(f"Extracting PNG data from {file_path}")
    try:
        reader = png.Reader(filename=file_path)
        width, height, pixels, metadata = reader.read_flat()
        pypng_data = {
            "Width": width,
            "Height": height,
            "Metadata": metadata,
            "First 10 Pixels": list(pixels[:10])
        }
    except png.FormatError as e:
        pypng_data = {"Error": f"Error reading PNG file with pypng: {e}"}
        logging.error(f"Error reading PNG file with pypng: {e}")
    return pypng_data

def extract_hachoir_data(file_path):
    logging.info(f"Extracting Hachoir data from {file_path}")
    parser = createParser(file_path)
    if not parser:
        logging.error("Unable to parse file with hachoir.")
        return {"Error": "Unable to parse file with hachoir."}

    metadata = extractMetadata(parser)
    hachoir_data = {}

    if metadata:
        for item in metadata.exportPlaintext():
            if ": " in item:
                key, value = item.split(": ", 1)
                hachoir_data[key] = value
            else:
                hachoir_data[item] = "N/A"  # Handle items without the delimiter
    else:
        hachoir_data = {"Error": "No metadata found with hachoir."}
    
    return hachoir_data

def extract_geolocation(file_path):
    logging.info(f"Extracting geolocation data from {file_path}")
    result = subprocess.run(["exiftool", file_path], capture_output=True, text=True)
    lines = result.stdout.splitlines()

    gps_data = {}
    for line in lines:
        if "GPS" in line:
            key, value = line.split(":", 1)
            gps_data[key.strip()] = value.strip()

    if not gps_data:
        logging.warning("No geolocation data found.")
    return gps_data if gps_data else {"Error": "No geolocation data found."}

def extract_exiftool_data(file_path):
    logging.info(f"Extracting ExifTool data from {file_path}")
    result = subprocess.run(["exiftool", file_path], capture_output=True, text=True)
    exif_data = {}
    lines = result.stdout.splitlines()
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            exif_data[key.strip()] = value.strip()
    return exif_data

def analyze_file(file_path):
    logging.info(f"Analyzing file {file_path}")
    data = {
        "Pillow Data": extract_pillow_data(file_path),
        "Hachoir Data": extract_hachoir_data(file_path),
        "ExifTool Data": extract_exiftool_data(file_path),
        "Geolocation Data": extract_geolocation(file_path),
    }
    
    if file_path.lower().endswith('.png'):
        data["pypng Data"] = extract_pypng_data(file_path)
    elif file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
        data["JPG Data"] = extract_jpg_data(file_path)
    
    return data

def save_to_json(file_path, data):
    def convert_bytes(obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    base_name = os.path.basename(file_path)
    file_name = os.path.splitext(base_name)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"{file_name}_{timestamp}.json"
    json_dir = "JSON"
    os.makedirs(json_dir, exist_ok=True)
    json_path = os.path.join(json_dir, json_filename)

    try:
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=4, default=convert_bytes)
        logging.info(f"Data saved to {json_path}")
    except Exception as e:
        logging.error(f"Failed to save data to JSON: {e}")

def main():
    file_path = input("Enter the path to the image file (PNG or JPG): ")  # Prompt user for file path
    data = analyze_file(file_path)
    
    option = input("Do you want to save the data in a JSON file or display it? (Enter 'json' to save or 'display' to display): ").strip().lower()

    if option == 'json':
        save_to_json(file_path, data)
    elif option == 'display':
        print(json.dumps(data, indent=4, default=lambda obj: base64.b64encode(obj).decode('utf-8') if isinstance(obj, bytes) else str(obj)))
    else:
        print("Invalid option. Exiting.")
        logging.warning("Invalid option selected.")

if __name__ == "__main__":
    main()
