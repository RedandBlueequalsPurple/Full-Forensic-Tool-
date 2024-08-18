import cmd
import os
from datetime import datetime
import importlib.util
import logging
import sys

class CaseFileCLI(cmd.Cmd):
    prompt = 'casefile> '
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.current_case_number = None
        self.log_file = None
        self.current_tool_choice = None
        self.case_created = False

        # Set up the archive cases folder
        self.ensure_archive_cases_folder()

        # Set up logging
        self.setup_logging()

    def ensure_archive_cases_folder(self):
        """Ensure that the 'archive cases' folder exists."""
        folder_path = "archive cases"
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)

    def setup_logging(self):
        """Set up logging for the CLI."""
        if self.current_case_number:
            case_file_name = f"case {self.current_case_number}.txt"
            self.log_file = os.path.join("archive cases", case_file_name)
            if not os.path.exists(self.log_file):
                print(f"Case file {case_file_name} does not exist. Logging will not be set up.")
                self.log_file = None
        else:
            self.log_file = None

        if self.log_file:
            logging.basicConfig(filename=self.log_file, level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')
            logging.info('CaseFileCLI initialized.')

    def list_files_in_archive_cases(self):
        """List all files in the 'archive cases' folder."""
        folder_path = "archive cases"
        if os.path.isdir(folder_path):
            print(f"Files in '{folder_path}':")
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    print(f" - {filename}")
        else:
            print(f"The folder '{folder_path}' does not exist.")

    def do_load(self, line):
        """Load the case file with the specified case number."""
        case_number = input("Enter case number (format XXX-XXX): ").strip()
        if not case_number:
            print("Case number is required.")
            return

        case_file_name = f"case {case_number}.txt"
        case_file_path = os.path.join("archive cases", case_file_name)
        
        if os.path.exists(case_file_path):
            try:
                with open(case_file_path, 'r') as file:
                    content = file.read()
                print(f"Content of '{case_file_name}':\n")
                print(content)
                
                # Update the prompt to reflect the current case number
                self.current_case_number = case_number
                self.prompt = f"case {case_number}> "
                self.case_created = True
                
                # Re-setup logging to use the case-specific file
                self.setup_logging()
                
                # Log the case load event
                if self.log_file:
                    logging.info(f"Loaded case file: {case_file_name}")
                
                # Tool selection menu
                # self.ListOfTools()
                
            except Exception as e:
                print(f"An error occurred while reading the file: {e}")
                if self.log_file:
                    logging.error(f"Error reading file {case_file_name}: {e}")
        else:
            print(f"The case file '{case_file_name}' does not exist in 'archive cases'.")

    def do_tool(self, arg):
        """Select a tool to use."""
        if not self.case_created:
            print("You must create a case before selecting a tool.")
            return

        print("Choose which tool you need:")
        ListOfTools = [
            [1, 'Email'], [2, 'PDF'], [3, 'ISO'], [4, 'OVA'], [5, 'URL'],
            [6, 'JSON'], [7, 'DB'], [8, 'PNG'], [9, 'CODE'], [10, 'EXE / DMG'], [11, 'EVENT VIEWER']
        ]

        for tool in ListOfTools:
            print(f"{tool[0]}: {tool[1]}")

        while True:
            Choice = input("Choose the tool you need or type 'exit' to quit: ")

            if Choice == 'exit':
                print("Bye!")
                if self.current_case_file:
                    self.log_to_case_file("User exited tool selection.")
                break
            elif Choice == "1":
                print("Email Analysis was selected")
                module_path = os.path.join("Tools", "Email_Analysis.py")
                Email_Analysis = self.import_module_from_path("Email_Analysis", module_path)
                Email_Analysis.main()
                self.log_to_case_file("Email Analysis tool selected and executed.")
                break
            elif Choice == "2":
                print("PDF Analysis was selected")
                module_path = os.path.join("Tools", "PDF_Analysis.py")
                PDF_Analysis = self.import_module_from_path("PDF_Analysis", module_path)
                PDF_Analysis.main()
                self.log_to_case_file("PDF Analysis tool selected and executed.")
                break
            elif Choice == "3":
                print("ISO Analysis was selected")
                module_path = os.path.join("Tools", "ISO_Analysis.py")
                ISO_Analysis = self.import_module_from_path("ISO_Analysis", module_path)
                ISO_Analysis.main()
                self.log_to_case_file("ISO Analysis tool selected and executed.")
                break
            elif Choice == "4":
                print("OVA Analysis was selected")
                module_path = os.path.join("Tools", "OVA_Analysis.py")
                OVA_Analysis = self.import_module_from_path("OVA_Analysis", module_path)
                OVA_Analysis.main()
                self.log_to_case_file("OVA Analysis tool selected and executed.")
                break
            elif Choice == "5":
                print("URL Analysis was selected")
                module_path = os.path.join("Tools", "URL_Analysis.py")
                URL_Analysis = self.import_module_from_path("URL_Analysis", module_path)
                URL_Analysis.main()
                self.log_to_case_file("URL Analysis tool selected and executed.")
                break
            elif Choice == "6":
                print("JSON Analysis was selected")
                module_path = os.path.join("Tools", "JSON_Analysis.py")
                JSON_Analysis = self.import_module_from_path("JSON_Analysis", module_path)
                JSON_Analysis.main()
                self.log_to_case_file("JSON Analysis tool selected and executed.")
                break
            elif Choice == "7":
                print("DB was selected")
                module_path = os.path.join("DB","main_DB.py")
                main_DB = self.import_module_from_path("main_DB", module_path)
                main_DB.main()
                self.log_to_case_file("DB was seleceted and executed")
                break
            elif Choice == "8":
                print("PNG Analysis was selected")
                module_path = os.path.join("Tools", "PNG_Analysis.py")
                PNG_Analysis = self.import_module_from_path("PNG_Analysis", module_path)
                PNG_Analysis.main()
                self.log_to_case_file("PNG Analysis tool selected and executed.")
                break
            elif Choice == "9":
                print("CODE Analysis was selected")
                module_path = os.path.join("Tools", "CODE_Analysis.py")
                CODE_Analysis = self.import_module_from_path("CODE_Analysis", module_path)
                CODE_Analysis.main()
                self.log_to_case_file("CODE Analysis tool selected and executed.")
                break
            elif Choice == "10":
                print("EXE / DMG Analysis was selected")
                module_path = os.path.join("Tools", "EXE_DMG_Analysis.py")
                EXE_DMG_Analysis = self.import_module_from_path("EXE_DMG_Analysis", module_path)
                EXE_DMG_Analysis.main()
                self.log_to_case_file("EXE / DMG Analysis tool selected and executed.")
                break
            elif Choice == "11":
                print("EVENT VIEWER Analysis was selected")
                module_path = os.path.join("Tools", "EVENT_VIEWER_Analysis.py")
                EVENT_VIEWER_Analysis = self.import_module_from_path("EVENT_VIEWER_Analysis", module_path)
                EVENT_VIEWER_Analysis.main()
                self.log_to_case_file("EVENT VIEWER Analysis tool selected and executed.")
                break
            else:
                print("Invalid choice. Please try again.")
                self.log_to_case_file("Invalid tool selection attempted.")

    def log_to_case_file(self, message):
        """Log a message to the current case file."""
        if self.log_file:
            logging.info(message)

    def import_module_from_path(self, module_name, module_path):
        """Dynamically import a module from a given path."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def do_note(self, line):
        """Add a note to the specified case file."""
        if not self.current_case_number:
            print("No case is currently loaded. Use 'load' command to load a case.")
            return

        note_text = input("Enter note text: ").strip()
        if not note_text:
            print("Note text is required.")
            return

        note_file_name = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        note_file_path = os.path.join("archive cases", note_file_name)
        
        try:
            with open(note_file_path, 'w') as file:
                file.write(note_text)
            print(f"Note added: {note_file_name}")
            self.log_to_case_file(f"Note added: {note_file_name}")
        except Exception as e:
            print(f"An error occurred while saving the note: {e}")
            if self.log_file:
                logging.error(f"Error saving note {note_file_name}: {e}")

    def do_list(self, line):
        """List all archived cases."""
        self.list_files_in_archive_cases()

    def do_exit(self, line):
        """Exit the CLI."""
        print("Exiting...")
        sys.exit()

    def do_help(self, line):
        """Display help information."""
        help_messages = {
            'list': 'List all archived cases',
            'note': 'Add a note to the current case file',
            'tool': 'Select a tool to analyze the case',
            'exit': 'Exit the CASE sanction system',
            'help': 'Show this help message',
            'load': 'Load an existing case file'
        }
        print("Documented commands (type help <topic>):")
        print("========================================")
        for command, description in sorted(help_messages.items()):
            print(f"{command:<6} - {description}")

if __name__ == '__main__':
    # Adjust the file_path as needed for your use case
    cli = CaseFileCLI(file_path="casefile.txt")
    cli.cmdloop()
