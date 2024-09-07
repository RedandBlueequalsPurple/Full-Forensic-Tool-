import os
import json
from email.parser import BytesParser
from email import policy
from datetime import datetime
import logging

class EmailAnalysis:
    def __init__(self, current_case_number=None, archive_folder='archive cases'):
        self.current_case_number = current_case_number
        self.archive_folder = archive_folder
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging for the CLI."""
        if self.current_case_number:
            case_file_name = f"case_{self.current_case_number}.txt"
            self.log_file = os.path.join(self.archive_folder, case_file_name)
            if not os.path.exists(self.log_file):
                print(f"[red]Case file {case_file_name} does not exist. Logging will not be set up.[/red]")
                self.log_file = None
        else:
            self.log_file = None

        if self.log_file:
            logging.basicConfig(filename=self.log_file, level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')
            logging.info('CaseFileCLI initialized.')

    def log_to_case_file(self, message):
        """Log a message to the current case file."""
        if self.log_file:
            logging.info(message)

    def read_eml_file(self, file_path):
        try:
            self.log_to_case_file(f"Attempting to read EML file: {file_path}")
            with open(file_path, 'rb') as eml_file:
                msg = BytesParser(policy=policy.default).parse(eml_file)
                
                # Extract headers
                headers_text = {}
                for header_name, header_value in msg.items():
                    headers_text[header_name] = header_value
                    self.log_to_case_file(f"Header - {header_name}: {header_value}")

                # Extract body
                body_text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain':
                            part_body = part.get_payload(decode=True).decode(part.get_content_charset())
                            body_text += part_body + "\n"
                            self.log_to_case_file(f"Multipart body part: {part_body}")
                else:
                    body_text = msg.get_payload(decode=True).decode(msg.get_content_charset()) + "\n"
                    self.log_to_case_file(f"Singlepart body: {body_text}")

                self.log_to_case_file(f"Successfully read EML file: {file_path}")
                return msg, headers_text, body_text

        except FileNotFoundError:
            self.log_to_case_file(f"File not found: {file_path}")
            return None, {}, "File not found."
        except Exception as e:
            self.log_to_case_file(f"Error reading EML file: {e}")
            return None, {"error": str(e)}, ""

    def export_to_json(self, headers_text, body_text, file_name_prefix):
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
            self.log_to_case_file(f"Exported JSON content: {json.dumps(data, ensure_ascii=False, indent=4)}")
            print(f"Data exported to {file_path} successfully!")
        except Exception as e:
            self.log_to_case_file(f"Error exporting data to JSON: {e}")
            print("An error occurred while exporting data:", str(e))

    def save_attachments(self, msg, output_dir):
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
        except Exception as e:
            self.log_to_case_file(f"Error saving attachments: {e}")
            print("An error occurred while saving attachments:", str(e))

    def main(self):
        self.log_to_case_file("Email Analysis tool execution started.")
        try:
            file_path = input("Enter the file path: ")
            file_path = os.path.join(os.getcwd(), file_path)  # Construct absolute path
            self.log_to_case_file(f"Constructed absolute path: {file_path}")
            
            if os.path.isfile(file_path):
                msg, headers_text, body_text = self.read_eml_file(file_path)
                if msg:
                    self.log_to_case_file(f"Extracted Headers: {headers_text}")
                    self.log_to_case_file(f"Extracted Body: {body_text}")

                    file_name_prefix = os.path.splitext(os.path.basename(file_path))[0]
                    self.export_to_json(headers_text, body_text, file_name_prefix)

                    output_dir = 'attachments'
                    self.save_attachments(msg, output_dir)
                else:
                    self.log_to_case_file("Failed to read the email file.")
                    print("Failed to read the email file.")
            else:
                self.log_to_case_file(f"File not found: {file_path}")
                print("File not found.")
        except Exception as e:
            self.log_to_case_file(f"An error occurred: {e}")
        finally:
            self.log_to_case_file("Email Analysis tool execution finished.")

if __name__ == "__main__":
    # Ensure this script is executed directly
    analysis_tool = EmailAnalysis(current_case_number=123)  # Example case number
    analysis_tool.main()
