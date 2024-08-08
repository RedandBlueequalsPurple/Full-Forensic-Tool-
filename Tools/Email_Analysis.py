import sys
import os
import json
from email.parser import BytesParser
from email import policy
from datetime import datetime

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

            return headers_text, body_text

    except FileNotFoundError:
        return {}, "File not found."
    except Exception as e:
        return {"error": str(e)}, ""

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

def main():
    file_path = input("Enter the file path: ")
    file_path = os.path.join(os.getcwd(), file_path)  # Construct absolute path
    if os.path.isfile(file_path):
        headers_text, body_text = read_eml_file(file_path)
        print("\nHeaders:\n")
        print(headers_text)
        print("\nMessage Body:\n")
        print(body_text)
        
        # Use the filename without the extension for the prefix
        file_name_prefix = os.path.splitext(os.path.basename(file_path))[0]
        export_to_json(headers_text, body_text, file_name_prefix)
    else:
        print("File not found.")

if __name__ == "__main__":
    main()
