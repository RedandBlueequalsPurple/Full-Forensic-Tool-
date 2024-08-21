import sys
import os
import json
from email.parser import BytesParser
from email import policy
from datetime import datetime
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('tool_execution.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')  # Use the same log file
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def main():
    logger.info("Email Analysis tool execution started.")
    try:
        # Tool logic here
        logger.debug("Executing Email Analysis tool logic.")
        # Example action
        logger.info("Email Analysis tool action completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Email Analysis tool execution finished.")



def read_eml_file(file_path):
    try:
        with open(file_path, 'rb') as eml_file:
            # Parse the EML file
            msg = BytesParser(policy=policy.default).parse(eml_file)
            
            # Extract headers
            headers_text = {}
            for header_name, header_value in msg.items():
                headers_text[header_name] = header_value

            # Extract body
            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        body_text += part.get_payload(decode=True).decode(part.get_content_charset()) + "\n"
            else:
                body_text += msg.get_payload(decode=True).decode(msg.get_content_charset()) + "\n"

            return msg, headers_text, body_text

    except FileNotFoundError:
        return None, {}, "File not found."
    except Exception as e:
        return None, {"error": str(e)}, ""

def export_to_json(headers_text, body_text, file_name_prefix):
    try:
        # Ensure the 'json' directory exists
        os.makedirs('json', exist_ok=True)
        
        # Generate a filename with the current date
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{file_name_prefix}_{current_date}.json"
        file_path = os.path.join('json', file_name)

        # Prepare data for JSON
        data = {
            "headers": headers_text,
            "body": body_text
        }

        # Save the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Data exported to {file_path} successfully!")
    except Exception as e:
        print("An error occurred while exporting data:", str(e))

def save_attachments(msg, output_dir):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for part in msg.iter_attachments():
            filename = part.get_filename()
            if filename:
                print(f"Found attachment: {filename}")
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
    except Exception as e:
        print("An error occurred while saving attachments:", str(e))

def main():
    file_path = input("Enter the file path: ")
    file_path = os.path.join(os.getcwd(), file_path)  # Construct absolute path
    if os.path.isfile(file_path):
        msg, headers_text, body_text = read_eml_file(file_path)
        if msg:
            print("\nHeaders:\n")
            print(headers_text)
            print("\nMessage Body:\n")
            print(body_text)
            
            # Use the filename without the extension for the prefix
            file_name_prefix = os.path.splitext(os.path.basename(file_path))[0]
            export_to_json(headers_text, body_text, file_name_prefix)

            # Define output directory for attachments
            output_dir = 'attachments'
            save_attachments(msg, output_dir)
        else:
            print("Failed to read the email file.")
    else:
        print("File not found.")

if __name__ == "__main__":
    main()
