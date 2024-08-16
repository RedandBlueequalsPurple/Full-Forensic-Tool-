import os
import re
import cmd
import importlib.util
import sys
from datetime import datetime

class CaseManager(cmd.Cmd):
    intro = "Welcome to the Case Manager CLI. Type 'help' or '?' to list commands."
    prompt = '> '

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

    def log_to_case_file(self, message):
        """Log a message to the current case file."""
        if self.current_case_file:
            with open(self.current_case_file, 'a') as file:
                file.write(f"{datetime.now()} - {message}\n")

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

        self.current_case_file = new_file_path
        self.log_to_case_file("Case file created.")
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

        # Update prompt to reflect the new case number
        case_number = os.path.basename(file_path).split('.')[0]
        self.prompt = f"{case_number}> "
        print(f"Prompt updated to '{self.prompt}'.")

        # Log user data addition
        self.log_to_case_file("User data added.")

    def do_create(self, arg):
        """Create a new case file."""
        self.create_next_case_file()

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
                db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "DB"))  # Correct path to DB folder
                sys.path.append(db_path)  # Add the DB path to sys.path

                try:
                    import main_DB  # Import the main_DB module
                    main_DB.DBCLI().cmdloop()  # This will start the CLI for the DB tool
                except ImportError as e:
                    print(f"Error importing main_DB: {e}")
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

    def do_list_cases(self, arg):
        """List all cases in the archive folder."""
        if not os.path.isdir(self.archive_folder):
            print("No cases found.")
            return

        files = os.listdir(self.archive_folder)
        cases = [file for file in files if file.startswith("case") and file.endswith(".txt")]

        if cases:
            print("Archived Cases:")
            for case in cases:
                print(case)
        else:
            print("No cases found.")

    def do_note(self, arg):
        """Add a note to the current case file."""
        if not self.current_case_file:
            print("No case file is currently selected.")
            return

        investigator_name = input("Name of the Investigator: ")
        note = input("Enter your note: ")

        with open(self.current_case_file, 'a') as file:
            file.write(f"{datetime.now()} - Investigator: {investigator_name}\n")
            file.write(f"Note: {note}\n\n")

        print("Note added.")
        self.log_to_case_file(f"Note added by {investigator_name}.")

    def do_exit(self, arg):
        """Exit the Case Manager CLI."""
        print("Goodbye!")
        return True

    def do_new(self, arg):
        """Create a new case file."""
        self.create_next_case_file()

    def import_module_from_path(self, module_name, module_path):
        """Dynamically import a module from a given path."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def do_help(self, arg):
        """Display the help message."""
        if arg:
            try:
                func = getattr(self, 'do_' + arg)
                func.__doc__ and print(f"{arg}: {func.__doc__}")
            except AttributeError:
                print(f"No help available for '{arg}'")
        else:
            print("Available commands:")
            print(" new    - Create a new case")
            print(" list   - List all archived cases")
            print(" note   - Add a note to the current case file")
            print(" tool   - Select a tool to analyze the case")
            print(" exit   - Exit the CASE sanction system")
            print(" help   - Show this help message")


if __name__ == '__main__':
    CaseManager().cmdloop()
