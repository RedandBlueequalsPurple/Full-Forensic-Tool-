import json
import os
import cmd
import csv
import array as arr
from prettytable import PrettyTable
from configparser import ConfigParser

import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Define paths
db_file = 'db.json'
csv_file_path = 'data.csv'
array_file_path = 'data.bin'
config_file_path = 'config.ini'

def load_db():
    """Load the database from a JSON file."""
    logger.info("Config-Cli load the database from a JSON file")
    if os.path.isfile(db_file):
        with open(db_file, 'r') as file:
            return json.load(file)
    return {}

def save_db(data_store):
    """Save the database to a JSON file."""
    #logger.info("Config-Cli save the database to the JSON file")
    with open(db_file, 'w') as file:
        json.dump(data_store, file, indent=4)

def display_config(config):
    """Display the current configuration."""
    #logger.info("Config-Cli is display the current configuration")
    print("\nCurrent Configuration:")
    for key, value in config.items():
        print(f"{key}: {value}")

def add_manual_data(config):
    """Add data manually to the configuration."""
    print("\nEnter the key and value to add, or 'exit' to quit.")
    while True:
        key = input("Enter key: ").strip()
        if key.lower() == 'exit':
            break
        value = input("Enter value: ").strip()
        if key:
            config[key] = value
            print(f"Added {key}: {value}")
        else:
            print("Key cannot be empty.")
            continue
    save_db(config)
    display_config(config)

def remove_key_from_config(config):
    """Remove a key from the configuration."""
    print("\nCurrent keys in configuration:")
    keys = list(config.keys())
    for idx, key in enumerate(keys):
        print(f"{idx + 1}. {key}")

    try:
        choice = int(input("\nChoose a key to remove (enter number): ").strip())
        if 1 <= choice <= len(keys):
            selected_key = keys[choice - 1]
            if input(f"Do you want to remove the key '{selected_key}' from the configuration? (yes/no): ").strip().lower() == 'yes':
                del config[selected_key]
                save_db(config)
                print(f"Key '{selected_key}' removed from configuration.")
            else:
                print("Key not removed from configuration.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def parse_and_add_data_from_json(file_path, config):
    """Parse data from a JSON file and add it to the configuration."""
    if not os.path.isfile(file_path):
        print(f"File {file_path} not found.")
        return

    with open(file_path, 'r') as file:
        data = json.load(file)

    print("\nAvailable keys in the JSON file:")
    
    # Flatten and print keys
    flattened_data = break_json_data(data)
    keys = list(flattened_data.keys())
    for idx, key in enumerate(keys):
        print(f"{idx + 1}. {key}")

    try:
        choice = int(input("\nChoose a key to add to the configuration (enter number): ").strip())
        if 1 <= choice <= len(keys):
            selected_key = keys[choice - 1]
            print(f"Selected key: {selected_key}")
            value = flattened_data[selected_key]
            print(f"Value for '{selected_key}': {value}")
            if input(f"Do you want to add the key '{selected_key}' with value '{value}' to the database configuration? (yes/no): ").strip().lower() == 'yes':
                config[selected_key] = value
                save_db(config)
                print(f"Key '{selected_key}' added to configuration with value: {value}")
            else:
                print("Key not added to configuration.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def format_value(value, max_length=50):
    """Format the value for better readability in the table."""
    if isinstance(value, list):
        formatted_value = ', '.join(str(item) for item in value)
    elif isinstance(value, dict):
        formatted_value = json.dumps(value, indent=2)
    else:
        formatted_value = str(value)
    
    # Truncate if it's too long
    if len(formatted_value) > max_length:
        formatted_value = formatted_value[:max_length] + '...'
    
    return formatted_value

def display_data(filter_key=None):
    """Display data from the database file, optionally filtered by a key."""
    data_store = load_db()

    if data_store:
        # Create a PrettyTable for displaying data
        table = PrettyTable()
        table.field_names = ["ID", "Key", "Value", "Date", "Group"]
        
        # Iterate through each entry in the data store
        id_counter = 1
        for key, value in data_store.items():
            if filter_key is None or filter_key.lower() in key.lower():
                if isinstance(value, dict):
                    date = value.get("date", "N/A")
                    group = value.get("group", "N/A")
                    formatted_value = format_value(value.get("value", ""))
                else:
                    date = "N/A"
                    group = "N/A"
                    formatted_value = format_value(value)
                
                # Add row to the table
                table.add_row([id_counter, key, formatted_value, date, group])
                table.add_row(["-" * 5, "-" * 30, "-" * 60, "-" * 20, "-" * 20])  # Adding a separator line
                id_counter += 1

        # Print the table
        print(table)
    else:
        print(f"No data available in '{db_file}'.")

def assign_keys_to_group(config):
    """Assign a group to all keys that contain a specified keyword."""
    if not config:
        print("No configuration data available.")
        return

    # Get the keyword to search for
    keyword = input("Enter the keyword or pattern to match keys: ").strip()
    if not keyword:
        print("Keyword cannot be empty.")
        return

    # Get the group name to assign
    group = input("Enter the group name to assign to matching keys: ").strip()
    if not group:
        print("Group name cannot be empty.")
        return

    # Track if any keys were updated
    updated = False

    # Iterate through the keys and update the group if the keyword is in the key name
    for key in list(config.keys()):
        if keyword.lower() in key.lower():
            if isinstance(config[key], dict):
                config[key]['group'] = group
            else:
                # Retain the existing value and add the group
                config[key] = {'value': config[key], 'group': group}
            updated = True

    if updated:
        save_db(config)
        print(f"All keys containing '{keyword}' have been assigned to group '{group}'.")
    else:
        print(f"No keys containing '{keyword}' were found.")

def save_to_csv(data, file_path):
    """Save data to a CSV file."""
    try:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Key', 'Value'])
            for item in data:
                for key, value in item.items():
                    writer.writerow([key, value])
        print(f"Data successfully saved to CSV file: {file_path}")
    except IOError as e:
        print(f"Error saving CSV file: {e}")

def save_to_config(data, file_path):
    """Save data to an INI config file."""
    config = ConfigParser()

    if isinstance(data, dict):
        for section, details in data.items():
            if not isinstance(details, dict):
                print(f"Skipping section '{section}' as its value is not a dictionary.")
                continue
            config[section] = details
    else:
        print("Data must be a dictionary of dictionaries for INI file format.")
        return

    try:
        with open(file_path, 'w') as file:
            config.write(file)
        print(f"Data successfully saved to INI file: {file_path}")
    except IOError as e:
        print(f"Error saving INI file: {e}")

def save_to_array(data, file_path):
    """Save data to a binary array file."""
    try:
        with open(file_path, 'wb') as file:
            # Convert data to a byte array
            byte_array = arr.array('B', json.dumps(data).encode())
            file.write(byte_array)
        print(f"Data successfully saved to binary array file: {file_path}")
    except IOError as e:
        print(f"Error saving binary array file: {e}")

def break_json_data(data):
    """Break down JSON data into smaller parts."""
    result = {}
    def flatten_data(d, parent_key=''):
        if isinstance(d, dict):
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, (dict, list)):
                    flatten_data(v, new_key)
                else:
                    result[new_key] = v
        elif isinstance(d, list):
            for i, item in enumerate(d):
                flatten_data(item, f"{parent_key}[{i}]")

    flatten_data(data)
    return result

def process_and_load_data():
    """Process and load data from JSON, CSV, INI, and binary files."""
    # Read JSON data
    if os.path.isfile(db_file):
        with open(db_file, 'r') as file:
            json_data = json.load(file)
        print(f"Loaded data from {db_file}")
    else:
        print(f"{db_file} does not exist. Creating a new one.")
        json_data = {}

    # Load other data formats
    if os.path.isfile(csv_file_path):
        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                json_data[row['Key']] = row['Value']
        print(f"Loaded data from {csv_file_path}")

    if os.path.isfile(config_file_path):
        config = ConfigParser()
        config.read(config_file_path)
        for section in config.sections():
            for key in config[section]:
                json_data[key] = config[section][key]
        print(f"Loaded data from {config_file_path}")

    if os.path.isfile(array_file_path):
        with open(array_file_path, 'rb') as file:
            byte_array = arr.array('B')
            byte_array.fromfile(file, os.path.getsize(array_file_path))
            data = json.loads(byte_array.tobytes().decode())
            json_data.update(data)
        print(f"Loaded data from {array_file_path}")

    save_db(json_data)

class DBCLI(cmd.Cmd):
    """Command-line interface for managing the database."""
    intro = "Welcome to the Database CLI. Type help or ? to list commands.\n"
    prompt = "(Config-cli) "

    def __init__(self):
        super().__init__()
        self.config = load_db()
        self.process_and_load_data()
        logging.info("CLI initialized.")

    def process_and_load_data(self):
        """Process and load data from various files."""
        logging.info("Processing and loading data.")
        process_and_load_data()

    def do_add(self, line):
        """Add data manually to the configuration."""
        logging.info("Running 'add' command.")
        add_manual_data(self.config)

    def do_remove(self, line):
        """Remove a key from the configuration."""
        logging.info("Running 'remove' command.")
        remove_key_from_config(self.config)

    def do_load_json(self, line):
        """Load data from a JSON file into the configuration."""
        file_path = input("Enter the path to the JSON file: ").strip()
        logging.info(f"Running 'load_json' command with file path: {file_path}")
        if not file_path:
            print("File path cannot be empty.")
            return
        parse_and_add_data_from_json(file_path, self.config)

    def do_display(self, line):
        """Display data from the database, optionally filtered by a key."""
        logging.info(f"Running 'display' command with filter_key: {line}")
        display_data(line)

    def do_group(self, line):
        """Assign a group to keys containing a specified keyword."""
        logging.info(f"Running 'group' command with keyword: {line}")
        assign_keys_to_group(self.config)

    def do_save_csv(self, line):
        """Save data to a CSV file."""
        logging.info("Running 'save_csv' command.")
        save_to_csv(self.config, csv_file_path)

    def do_save_ini(self, line):
        """Save data to an INI config file."""
        logging.info("Running 'save_ini' command.")
        save_to_config(self.config, config_file_path)

    def do_save_array(self, line):
        """Save data to a binary array file."""
        logging.info("Running 'save_array' command.")
        save_to_array(self.config, array_file_path)

    def do_load_array(self, line):
        """Load data from a binary array file."""
        logging.info("Running 'load_array' command.")
        process_and_load_data()

    def do_exit(self, line):
        """Exit the CLI."""
        logging.info("Exiting CLI.")
        print("Exiting CLI.")
        return True

    def do_help(self, line):
        """Display help information."""
        logging.info("Running 'help' command.")
        print("\nDocumented commands (type help <topic>):")
        print("========================================")
        print("add           Add data manually to the configuration")
        print("exit          Exit the CLI")
        print("help          Show this help message")
        print("load_json     Load data from a JSON file into the configuration")
        print("save_array    Save data to a binary array file")
        print("save_ini      Save data to an INI config file")
        print("display       Display data from the database, optionally filtered by a key")
        print("group         Assign a group to keys containing a specified keyword")
        print("load_array    Load data from a binary array file")
        print("remove        Remove a key from the configuration")
        print("save_csv      Save data to a CSV file")

    def default(self, line):
        """Handle unknown commands."""
        logger.warning(f"Unknown command: {line}")
        print(f"*** Unknown syntax: {line}")

if __name__ == '__main__':
    DBCLI().cmdloop()
