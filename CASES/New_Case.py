import os
import re
import cmd
import importlib.util
import sys
from datetime import datetime

class CaseManager(cmd.Cmd):
    prompt = '> '
    intro = "Welcome to the Case Manager CLI. Type 'help' or '?' to list commands."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.archive_folder = "archive cases"
        self.ensure_archive_cases_folder()
        self.current_case_file = None
        self.case_created = False  # Flag to track case creation

    def ensure_archive_cases_folder(self):
        """Ensure that the 'archive cases' folder exists."""
        if not os.path.isdir(self.archive_folder):
            os.makedirs(self.archive_folder)
            print(f"Folder '{self.archive_folder}' created.")
        else:
            print(f"Folder '{self.archive_folder}' already exists.")

    def create_next_case_file(self):
        """Create a new case file with an incremented number."""
        if not os.path.isdir(self.archive_folder):
            os.makedirs(self.archive_folder)

        files = os.listdir(self.archive_folder)
        pattern = re.compile(r'case (\d{3}-\d{3})\.txt')
        highest_number = 0
        for file in files:
            match = pattern.search(file)
            if match:
                number = match.group(1)
                num = int(number.replace('-', ''))
                if num > highest_number:
                    highest_number = num

        new_number = highest_number + 1
        new_filename = f"case {new_number // 1000:03d}-{new_number % 1000:03d}.txt"
        new_file_path = os.path.join(self.archive_folder, new_filename)

        with open(new_file_path, 'w') as file:
            file.write(f"Case Number: {new_number // 1000:03d}-{new_number % 1000:03d}\n")
            file.write("User Data:\n")

        print(f"File '{new_filename}' created in folder '{self.archive_folder}'.")
        self.current_case_file = new_file_path
        self.add_user_data(new_file_path)
        self.case_created = True  # Set flag to indicate a case has been created

    def add_user_data(self, file_path):
        """Prompt the user to enter data and append it to the file."""
        print("Please enter the following details:")

        # Collect and format additional fields
        while True:
            try:
                date_input = input("Date (DD-MM-YYYY): ")
                # Parse the entered date and format it as YYYY-MM-DD
                date_obj = datetime.strptime(date_input, "%d-%m-%Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format. Please enter the date as 'DD-MM-YYYY' (e.g., '10-08-2024').")

        investigator_name = input("Name of the Investigator: ")
        case_description = input("Description of the Case: ")

        with open(file_path, 'a') as file:
            file.write(f"Date: {formatted_date}\n")
            file.write(f"Name of the Investigator: {investigator_name}\n")
            file.write(f"Description of the Case: {case_description}\n")
            file.write("\nUser Data:\n")
        
        print(f"Data added to '{file_path}'.")

        # Update prompt to reflect the new case number
        case_number = os.path.basename(file_path).split('.')[0]
        self.prompt = f"{case_number}> "
        print(f"Prompt updated to '{self.prompt}'.")

    def do_create(self, arg):
        """Create a new case file."""
        self.create_next_case_file()

    def do_exit(self, arg):
        """Exit the CLI."""
        print("Exiting Case Manager CLI.")
        return True

    def import_module_from_path(self, module_name, module_path):
        """Import a module from a specified file path."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def do_select_tool(self, arg):
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
                break
            elif Choice == "1":
                print("Email Analysis was selected")
                module_path = os.path.join("Tools", "Email_Analysis.py")
                Email_Analysis = self.import_module_from_path("Email_Analysis", module_path)
                Email_Analysis.main()
                break
            elif Choice == "2":
                print("PDF Analysis was selected")
                module_path = os.path.join("Tools", "PDF_Analysis.py")
                PDF_Analysis = self.import_module_from_path("PDF_Analysis", module_path)
                PDF_Analysis.main()
                break
            elif Choice == "3":
                print("ISO Analysis was selected")
                module_path = os.path.join("Tools", "ISO_Analysis.py")
                ISO_Analysis = self.import_module_from_path("ISO_Analysis", module_path)
                ISO_Analysis.main()
                break
            elif Choice == "4":
                print("OVA Analysis was selected")
                module_path = os.path.join("Tools", "OVA_Analysis.py")
                OVA_Analysis = self.import_module_from_path("OVA_Analysis", module_path)
                OVA_Analysis.main()
                break
            elif Choice == "5":
                print("URL Analysis was selected")
                module_path = os.path.join("Tools", "URL_Analysis.py")
                URL_Analysis = self.import_module_from_path("URL_Analysis", module_path)
                URL_Analysis.main()
                break
            elif Choice == "6":
                print("JSON Analysis was selected")
                module_path = os.path.join("Tools", "JSON_Analysis.py")
                JSON_Analysis = self.import_module_from_path("JSON_Analysis", module_path)
                JSON_Analysis.main()
                break
            elif Choice == "7":
                print("DB was selected")
                module_path = os.path.join("DB", "main_DB.py")
                main_DB = self.import_module_from_path("main_DB", module_path)
                main_DB.main()
                break
            elif Choice == "8":
                print("PNG Analysis was selected")
                module_path = os.path.join("Tools", "PNG_Analysis.py")
                PNG_Analysis = self.import_module_from_path("PNG_Analysis", module_path)
                PNG_Analysis.main()
                break
            elif Choice == "9":
                print("CODE Analysis was selected")
                module_path = os.path.join("Tools", "CODE_Analysis.py")
                CODE_Analysis = self.import_module_from_path("CODE_Analysis", module_path)
                CODE_Analysis.main()
                break
            elif Choice == "10":
                print("EXE / DMG Analysis was selected")
                module_path = os.path.join("Tools", "EXE_DMG_Analysis.py")
                EXE_DMG_Analysis = self.import_module_from_path("EXE_DMG_Analysis", module_path)
                EXE_DMG_Analysis.main()
                break
            elif Choice == "11":
                print("EVENT VIEWER was selected")
                module_path = os.path.join("Tools", "Event_Viewer.py")
                Event_Viewer = self.import_module_from_path("Event_Viewer", module_path)
                Event_Viewer.main()
                break
            else:
                print("Invalid choice. Please select a valid tool.")

if __name__ == '__main__':
    CaseManager().cmdloop()
