import json
import os
from prettytable import PrettyTable

# Define the path to the configuration file and database file
config_file = 'config.json'
db_file = 'db.json'

def load_config():
    """Load the configuration from a JSON file."""
    if os.path.isfile(config_file):
        try:
            with open(config_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Error decoding JSON configuration file.")
    return {}

def display_data_based_on_config(config):
    """Display data from the database file based on the current configuration."""
    data_store_file = db_file

    if os.path.isfile(data_store_file):
        try:
            with open(data_store_file, 'r') as file:
                data_store = json.load(file)
        except json.JSONDecodeError:
            print("Error decoding JSON data store file.")
            return
        except IOError:
            print(f"Error reading the data store file '{data_store_file}'.")
            return

        # Create a PrettyTable for displaying data
        table = PrettyTable()
        table.field_names = ["Key", "Value"]

        # Iterate through each entry in the data store
        for key, value in data_store.items():
            if key in config:  # Only display keys that are in the configuration
                table.add_row([key, value])
                table.add_row(["-" * 30, "-" * 30])  # Adding a separator line

        print(table)
    else:
        print(f"Data store file '{data_store_file}' not found.")

def main_loop():
    """Main command loop for filtering and displaying data."""
    config = load_config()
    
    if not config:
        print("No configuration loaded.")
        return

    while True:
        print("\nAvailable Commands:")
        print("1. Display data based on config")
        print("2. Filter data by key")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == '1':
            display_data_based_on_config(config)
        elif choice == '2':
            key_filter = input("Enter the key to filter by: ").strip()
            if key_filter in config:
                # Create a PrettyTable for displaying filtered data
                table = PrettyTable()
                table.field_names = ["Key", "Value"]

                data_store = load_data_store()
                if data_store:
                    for key, value in data_store.items():
                        if key == key_filter:
                            table.add_row([key, value])
                            table.add_row(["-" * 30, "-" * 30])  # Adding a separator line
                    
                    print(table)
                else:
                    print(f"No data available in '{db_file}'.")

            else:
                print(f"Key '{key_filter}' not found in configuration.")
        elif choice == '3' or choice.lower() == 'exit':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def load_data_store():
    """Load the data store from a JSON file."""
    if os.path.isfile(db_file):
        try:
            with open(db_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Error decoding JSON data store file.")
        except IOError:
            print(f"Error reading the data store file '{db_file}'.")
    return {}

if __name__ == "__main__":
    main_loop()
