import json
import os
import cmd
import logging

# Set up logging
log_file = 'event_history.log'
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define directories and files
json_directory = 'JSON'
processed_files_path = 'processed_files.txt'
data_store_file = 'db.json'
config_file = 'config.json'

# Ensure the directories exist
if not os.path.exists(json_directory):
    os.makedirs(json_directory)

def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            logging.info(f"Loading file {file_path}")
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return None

def get_processed_files():
    """Retrieve the list of processed files."""
    if os.path.isfile(processed_files_path):
        with open(processed_files_path, 'r') as file:
            logging.info(f"Retrieving processed files from {processed_files_path}")
            return set(line.strip() for line in file)
    return set()

def update_processed_files(file_list):
    """Update the list of processed files."""
    with open(processed_files_path, 'a') as file:
        for file_name in file_list:
            file.write(f"{file_name}\n")
            logging.info(f"Updated processed files with {file_name}")

def copy_config_to_data_store(data_store):
    """Copy data from config.json to the data store."""
    if os.path.isfile(config_file):
        config_data = load_json(config_file)
        if config_data:
            for key, value in config_data.items():
                if key in data_store:
                    if isinstance(data_store[key], list):
                        data_store[key].append(value)
                    else:
                        data_store[key] = [data_store[key], value]
                else:
                    data_store[key] = [value]
            logging.info("Config data copied to data store.")
    else:
        logging.warning(f"Config file {config_file} not found.")

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

def process_new_files():
    """Process new JSON files and update the data store."""
    processed_files = get_processed_files()
    json_files = [f for f in os.listdir(json_directory) if os.path.isfile(os.path.join(json_directory, f))]
    new_files = [f for f in json_files if f not in processed_files]

    if not new_files:
        logging.info("No new files to process.")
        return

    logging.info(f"Processing new files: {new_files}")

    all_data = load_db()

    for json_file in new_files:
        file_path = os.path.join(json_directory, json_file)
        data = load_json(file_path)

        if data:
            flattened_data = break_json_data(data)
            for key, value in flattened_data.items():
                if key in all_data:
                    if isinstance(all_data[key], list):
                        all_data[key].append(value)
                    else:
                        all_data[key] = [all_data[key], value]
                else:
                    all_data[key] = [value]
            logging.info(f"Processed data from file: {json_file}")

    # Include data from config.json
    copy_config_to_data_store(all_data)

    # Save all data to file
    save_data_store(all_data)
    update_processed_files(new_files)

def load_db():
    """Load the database from a JSON file."""
    if os.path.isfile(data_store_file):
        with open(data_store_file, 'r') as file:
            logging.info(f"Loading database from {data_store_file}")
            return json.load(file)
    logging.info(f"No existing database found. Creating a new one.")
    return {}

def save_data_store(data):
    """Save the data store to a JSON file."""
    with open(data_store_file, 'w') as file:
        json.dump(data, file, indent=4)
        logging.info(f"Data saved to {data_store_file}")

class DBCLI(cmd.Cmd):
    prompt = '(Server-cli) '
    
    def preloop(self):
        logging.info("Starting the Server CLI")

    def postloop(self):
        logging.info("Exiting the Server CLI")

    def default(self, line):
        """Log unknown commands"""
        logging.warning(f"Unknown command: {line}")
        print(f"Unknown command: {line}")

    def do_process(self, arg):
        """Process new JSON files and update the data store."""
        logging.info(f"User input: process {arg}")
        process_new_files()

    def do_load_db(self, arg):
        """Load the database from the JSON file."""
        logging.info(f"User input: load_db {arg}")
        data = load_db()
        logging.info("Database loaded:")
        logging.info(json.dumps(data, indent=4))

    def do_save_db(self, arg):
        """Save the current data to the database file."""
        logging.info(f"User input: save_db {arg}")
        data = load_db()  # Assuming we want to save current data
        save_data_store(data)
        logging.info("Data saved to database file.")

    def do_exit(self, arg):
        """Exit the CLI."""
        logging.info(f"User input: exit {arg}")
        logging.info("Exiting...")
        return True

    def do_help(self, arg):
        """Show help information."""
        logging.info(f"User input: help {arg}")
        if arg:
            cmd.Cmd.do_help(self, arg)
        else:
            print("\nDocumented commands (type help <topic>):")
            print("========================================")
            print("process       Process new JSON files and update the data store")
            print("load_db       Load the database from the JSON file")
            print("save_db       Save the current data to the database file")
            print("exit          Exit the CLI")
            print("help          Show this help message")

if __name__ == '__main__':
    DBCLI().cmdloop()
