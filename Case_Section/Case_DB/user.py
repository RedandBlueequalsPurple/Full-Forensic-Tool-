import json
import os
from prettytable import PrettyTable
from datetime import datetime
import cmd
import logging

# Set up logging
log_file = 'event_history.log'
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define the path to the database file
db_file = 'db.json'

def load_data_store():
    """Load the data store from a JSON file."""
    if os.path.isfile(db_file):
        try:
            with open(db_file, 'r') as file:
                logging.info(f"Loading data store from {db_file}")
                return json.load(file)
        except json.JSONDecodeError:
            logging.error("Error decoding JSON data store file.")
            print("Error decoding JSON data store file.")
        except IOError:
            logging.error(f"Error reading the data store file '{db_file}'.")
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

def display_data(filter_key=None, filter_group=None):
    """Display data from the database file, optionally filtered by a key and/or group."""
    data_store = load_data_store()

    if data_store:
        # Create a PrettyTable for displaying data
        table = PrettyTable()
        table.field_names = ["ID", "Key", "Value", "Date", "Group", "VS checked"]
        
        # Set table column widths
        table.max_width["ID"] = 5
        table.max_width["Key"] = 30
        table.max_width["Value"] = 60
        table.max_width["Date"] = 20
        table.max_width["Group"] = 20
        table.max_width["VS checked"] = 30
        
        # Add the actual data rows
        id_counter = 1
        for key, value in data_store.items():
            if (filter_key is None or filter_key.lower() in key.lower()) and \
               (filter_group is None or (isinstance(value, dict) and value.get("group", "N/A").lower() == filter_group.lower())):
                if isinstance(value, dict):
                    date = value.get("date", "N/A")
                    group = value.get("group", "N/A")
                    formatted_value = format_value(value.get("value", ""))
                else:
                    date = "N/A"
                    group = "N/A"
                    formatted_value = format_value(value)
                
                vs_checked = "N/A"  # Placeholder value for the "VS checked" column
                
                table.add_row([id_counter, key, formatted_value, date, group, vs_checked])
                
                # Add a separator row after each data row
                separator_row = ['-'*len(field) for field in table.field_names]
                table.add_row(separator_row)
                
                id_counter += 1

        logging.info("Displaying data:")
        logging.info(f"\n{table}")
        print(table)
    else:
        logging.info(f"No data available in '{db_file}'.")
        print(f"No data available in '{db_file}'.")

def show_groups():
    """Display all unique groups in the data store."""
    data_store = load_data_store()
    groups = set()

    for value in data_store.values():
        if isinstance(value, dict) and "group" in value:
            groups.add(value["group"])

    if groups:
        logging.info("Displaying groups:")
        for group in groups:
            logging.info(group)
            print(group)
    else:
        logging.info("No groups available.")
        print("No groups available.")

class DBCLI(cmd.Cmd):
    prompt = '(User-cli) '
    
    def preloop(self):
        logging.info("Starting the User CLI")

    def postloop(self):
        logging.info("Exiting the User CLI")

    def default(self, line):
        """Log unknown commands"""
        logging.warning(f"Unknown command: {line}")
        print(f"Unknown command: {line}")

    def do_display(self, arg):
        """Display all data."""
        logging.info(f"User input: display {arg}")
        display_data()

    def do_filter_key(self, arg):
        """Filter data by key."""
        logging.info(f"User input: filter_key {arg}")
        key_filter = input("Enter key to filter by: ").strip()
        logging.info(f"Filter key input: {key_filter}")
        if key_filter:
            display_data(filter_key=key_filter)
        else:
            logging.warning("No key provided to filter by.")
            print("Please provide a key to filter by.")

    def do_filter_group(self, arg):
        """Filter data by group."""
        logging.info(f"User input: filter_group {arg}")
        group_filter = input("Enter group to filter by (or type 'show groups'): ").strip()
        logging.info(f"Filter group input: {group_filter}")
        if group_filter.lower() == 'show groups':
            show_groups()
        elif group_filter:
            display_data(filter_group=group_filter)
        else:
            logging.warning("No group provided to filter by.")
            print("Please provide a group to filter by.")

    def do_exit(self, arg):
        """Exit the CLI."""
        logging.info(f"User input: exit {arg}")
        logging.info("Exiting...")
        print("Exiting...")
        return True

    def do_help(self, arg):
        """Show help information."""
        logging.info(f"User input: help {arg}")
        if arg:
            cmd.Cmd.do_help(self, arg)
        else:
            help_message = (
                "\nDocumented commands (type help <topic>):\n"
                "========================================\n"
                "display       Display all data\n"
                "filter_key    Filter data by key\n"
                "filter_group  Filter data by group\n"
                "exit          Exit the CLI\n"
                "help          Show this help message\n"
            )
            logging.info(f"Displaying help:\n{help_message}")
            print(help_message)

if __name__ == '__main__':
    DBCLI().cmdloop()
