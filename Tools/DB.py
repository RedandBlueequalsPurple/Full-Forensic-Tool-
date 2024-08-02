import json
import sys
import os

# Define directories and files
json_directory = 'JSON'
processed_files_path = 'processed_files.txt'

# Ensure the directories exist
if not os.path.exists(json_directory):
    os.makedirs(json_directory)

# In-memory data store
data_store = []

# Function to load JSON data
def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

# Function to get processed files
def get_processed_files():
    if os.path.isfile(processed_files_path):
        with open(processed_files_path, 'r') as file:
            return set(line.strip() for line in file)
    return set()

# Function to update processed files
def update_processed_files(file_list):
    with open(processed_files_path, 'a') as file:
        for file_name in file_list:
            file.write(f"{file_name}\n")

# Get the list of previously processed files
processed_files = get_processed_files()

# List all files in the JSON directory
json_files = [f for f in os.listdir(json_directory) if os.path.isfile(os.path.join(json_directory, f))]

# Determine new files
new_files = [f for f in json_files if f not in processed_files]

if not new_files:
    print("No new files to process.")
    sys.exit(0)

print(f"New files to process: {new_files}")

# Process new files
for json_file in new_files:
    file_path = os.path.join(json_directory, json_file)
    data = load_json(file_path)

    if 'file_hashes' not in data:
        print(f"File {json_file} does not contain 'file_hashes' key. Skipping.")
        continue

    hashes = data['file_hashes']
    required_fields = ['md5', 'sha1', 'sha256']
    if all(field in hashes for field in required_fields):
        data_store.append({
            'MD5': hashes['md5'],
            'SHA1': hashes['sha1'],
            'SHA256': hashes['sha256'],
            'source_file': json_file
        })
        print(f"Processed file: {json_file}")
    else:
        print(f"File {json_file} missing required fields. Skipping.")

update_processed_files(new_files)

# Function to query the data store
def query_data_store(query):
    results = []
    for entry in data_store:
        if query.lower() in entry['MD5'].lower() or query.lower() in entry['SHA1'].lower() or query.lower() in entry['SHA256'].lower():
            results.append(entry)
    return results

# Function to display all MD5 hashes with source files
def display_all_md5():
    if data_store:
        for entry in data_store:
            print(f"MD5: {entry['MD5']}, Source File: {entry['source_file']}")
    else:
        print("No data available.")

# Function to display all SHA1 hashes with source files
def display_all_sha1():
    if data_store:
        for entry in data_store:
            print(f"SHA1: {entry['SHA1']}, Source File: {entry['source_file']}")
    else:
        print("No data available.")

# Function to display all entries
def display_all_entries():
    if data_store:
        for entry in data_store:
            print(f"MD5: {entry['MD5']}, SHA1: {entry['SHA1']}, SHA256: {entry['SHA256']}, Source File: {entry['source_file']}")
    else:
        print("No data available.")

# Command loop for querying
def command_loop():
    print("Entering query mode. Type 'exit' to quit, 'show all' to display all entries, 'show md5' to display all MD5 hashes with source files, 'show sha1' to display all SHA1 hashes with source files.")
    while True:
        query = input("Enter command: ").strip()
        if query.lower() == 'exit':
            break
        elif query.lower() == 'show all':
            display_all_entries()
        elif query.lower() == 'show md5':
            display_all_md5()
        elif query.lower() == 'show sha1':
            display_all_sha1()    
        else:
            results = query_data_store(query)
            if results:
                for result in results:
                    print(f"MD5: {result['MD5']}, SHA1: {result['SHA1']}, SHA256: {result['SHA256']}, Source File: {result['source_file']}")
            else:
                print("No matching results found.")

# Start the command loop for querying
command_loop()
