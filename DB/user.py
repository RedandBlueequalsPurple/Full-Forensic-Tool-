import json
import os
from prettytable import PrettyTable

# Define the path to the database file
db_file = 'db.json'

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
    data_store = load_data_store()

    if data_store:
        # Create a PrettyTable for displaying data
        table = PrettyTable()
        table.field_names = ["Key", "Value"]
        
        # Set table column widths
        table.max_width["Key"] = 60
        table.max_width["Value"] = 100
        
        # Iterate through each entry in the data store
        for key, value in data_store.items():
            formatted_value = format_value(value)
            table.add_row([key, formatted_value])
            table.add_row(["-" * 30, "-" * 30])  # Adding a separator line

        print(table)
    else:
        print(f"No data available in '{db_file}'.")

def main_loop():
    """Main command loop for displaying and filtering data."""
    while True:
        print("\nAvailable Commands:")
        print("1. Display all data")
        print("2. Filter data by key")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == '1':
            display_data()
        elif choice == '2':
            key_filter = input("Enter the key to filter by: ").strip()
            data_store = load_data_store()
            if data_store:
                # Create a PrettyTable for displaying filtered data
                table = PrettyTable()
                table.field_names = ["Key", "Value"]

                # Set table column widths
                table.max_width["Key"] = 60
                table.max_width["Value"] = 100

                if key_filter in data_store:
                    formatted_value = format_value(data_store[key_filter])
                    table.add_row([key_filter, formatted_value])
                    table.add_row(["-" * 30, "-" * 30])  # Adding a separator line

                    print(table)
                else:
                    print(f"Key '{key_filter}' not found in data store.")
            else:
                print(f"No data available in '{db_file}'.")
        elif choice == '3' or choice.lower() == 'exit':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main_loop()
