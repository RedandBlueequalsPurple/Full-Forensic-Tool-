import json
import os
from prettytable import PrettyTable

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
        return None
    except IOError as e:
        print(f"Error reading file: {e}")
        return None

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

# Function to process new files
def process_new_files():
    global data_store
    processed_files = get_processed_files()

    # List all files in the JSON directory
    json_files = [f for f in os.listdir(json_directory) if os.path.isfile(os.path.join(json_directory, f))]

    # Determine new files
    new_files = [f for f in json_files if f not in processed_files]

    if not new_files:
        print("No new files to process.")
        return

    print(f"New files to process: {new_files}")

    # Process new files
    for json_file in new_files:
        file_path = os.path.join(json_directory, json_file)
        data = load_json(file_path)

        if data is None:
            print(f"Skipping file {json_file} due to loading error.")
            continue

        # Process hardware specifications
        if 'Hardware Specifications' in data:
            hardware_specs = data['Hardware Specifications']
            entry = {
                'RAMSize': hardware_specs.get('RAMSize', ''),
                'VRAMSize': hardware_specs.get('VRAMSize', ''),
                'screens': hardware_specs.get('screens', ''),
                'file': hardware_specs.get('file', ''),
                'fps': hardware_specs.get('fps', ''),
                'type': ', '.join(hardware_specs.get('type', [])),
                'slot': hardware_specs.get('slot', ''),
                'cable': hardware_specs.get('cable', ''),
                'driver': hardware_specs.get('driver', ''),
                'enabledIn': hardware_specs.get('enabledIn', ''),
                'timestamp': hardware_specs.get('timestamp', ''),
                'flags': hardware_specs.get('flags', ''),
                'PortCount': hardware_specs.get('PortCount', ''),
                'useHostIOCache': hardware_specs.get('useHostIOCache', ''),
                'Bootable': hardware_specs.get('Bootable', ''),
                'IDE0MasterEmulationPort': hardware_specs.get('IDE0MasterEmulationPort', ''),
                'IDE0SlaveEmulationPort': hardware_specs.get('IDE0SlaveEmulationPort', ''),
                'IDE1MasterEmulationPort': hardware_specs.get('IDE1MasterEmulationPort', ''),
                'IDE1SlaveEmulationPort': hardware_specs.get('IDE1SlaveEmulationPort', ''),
                'hotpluggable': hardware_specs.get('hotpluggable', ''),
                'port': ', '.join(hardware_specs.get('port', [])),
                'device': hardware_specs.get('device', ''),
                'passthrough': hardware_specs.get('passthrough', ''),
                'source_file': json_file 
            }
            data_store.append(entry)
            print(f"Processed hardware specifications from file: {json_file}")
            print(entry)

        # Process hashes
        if 'file_hashes' in data:
            hashes = data['file_hashes']
            entry = {
                'MD5': hashes.get('md5', ''),
                'SHA1': hashes.get('sha1', ''),
                'SHA256': hashes.get('sha256', ''),
                'source_file': json_file
            }
            data_store.append(entry)
            print(f"Processed file hashes from file: {json_file}")
            print(entry)

    update_processed_files(new_files)

# Function to query the data store
def query_data_store(query):
    results = []
    for entry in data_store:
        if any(query.lower() in str(value).lower() for value in entry.values()):
            results.append(entry)
    return results

# Function to create a PrettyTable with separators after each row
def create_pretty_table_with_separators(field_names, rows):
    table = PrettyTable()
    table.field_names = field_names
    table.align = "l"  # Align text to the left

    if rows:
        for row in rows:
            table.add_row(row)
            table.add_row(["-" * (len(field) + 2) for field in field_names])

        # Convert table to string and add full-width separators
        table_str = table.get_string()
        lines = table_str.split('\n')
        full_width_separator = "+" + "+".join("-" * (len(field) + 2) for field in field_names) + "+"

        new_lines = []
        for line in lines:
            new_lines.append(line)
            if line.startswith("+") and not line.endswith("+"):
                new_lines.append(full_width_separator)

        # Remove the extra last separator line
        if new_lines[-1] == full_width_separator:
            new_lines = new_lines[:-1]

        return '\n'.join(new_lines)
    else:
        return PrettyTable(field_names).get_string()

# Function to display all entries with all keys
def display_all_entries_with_all_keys():
    if data_store:
        all_keys = get_all_keys()
        field_names = ["MD5", "SHA1", "SHA256", "Source File"] + list(all_keys)
        rows = [[entry.get('MD5', ''), entry.get('SHA1', ''), entry.get('SHA256', ''), entry.get('source_file', '')] + [entry.get(key, '') for key in all_keys] for entry in data_store]
        table_str = create_pretty_table_with_separators(field_names, rows)
        print(table_str)
    else:
        print("No data available.")

# Function to get all keys
def get_all_keys():
    if data_store:
        return set(key for entry in data_store for key in entry.keys() if key not in ['MD5', 'SHA1', 'SHA256', 'source_file'])
    return []

# Display specific data
def display_all_md5():
    display_specific_data('MD5')

def display_all_sha1():
    display_specific_data('SHA1')

def display_all_sha256():
    display_specific_data('SHA256')

def display_all_tag():
    display_specific_data('tag')

def display_all_value():
    display_specific_data('value')

def display_all_enabled():
    display_specific_data('enabled')

# Helper function to display specific data
def display_specific_data(field_name):
    if data_store:
        field_names = [field_name, "Source File"]
        rows = [[entry.get(field_name, ''), entry.get('source_file', '')] for entry in data_store if field_name in entry]
        table_str = create_pretty_table_with_separators(field_names, rows)
        print(table_str)
    else:
        print("No data available.")

# Functions to display hardware specification keys
def display_ram_size():
    display_specific_data('RAMSize')

def display_vram_size():
    display_specific_data('VRAMSize')

def display_screens():
    display_specific_data('screens')

def display_file():
    display_specific_data('file')

def display_fps():
    display_specific_data('fps')

def display_type():
    display_specific_data('type')

def display_slot():
    display_specific_data('slot')

def display_cable():
    display_specific_data('cable')

def display_driver():
    display_specific_data('driver')

def display_enabled_in():
    display_specific_data('enabledIn')

def display_timestamp():
    display_specific_data('timestamp')

def display_flags():
    display_specific_data('flags')

def display_port_count():
    display_specific_data('PortCount')

def display_use_host_io_cache():
    display_specific_data('useHostIOCache')

def display_bootable():
    display_specific_data('Bootable')

def display_ide0_master_emulation_port():
    display_specific_data('IDE0MasterEmulationPort')

def display_ide0_slave_emulation_port():
    display_specific_data('IDE0SlaveEmulationPort')

def display_ide1_master_emulation_port():
    display_specific_data('IDE1MasterEmulationPort')

def display_ide1_slave_emulation_port():
    display_specific_data('IDE1SlaveEmulationPort')

def display_hotpluggable():
    display_specific_data('hotpluggable')

def display_port():
    display_specific_data('port')

def display_device():
    display_specific_data('device')

def display_passthrough():
    display_specific_data('passthrough')

if __name__ == "__main__":
    process_new_files()



def command_loop():
    print("Entering query mode. Type 'exit' to quit, 'show all' to display all entries, 'show md5' to display all MD5 hashes with source files, 'show sha1' to display all SHA1 hashes with source files, 'show sha256' to display all SHA256 hashes with source files, 'show tag' to display all TAG values with source files, 'show value' to display all VALUE values with source files, 'show enabled' to display all ENABLED values with source files.")
    print("You can also type 'show [key]' to display specific hardware specifications.")
    while True:
        query = input("Enter command: ").strip()
        if query.lower() == 'exit':
            break
        elif query.lower() == 'show all':
            display_all_entries_with_all_keys()
        elif query.lower() == 'show md5':
            display_all_md5()
        elif query.lower() == 'show sha1':
            display_all_sha1()
        elif query.lower() == 'show sha256':
            display_all_sha256()
        elif query.lower() == 'show tag':
            display_all_tag()
        elif query.lower() == 'show value':
            display_all_value()
        elif query.lower() == 'show enabled':
            display_all_enabled()
        elif query.lower().startswith('show '):
            key = query[5:].strip()  # Extract key after 'show '
            display_function_name = f"display_{key.lower()}"
            if hasattr(data_store, display_function_name):
                getattr(data_store, display_function_name)()
            else:
                print(f"No such key: {key}")
        else:
            results = query_data_store(query)
            if results:
                field_names = ["MD5", "SHA1", "SHA256", "Source File"] + list(get_all_keys())
                rows = [[result.get('MD5', ''), result.get('SHA1', ''), result.get('SHA256', ''), result.get('source_file', '')] + [result.get(key, '') for key in get_all_keys()] for result in results]
                table_str = create_pretty_table_with_separators(field_names, rows)
                print(table_str)
            else:
                print("No matching results found.")
