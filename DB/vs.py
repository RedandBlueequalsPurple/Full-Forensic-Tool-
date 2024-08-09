import cmd
import json
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
                sample_ioc = self.db.get(sample_name)
                if sample_ioc:
                    self.check_virustotal(sample_ioc)
                else:
                    print(f"Sample '{sample_name}' not found in the database.")
            else:
                print(f"Sample ID '{sample_id}' not found.")
        else:
            if sample_identifier in self.db:
                sample_ioc = self.db[sample_identifier]
                self.check_virustotal(sample_ioc)
            else:
                print(f"Sample '{sample_identifier}' not found in the database.")

    def check_virustotal(self, sample_ioc):
        """Check the sample IOC against VirusTotal and display the result."""
        try:
            if self.is_hash(sample_ioc):
                file = self.client.get_object(f"/files/{sample_ioc}")
                self.display_file_info(file)
            elif self.is_url(sample_ioc):
                url_id = vt.url_id(sample_ioc)
                url = self.client.get_object(f"/urls/{url_id}")
                self.display_url_info(url)
            elif self.is_domain(sample_ioc):
                domain = self.client.get_object(f"/domains/{sample_ioc}")
                self.display_domain_info(domain)
            elif self.is_ip(sample_ioc):
                ip = self.client.get_object(f"/ip_addresses/{sample_ioc}")
                self.display_ip_info(ip)
            else:
                print(f"Unsupported IOC type: {sample_ioc}")
        except vt.error.APIError as e:
            print(f"API error occurred: {e}")
        except Exception as e:
            print(f"Error checking IOC: {e}")

    def display_file_info(self, file):
        """Display information about a file IOC."""
        name = file.get("meaningful_name", "N/A")
        scan_date = file.get("last_analysis_date", "N/A")
        last_analysis_stats = file.get("last_analysis_stats", {})
        malicious = last_analysis_stats.get('malicious', 0)
        total = sum(last_analysis_stats.values())

        print(f"File: {name}")
        print(f"Scan Date: {scan_date}")
        print(f"Malicious: {malicious}")
        print(f"Total Scans: {total}")

    def display_url_info(self, url):
        """Display information about a URL IOC."""
        scan_date = url.get("last_analysis_date", "N/A")
        last_analysis_stats = url.get("last_analysis_stats", {})
        malicious = last_analysis_stats.get('malicious', 0)
        total = sum(last_analysis_stats.values())

        print(f"URL: {url.get('url', 'N/A')}")
        print(f"Scan Date: {scan_date}")
        print(f"Malicious: {malicious}")
        print(f"Total Scans: {total}")

    def display_domain_info(self, domain):
        """Display information about a domain IOC."""
        last_analysis_stats = domain.get("last_analysis_stats", {})
        malicious = last_analysis_stats.get('malicious', 0)
        total = sum(last_analysis_stats.values())

        print(f"Domain: {domain.get('id', 'N/A')}")
        print(f"Malicious: {malicious}")
        print(f"Total Scans: {total}")

    def display_ip_info(self, ip):
        """Display information about an IP address IOC."""
        last_analysis_stats = ip.get("last_analysis_stats", {})
        malicious = last_analysis_stats.get('malicious', 0)
        total = sum(last_analysis_stats.values())

        print(f"IP Address: {ip.get('id', 'N/A')}")
        print(f"Malicious: {malicious}")
        print(f"Total Scans: {total}")

    def is_hash(self, ioc):
        """Determine if the IOC is a hash."""
        return len(ioc) in (32, 40, 64) and all(c in '0123456789abcdefABCDEF' for c in ioc)

    def is_url(self, ioc):
        """Determine if the IOC is a URL."""
        return ioc.startswith(('http://', 'https://'))

    def is_domain(self, ioc):
        """Determine if the IOC is a domain."""
        return '.' in ioc and not self.is_ip(ioc)

    def is_ip(self, ioc):
        """Determine if the IOC is an IP address."""
        parts = ioc.split('.')
        return len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)

    def do_list_samples(self, _):
        """List all samples in the database with IDs."""
        if self.db:
            table = PrettyTable()
            table.field_names = ["ID", "Name", "IOC"]
            
            # Set table column widths
            table.max_width["ID"] = 5
            table.max_width["Name"] = 30
            table.max_width["IOC"] = 60 

            # Iterate through each entry in the database
            id_counter = 1
            for name, sample_ioc in self.db.items():
                table.add_row([id_counter, name, sample_ioc])
                id_counter += 1

            print(table)
        else:
            print("No samples in the database.")

    def do_display_data(self, _):
        """Display the data in the database in a tabular format."""
        if self.db:
            # Create a PrettyTable for displaying data
            table = PrettyTable()
            table.field_names = ["ID", "Name", "IOC", "Additional Info"]
            
            # Set table column widths
            table.max_width["ID"] = 5
            table.max_width["Name"] = 30
            table.max_width["IOC"] = 60
            table.max_width["Additional Info"] = 30 

            # Iterate through each entry in the database
            id_counter = 1
            for name, sample_ioc in self.db.items():
                additional_info = "N/A"  # Placeholder for additional information
                table.add_row([id_counter, name, sample_ioc, additional_info])
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
