import cmd
import json
import requests
import os
from prettytable import PrettyTable
import vt

# Initialize VirusTotal API client
API_KEY = '9bcb54f31badf1de44a5ea1b0f501f02a42ac46389133cf554b80409219dbdd8'

class VirusTotalCLI(cmd.Cmd):
    intro = 'Welcome to the VirusTotal CLI. Type help or ? to list commands.'
    prompt = '(vt-cli) '
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_file = 'db.json'
        self.load_db()
        self.client = vt.Client(API_KEY)

    def load_db(self):
        """Load JSON database."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as file:
                self.db = json.load(file)
        else:
            print(f"Database file '{self.db_file}' not found.")
            self.db = {}

    def do_check(self, sample_identifier):
        """Check a sample against VirusTotal: check [sample_identifier]"""
        if sample_identifier.isdigit():
            sample_id = int(sample_identifier)
            sample_name = self.get_sample_name_by_id(sample_id)
            if sample_name:
                sample_hash = self.db.get(sample_name)
                if sample_hash:
                    self.check_virustotal(sample_hash)
                else:
                    print(f"Sample '{sample_name}' not found in the database.")
            else:
                print(f"Sample ID '{sample_id}' not found.")
        else:
            if sample_identifier in self.db:
                sample_hash = self.db[sample_identifier]
                self.check_virustotal(sample_hash)
            else:
                print(f"Sample '{sample_identifier}' not found in the database.")

    def check_virustotal(self, sample_hash):
        """Check the sample hash against VirusTotal and display the result."""
        try:
            file = self.client.get_object(f"/files/{sample_hash}")

            name = file.get("meaningful_name", "N/A")
            scan_date = file.get("last_analysis_date", "N/A")
            last_analysis_stats = file.get("last_analysis_stats", {})
            malicious = last_analysis_stats.get('malicious', 0)
            total = sum(last_analysis_stats.values())

            print(f"File: {name}")
            print(f"Scan Date: {scan_date}")
            print(f"Malicious: {malicious}")
            print(f"Total Scans: {total}")

        except vt.error.APIError as e:
            if e.code == 'NotFoundError':
                print(f"File with hash '{sample_hash}' not found in VirusTotal.")
            else:
                print(f"API error occurred: {e}")
        except Exception as e:
            print(f"Error checking file: {e}")

    def do_list_samples(self, _):
        """List all samples in the database with IDs."""
        if self.db:
            table = PrettyTable()
            table.field_names = ["ID", "Name", "Hash"]
            
            # Set table column widths
            table.max_width["ID"] = 5
            table.max_width["Name"] = 30
            table.max_width["Hash"] = 60 

            # Iterate through each entry in the database
            id_counter = 1
            for name, sample_hash in self.db.items():
                table.add_row([id_counter, name, sample_hash])
                id_counter += 1

            print(table)
        else:
            print("No samples in the database.")

    def do_display_data(self, _):
        """Display the data in the database in a tabular format."""
        if self.db:
            # Create a PrettyTable for displaying data
            table = PrettyTable()
            table.field_names = ["ID", "Name", "Hash", "Additional Info"]
            
            # Set table column widths
            table.max_width["ID"] = 5
            table.max_width["Name"] = 30
            table.max_width["Hash"] = 60
            table.max_width["Additional Info"] = 30 

            # Iterate through each entry in the database
            id_counter = 1
            for name, sample_hash in self.db.items():
                additional_info = "N/A"  # Placeholder for additional information
                table.add_row([id_counter, name, sample_hash, additional_info])
                id_counter += 1

            print(table)
        else:
            print(f"No data available in '{self.db_file}'.")

    def get_sample_name_by_id(self, sample_id):
        """Get sample name by its ID."""
        if 1 <= sample_id <= len(self.db):
            sample_name = list(self.db.keys())[sample_id - 1]
            return sample_name
        return None

    def do_exit(self, _):
        """Exit the CLI."""
        print('Goodbye!')
        self.client.close()
        return True

if __name__ == '__main__':
    VirusTotalCLI().cmdloop()
