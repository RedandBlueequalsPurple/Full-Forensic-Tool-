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
handler = logging.FileHandler('event_history.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def read_eml_file(file_path):
    try:
        logger.debug(f"Attempting to read EML file: {file_path}")
        with open(file_path, 'rb') as eml_file:
            msg = BytesParser(policy=policy.default).parse(eml_file)
            
            # Extract headers
            headers_text = {}
            for header_name, header_value in msg.items():
                headers_text[header_name] = header_value
                logger.debug(f"Header - {header_name}: {header_value}")

            # Extract body
            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        part_body = part.get_payload(decode=True).decode(part.get_content_charset())
                        body_text += part_body + "\n"
                        logger.debug(f"Multipart body part: {part_body}")
            else:
                body_text = msg.get_payload(decode=True).decode(msg.get_content_charset()) + "\n"
                logger.debug(f"Singlepart body: {body_text}")

            logger.info(f"Successfully read EML file: {file_path}")
            return msg, headers_text, body_text

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None, {}, "File not found."
    except Exception as e:
        logger.error(f"Error reading EML file: {e}")
        return None, {"error": str(e)}, ""

def export_to_json(headers_text, body_text, file_name_prefix):
    try:
        logger.debug(f"Exporting data to JSON with prefix: {file_name_prefix}")
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
        
        logger.info(f"Data exported to JSON file: {file_path} successfully!")
        logger.debug(f"Exported JSON content: {json.dumps(data, ensure_ascii=False, indent=4)}")
        print(f"Data exported to {file_path} successfully!")
    except Exception as e:
        logger.error(f"Error exporting data to JSON: {e}")
        print("An error occurred while exporting data:", str(e))

def save_attachments(msg, output_dir):
    try:
        logger.debug(f"Saving attachments to directory: {output_dir}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for part in msg.iter_attachments():
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                logger.info(f"Saved attachment: {filename} to {filepath}")
    except Exception as e:
        logger.error(f"Error saving attachments: {e}")
        print("An error occurred while saving attachments:", str(e))

def main():
    logger.info("Email Analysis tool execution started.")
    try:
        file_path = input("Enter the file path: ")
        file_path = os.path.join(os.getcwd(), file_path)  # Construct absolute path
        logger.debug(f"Constructed absolute path: {file_path}")
        
        if os.path.isfile(file_path):
            msg, headers_text, body_text = read_eml_file(file_path)
            if msg:
                logger.debug(f"Extracted Headers: {headers_text}")
                logger.debug(f"Extracted Body: {body_text}")

                file_name_prefix = os.path.splitext(os.path.basename(file_path))[0]
                export_to_json(headers_text, body_text, file_name_prefix)

                output_dir = 'attachments'
                save_attachments(msg, output_dir)
            else:
                logger.warning("Failed to read the email file.")
                print("Failed to read the email file.")
        else:
            logger.warning(f"File not found: {file_path}")
            print("File not found.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Email Analysis tool execution finished.")

if __name__ == "__main__":
    main()
