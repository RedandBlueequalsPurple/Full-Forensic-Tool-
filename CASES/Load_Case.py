import cmd
import os
from datetime import datetime

class CaseFileCLI(cmd.Cmd):
    prompt = 'casefile> '
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.ensure_archive_cases_folder()
        self.current_case_number = None

    def ensure_archive_cases_folder(self):
        folder_name = "archive cases"
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)

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
            except Exception as e:
                print(f"An error occurred while reading the file: {e}")
        else:
            print(f"The case file '{case_file_name}' does not exist in 'archive cases'.")

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
            else:
                print(f"The case file '{case_file_name}' does not exist in 'archive cases'.")
        
        except Exception as e:
            print(f"An error occurred: {e}")

    def do_list_cases(self, line):
        """
        List all files in the 'archive cases' folder.
        Usage: list_cases
        """
        self.list_files_in_archive_cases()

    def do_exit(self, line):
        """Exit the CLI."""
        print("Exiting CLI.")
        return True

    def do_help(self, line):
        """Display help information for available commands."""
        commands = {
            'load': 'Load the case file with the specified case number.',
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
