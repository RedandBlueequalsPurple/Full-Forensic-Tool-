import json
import os
import csv
import array as arr
from prettytable import PrettyTable

# Define paths
db_file = 'db.json'
csv_file_path = 'data.csv'
array_file_path = 'data.bin'
config_file_path = 'config.ini'

def load_db():
    """Load the database from a JSON file."""
    if os.path.isfile(db_file):
        with open(db_file, 'r') as file:
            return json.load(file)
    return {}

def save_db(data_store):
    """Save the database to a JSON file."""
    with open(db_file, 'w') as file:
        json.dump(data_store, file, indent=4)

def display_config(config):
    """Display the current configuration."""
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

def display_data():
    """Display data from the database file."""
    data_store = load_db()

    if data_store:
        # Create a PrettyTable for displaying data
        table = PrettyTable()
        table.field_names = ["Key", "Value"]
        
        # Set table column widths
        table.max_width = {"Key": 60, "Value": 100}
        
        # Iterate through each entry in the data store
        for key, value in data_store.items():
            formatted_value = format_value(value)
            table.add_row([key, formatted_value])
            table.add_row(["-" * 30, "-" * 30])  # Adding a separator line

        print(table)
    else:
        print(f"No data available in '{db_file}'.")

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
    from configparser import ConfigParser

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

def process_and_save_json_data():
    """Process the JSON file and save detailed information to CSV, INI, and binary array files."""
    config = load_db()
    if config:
        # Break down the configuration data
        detailed_data = break_json_data(config)
        print("\nDetailed JSON data:")
        for idx, key in enumerate(detailed_data.keys(), 1):
            print(f"{idx}. {key}")

        try:
            choice = int(input("\nChoose a key to display its value (enter number): ").strip())
            selected_key = list(detailed_data.keys())[choice - 1]
            print(f"Selected key: {selected_key}")
            print(f"Value for '{selected_key}': {detailed_data[selected_key]}")

            save_choice = input(f"Do you want to save the key '{selected_key}' with its value to CSV, INI, and binary array files? (yes/no): ").strip().lower()
            if save_choice == 'yes':
                save_to_csv([{selected_key: detailed_data[selected_key]}], csv_file_path)
                save_to_config({selected_key: detailed_data[selected_key]}, config_file_path)
                save_to_array({selected_key: detailed_data[selected_key]}, array_file_path)
                print("Data saved successfully.")
            else:
                print("Data not saved.")
        except (IndexError, ValueError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No configuration data to process.")

def main_menu():
    """Display the main menu and handle user choices."""
    config = load_db()
    while True:
        print("\nMain Menu:")
        print("1. Add data manually")
        print("2. Parse and add data from JSON file")
        print("3. Remove key from configuration")
        print("4. Display data based on configuration")
        print("5. Process and save JSON data")
        print("6. Exit")

        choice = input("Enter your choice (or type 'exit' to quit): ").strip()

        if choice == '1':
            add_manual_data(config)
        elif choice == '2':
            json_file_path = input("Enter the path to the JSON file: ").strip()
            parse_and_add_data_from_json(json_file_path, config)
        elif choice == '3':
            remove_key_from_config(config)
        elif choice == '4':
            display_data()
        elif choice == '5':
            process_and_save_json_data()
        elif choice == '6' or choice.lower() == 'exit':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main_menu()
