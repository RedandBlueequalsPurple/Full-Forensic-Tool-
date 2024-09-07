import os
import json
from email.parser import BytesParser
from email import policy
from datetime import datetime
import logging
from rich.console import Console
from rich.table import Table

# Initialize Rich console for colored output
console = Console()

class EmailAnalysis:
    def __init__(self, current_case_number=None, archive_folder='archive cases'):
        self.archive_folder = archive_folder
        self.current_case_number = current_case_number or self.generate_case_number()
        self.setup_logging()

    def generate_case_number(self):
        """Automatically generate a new case number based on existing case files."""
        case_files = [f for f in os.listdir(self.archive_folder) if f.startswith("case_")]
        if case_files:
            last_case = sorted(case_files)[-1]
            last_case_number = int(last_case.split("_")[1].split(".")[0])
            return last_case_number + 1
        else:
            return 1

    def setup_logging(self):
        """Set up logging for the case file."""
        case_file_name = f"case_{self.current_case_number}.txt"
        self.log_file = os.path.join(self.archive_folder, case_file_name)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                pass  # Create the file if it doesn't exist
        logging.basicConfig(filename=self.log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info(f"Case {self.current_case_number} initialized.")

    def log_to_case_file(self, message):
        """Log a message to the current case file."""
        if self.log_file:
            logging.info(message)

    def read_eml_file(self, file_path):
        """Read and parse the EML file."""
        try:
            self.log_to_case_file(f"Attempting to read EML file: {file_path}")
            with open(file_path, 'rb') as eml_file:
                msg = BytesParser(policy=policy.default).parse(eml_file)

                # Extract headers
                headers_text = {header_name: header_value for header_name, header_value in msg.items()}
                self.log_to_case_file(f"Extracted headers: {headers_text}")

                # Extract body
                body_text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain':
                            part_body = part.get_payload(decode=True).decode(part.get_content_charset())
                            body_text += part_body + "\n"
                else:
                    body_text = msg.get_payload(decode=True).decode(msg.get_content_charset()) + "\n"

                self.log_to_case_file(f"Extracted body: {body_text.strip()}")
                return msg, headers_text, body_text

        except FileNotFoundError:
            self.log_to_case_file(f"File not found: {file_path}")
            console.print("[bold red]File not found.[/bold red]")
            return None, {}, "File not found."
        except Exception as e:
            self.log_to_case_file(f"Error reading EML file: {e}")
            console.print(f"[bold red]Error reading EML file: {str(e)}[/bold red]")
            return None, {"error": str(e)}, ""

    def display_email_details(self, headers_text, body_text):
        """Display the email headers and body using Rich tables."""
        table = Table(title="Email Headers", show_header=True, header_style="bold magenta")
        table.add_column("Header", style="dim", width=20)
        table.add_column("Value", style="bold cyan")

        for header, value in headers_text.items():
            table.add_row(header, value)

        console.print(table)
        console.print("\n[bold]Email Body:[/bold]", style="green")
        console.print(body_text.strip())

    def export_to_json(self, headers_text, body_text, file_name_prefix):
        """Export the email data to a JSON file."""
        try:
            self.log_to_case_file(f"Exporting data to JSON with prefix: {file_name_prefix}")
            os.makedirs('json', exist_ok=True)

            current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"{file_name_prefix}_{current_date}.json"
            file_path = os.path.join('json', file_name)

            data = {
                "headers": headers_text,
                "body": body_text
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            self.log_to_case_file(f"Data exported to JSON file: {file_path} successfully!")
            console.print(f"[green]Data exported to {file_path} successfully![/green]")
        except Exception as e:
            self.log_to_case_file(f"Error exporting data to JSON: {e}")
            console.print(f"[bold red]An error occurred while exporting data: {str(e)}[/bold red]")

    def save_attachments(self, msg, output_dir="attachments"):
        """Save attachments from the email to the specified directory."""
        try:
            self.log_to_case_file(f"Saving attachments to directory: {output_dir}")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            for part in msg.iter_attachments():
                filename = part.get_filename()
                if filename:
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    self.log_to_case_file(f"Saved attachment: {filename} to {filepath}")
                    console.print(f"[green]Saved attachment: {filename} to {output_dir}[/green]")
        except Exception as e:
            self.log_to_case_file(f"Error saving attachments: {e}")
            console.print(f"[bold red]An error occurred while saving attachments: {str(e)}[/bold red]")

    def main(self):
        """Main function to handle the entire email analysis process."""
        self.log_to_case_file("Email Analysis tool execution started.")
        try:
            file_path = input("Enter the path to the email file (.eml): ")

            # Handle both absolute and relative paths
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
            self.log_to_case_file(f"Constructed absolute path: {file_path}")

            if os.path.isfile(file_path):
                msg, headers_text, body_text = self.read_eml_file(file_path)
                if msg:
                    # Display email details
                    self.display_email_details(headers_text, body_text)

                    # Export email data to JSON
                    file_name_prefix = os.path.splitext(os.path.basename(file_path))[0]
                    self.export_to_json(headers_text, body_text, file_name_prefix)

                    # Save attachments
                    output_dir = 'attachments'
                    self.save_attachments(msg, output_dir)
                else:
                    console.print("[bold red]Failed to read the email file.[/bold red]")
            else:
                console.print("[bold red]File not found.[/bold red]")
        except Exception as e:
            self.log_to_case_file(f"An error occurred: {e}")
            console.print(f"[bold red]An error occurred: {str(e)}[/bold red]")
        finally:
            self.log_to_case_file("Email Analysis tool execution finished.")

if __name__ == "__main__":
    # Ensure this script is executed directly
    analysis_tool = EmailAnalysis()  # Case number will be auto-generated
    analysis_tool.main()
