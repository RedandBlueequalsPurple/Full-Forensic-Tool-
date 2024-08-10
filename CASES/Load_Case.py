import cmd
import os
from datetime import datetime
import importlib.util
import logging

class CaseFileCLI(cmd.Cmd):
    prompt = 'casefile> '
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.ensure_archive_cases_folder()
        self.current_case_number = None
        self.log_file = None
        self.current_tool_choice = None

        # Set up logging
        self.setup_logging()

    def ensure_archive_cases_folder(self):
        folder_name = "archive cases"
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)

    def setup_logging(self):
        """Set up logging for the CLI."""
        if self.current_case_number:
            # Determine log file location based on the current case
            case_file_name = f"case {self.current_case_number}.txt"
            case_file_path = os.path.join("archive cases", case_file_name)
            
            # Ensure the case file exists before setting up logging
            if os.path.exists(case_file_path):
                self.log_file = case_file_path
            else:
                print(f"Case file {case_file_name} does not exist. Logging will not be set up.")
                self.log_file = None
        else:
            self.log_file = None

        if self.log_file:
            logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            logging.info('CaseFileCLI initialized.')

    def list_files_in_archive_cases(self):
        """List all files in the 'archive cases' folder."""
        folder_name = "archive cases"
        if os.path.isdir(folder_name):
            print(f"Files in '{folder_name}':")
            for filename in os.listdir(folder_name):
                file_path = os.path.join(folder_name, filename)
                if os.path.isfile(file_path):
                    print(f" - {filename}")
        else:
            print(f"The folder '{folder_name}' does not exist.")

    def do_load(self, line):
        """
        Load the case file with the specified case number.
        Usage: load
        """
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
                
                # Re-setup logging to use the case-specific file
                self.setup_logging()
                
                # Log the case load event
                if self.log_file:
                    logging.info(f"Loaded case file: {case_file_name}")
                
                # Tool selection menu
                self.show_tool_menu()
                
            except Exception as e:
                print(f"An error occurred while reading the file: {e}")
                if self.log_file:
                    logging.error(f"Error reading file {case_file_name}: {e}")
        else:
            print(f"The case file '{case_file_name}' does not exist in 'archive cases'.")

    def do_select_tool(self, line):
        """
        Select a tool to execute.
        Usage: select_tool
        """
        if not self.current_case_number:
            print("No case is currently loaded.")
            return

        self.show_tool_menu()

    def show_tool_menu(self):
        """Display tool selection menu and handle user choice."""
        print("Choose which tool you need:")
        list_of_tools = [
            [1, 'Email'], [2, 'PDF'], [3, 'ISO'], [4, 'OVA'], [5, 'URL'],
            [6, 'JSON'], [7, 'DB'], [8, 'PNG'], [9, 'CODE'], [10, 'EXE / DMG'], [11, 'EVENT VIEWER']
        ]

        for tool in list_of_tools:
            print(f"{tool[0]}: {tool[1]}")

        while True:
            choice = input("Choose the tool you need or type 'exit' to quit: ").strip()

            if choice == 'exit':
                print("Bye!")
                if self.log_file:
                    logging.info("Exiting CLI.")
                break
            elif choice in [str(tool[0]) for tool in list_of_tools]:
                self.current_tool_choice = int(choice)
                self.handle_tool_choice(self.current_tool_choice)
                break
            else:
                print("Invalid choice. Please select a valid tool.")
                if self.log_file:
                    logging.warning(f"Invalid tool choice: {choice}")

    def handle_tool_choice(self, choice):
        """Handle the tool choice and execute the corresponding module."""
        tool_map = {
            1: 'Email_Analysis',
            2: 'PDF_Analysis',
            3: 'ISO_Analysis',
            4: 'OVA_Analysis',
            5: 'URL_Analysis',
            6: 'JSON_Analysis',
            7: 'main_DB',
            8: 'PNG_Analysis',
            9: 'CODE_Analysis',
            10: 'EXE_DMG_Analysis',
            11: 'Event_Viewer'
        }

        tool_name = tool_map.get(choice)
        if tool_name:
            print(f"{tool_name.replace('_', ' ')} was selected")
            module_path = os.path.join("Tools" if choice != 7 else "DB", f"{tool_name}.py")
            module = self.import_module_from_path(tool_name, module_path)
            if module:
                module.main()
                if self.log_file:
                    logging.info(f"Executed tool: {tool_name}")
        else:
            print("An error occurred: Tool not found.")
            if self.log_file:
                logging.error(f"Tool not found for choice: {choice}")

    def import_module_from_path(self, module_name, module_path):
        """Import a module from a specific path."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"An error occurred while importing the module: {e}")
            if self.log_file:
                logging.error(f"Error importing module {module_name}: {e}")
            return None

    def do_note(self, line):
        """
        Add a note to the specified case file.
        Usage: note <case_number>
        """
        if not self.current_case_number:
            print("No case is currently loaded.")
            return
        
        investigator = input("Enter the name of the investigator: ").strip()
        if not investigator:
            print("Name of the investigator is required.")
            return
        
        note = input("Enter your note: ").strip()
        if not note:
            print("Note cannot be empty.")
            return

        note_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        case_file_name = f"case {self.current_case_number}.txt"
        case_file_path = os.path.join("archive cases", case_file_name)
        
        try:
            if os.path.exists(case_file_path):
                with open(case_file_path, 'a') as file:
                    file.write(f"\n\nNote Added on {note_date}\nInvestigator: {investigator}\nNote: {note}")
                print(f"Note added to {case_file_path} successfully.")
                if self.log_file:
                    logging.info(f"Note added to case file {case_file_name} by {investigator}.")
            else:
                print(f"The case file '{case_file_name}' does not exist in 'archive cases'.")
        
        except Exception as e:
            print(f"An error occurred: {e}")
            if self.log_file:
                logging.error(f"Error adding note to case file {case_file_name}: {e}")

    def do_list_cases(self, line):
        """
        List all files in the 'archive cases' folder.
        Usage: list_cases
        """
        self.list_files_in_archive_cases()

    def do_exit(self, line):
        """Exit the CLI."""
        print("Exiting CLI.")
        if self.log_file:
            logging.info("CLI exited.")
        return True

    def do_help(self, line):
        """Display help information for available commands."""
        commands = {
            'load': 'Load the case file with the specified case number.',
            'select_tool': 'Select and execute a tool after loading a case file.',
            'note': 'Add a note to the specified case file.',
            'list_cases': 'List all files in the "archive cases" folder.',
            'exit': 'Exit the CLI.',
            'help': 'Display help information for available commands.'
        }
        if line:
            if line in commands:
                print(f"{line}: {commands[line]}")
            else:
                print(f"No help available for {line}.")
        else:
            print("Documented commands (type help <topic>):")
            print("========================================\n")
            for cmd in commands:
                print(f"{cmd:<12} - {commands[cmd]}\n")

    def format_case_number(self, case_number):
        """
        Format the case number to include the 'case' prefix.
        """
        return f"Case {case_number}"

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'your_file.txt')

    cli = CaseFileCLI(file_path)
    cli.cmdloop()
