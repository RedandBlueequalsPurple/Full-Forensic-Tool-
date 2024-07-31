import sys
import os
from email.parser import BytesParser
from email import policy
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QDesktopWidget, QFileDialog

class SecureApplication(QApplication):
    def applicationSupportsSecureRestorableState(self):
        return True

def read_eml_file(file_path):
    try:
        with open(file_path, 'rb') as eml_file:
            # Parse the EML file
            msg = BytesParser(policy=policy.default).parse(eml_file)
            
            # Extract headers
            headers_text = ""
            for header_name, header_value in msg.items():
                headers_text += f"{header_name}: {header_value}\n"

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
        return "File not found.", ""
    except Exception as e:
        return "An error occurred: " + str(e), ""

def show_popup(file_path):
    app = SecureApplication(sys.argv)
    popup = QWidget()
    popup.setWindowTitle("EML File Viewer")

    layout = QVBoxLayout()

    headers_label = QLabel()
    body_label = QLabel()

    headers_text, body_text = read_eml_file(file_path)

    headers_label.setText(headers_text)
    body_label.setText(body_text)

    headers_label.setWordWrap(True)
    body_label.setWordWrap(True)

    layout.addWidget(QLabel("Headers:"))
    layout.addWidget(headers_label)
    layout.addWidget(QLabel("Message Body:"))
    layout.addWidget(body_label)

    # Export button
    def export_data():
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            txt_file_path, _ = QFileDialog.getSaveFileName(popup, "Save TXT", "", "Text Files (*.txt)", options=options)
            if txt_file_path:
                with open(txt_file_path, 'w', encoding='utf-8') as f:
                    f.write(headers_text)
                    f.write("\n\n")
                    f.write(body_text)
                print("Data exported to TXT successfully!")
        except Exception as e:
            print("An error occurred while exporting data:", str(e))

    export_button = QPushButton("Export to TXT")
    export_button.clicked.connect(export_data)
    layout.addWidget(export_button)

    # Close button
    close_button = QPushButton("Close")
    close_button.clicked.connect(popup.close)
    layout.addWidget(close_button)

    popup.setLayout(layout)

    # Set window size based on screen size
    screen = QDesktopWidget().screenGeometry()
    popup_width = screen.width() * 0.5  # Adjust window width to be 50% of screen width
    popup_height = screen.height() * 0.5  # Adjust window height to be 50% of screen height
    popup.setGeometry(screen.width() * 0.25, screen.height() * 0.25, popup_width, popup_height)  # Place window at 25% from the left and top of the screen

    popup.show()
    sys.exit(app.exec_())

def main():
    file_path = input("Enter the file path: ")
    file_path = os.path.join(os.getcwd(), file_path)  # Construct absolute path
    if os.path.isfile(file_path):
        show_popup(file_path)
    else:
        print("File not found.")

if __name__ == "__main__":
    main()
