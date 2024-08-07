import cmd
import json
import requests
import os
from prettytable import PrettyTable

# Initialize Hybrid Analysis API client
API_KEY = 'rgjdcvgm0a826723tesmchjz9f006785f4emp6r514d054e7xf3oukym060041a7'
BASE_URL = 'https://www.hybrid-analysis.com/api/v2'

class HybridAnalysisCLI(cmd.Cmd):
    intro = 'Welcome to the Hybrid Analysis CLI. Type help or ? to list commands.'
    prompt = '(ha-cli) '
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_file = 'db.json'
        self.load_db()

    def load_db(self):
        """Load JSON database."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as file:
                self.db = json.load(file)
        else:
            print(f"Database file '{self.db_file}' not found.")
            self.db = {}

    def do_check(self, sample_identifier):
        """Check a sample against Hybrid Analysis: check [sample_identifier]"""
        if sample_identifier.isdigit():
            sample_id = int(sample_identifier)
            sample_name = self.get_sample_name_by_id(sample_id)
            if sample_name:
                sample_hash = self.db.get(sample_name)
                if sample_hash:
                    self.check_hybrid_analysis(sample_hash)
                else:
                    print(f"Sample '{sample_name}' not found in the database.")
            else:
                print(f"Sample ID '{sample_id}' not found.")
        else:
            if sample_identifier in self.db:
                sample_hash = self.db[sample_identifier]
                self.check_hybrid_analysis(sample_hash)
            else:
                print(f"Sample '{sample_identifier}' not found in the database.")

    def check_hybrid_analysis(self, sample_hash):
        """Check the sample hash against Hybrid Analysis and display the result."""
        url = f"{BASE_URL}/files/{sample_hash}"
        headers = {
            'Authorization': f'Bearer {API_KEY}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for HTTP errors
            
            if response.status_code == 200:
                data = response.json()
                name = data.get('file_name', 'N/A')
                scan_date = data.get('scan_date', 'N/A')
                last_analysis_stats = data.get('last_analysis_stats', {})
                malicious = last_analysis_stats.get('malicious', 0)
                total = last_analysis_stats.get('total', 0)

                print(f"File: {name}")
                print(f"Scan Date: {scan_date}")
                print(f"Malicious: {malicious}")
                print(f"Total Scans: {total}")
            else:
                print(f"File with hash '{sample_hash}' not found.")
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"File with hash '{sample_hash}' not found in Hybrid Analysis.")
            else:
                print(f"HTTP error occurred: {e}")
        except requests.exceptions.RequestException as e:
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
        return True

    def test_hybrid_analysis(self):
        """Test Hybrid Analysis API with a known hash."""
        test_hash = 'your_known_sha256_hash_here'  # Replace with a known hash
        url = f"{BASE_URL}/files/{test_hash}"
        headers = {
            'Authorization': f'Bearer {API_KEY}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for HTTP errors
            
            if response.status_code == 200:
                data = response.json()
                name = data.get('file_name', 'N/A')
                scan_date = data.get('scan_date', 'N/A')
                last_analysis_stats = data.get('last_analysis_stats', {})
                malicious = last_analysis_stats.get('malicious', 0)
                total = last_analysis_stats.get('total', 0)

                print(f"File: {name}")
                print(f"Scan Date: {scan_date}")
                print(f"Malicious: {malicious}")
                print(f"Total Scans: {total}")
            else:
                print(f"File with hash '{test_hash}' not found.")
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"File with hash '{test_hash}' not found in Hybrid Analysis.")
            else:
                print(f"HTTP error occurred: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error checking file: {e}")

if __name__ == '__main__':
    HybridAnalysisCLI().cmdloop()
