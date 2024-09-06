import os
import re
from datetime import datetime
import cmd
import sys
import importlib.util
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Initialize console for Rich
console = Console()

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
        console.print(Panel("Please enter the following details:", title="Input", subtitle="Case Details"))

        # Collect and format additional fields
        while True:
            try:
                date_input = input("Date (DD-MM-YYYY): ")
                # Parse the entered date and format it as YYYY-MM-DD
                date_obj = datetime.strptime(date_input, "%d-%m-%Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                break
            except ValueError:
                console.print("[red]Invalid date format. Please enter the date as 'DD-MM-YYYY' (e.g., '10-08-2024').[/red]")

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
        console.print(f"Prompt updated to '{self.prompt}'.", style="bold green")

        # Log user data addition
        self.log_to_case_file("User data added.")

    def do_new(self, arg):
        """Create a new case file."""
        self.create_next_case_file()

    def do_tool(self, arg):
        """Select a tool to use."""
        if not self.case_created:
            console.print("[red]You must create a case before selecting a tool.[/red]")
            return

        console.print(Panel("Choose which tool you need:", title="Tool Selection"))

        ListOfTools = [
            [1, 'Email Analysis', "Case_Section/Case_Tools", "Email_Analysis.py"],
            [2, 'PDF Analysis', "Case_Section/Case_Tools", "PDF_Analysis.py"],
            [3, 'ISO Analysis', "Case_Section/Case_Tools", "ISO_Analysis.py"],
            [4, 'OVA Analysis', "Case_Section/Case_Tools", "OVA_Analysis.py"],
            [5, 'URL Analysis', "Case_Section/Case_Tools", "URL_Analysis.py"],
            [6, 'JSON Analysis', "Case_Section/Case_Tools", "JSON_Analysis.py"],
            [7, 'main_DB', "Case_Section/CASES/Case_DB", "main_DB.py"],
            [8, 'IMAGE Analysis', "Case_Section/Case_Tools", "IMAGE_Analysis.py"],
            [9, 'CODE Analysis', "Case_Section/Case_Tools", "CODE_Analysis.py"],
            [10, 'EXE / DMG Analysis', "Case_Section/Case_Tools", "EXE_DMG_Analysis.py"],
            [11, 'EVENT VIEWER', "Case_Section/Case_Tools", "EVENT_VIEWER_Analysis.py"]
        ]

        for tool in ListOfTools:
            console.print(f"{tool[0]}: {tool[1]}")

        while True:
            Choice = input("Choose the tool you need or type 'exit' to quit: ")

            if Choice == 'exit':
                console.print("Exiting tool selection...", style="bold red")
                if self.current_case_file:
                    self.log_to_case_file("User exited tool selection.")
                break
            for tool in ListOfTools:
                if Choice == str(tool[0]):
                    self.select_tool(tool[1], tool[2], tool[3])
                    break
            else:
                console.print("Invalid choice, please select again.", style="bold yellow")

    def do_exit(self, arg):
        """Exit the CLI."""
        console.print("Exiting the Case Manager CLI. Goodbye!", style="bold red")
        if self.current_case_file:
            self.log_to_case_file("User exited the CLI.")
        return True  # Return True to exit cmdloop

    def select_tool(self, tool_name, tool_dir, tool_script):
        """Helper method to select and run a tool."""
        console.print(f"{tool_name} was selected", style="bold cyan")
        module_path = os.path.join(tool_dir, tool_script)
        console.print(f"Looking for module at: {module_path}", style="bold yellow")

        try:
            # Ensure the tool directory is in the sys.path
            if tool_dir not in sys.path:
                sys.path.append(os.path.abspath(tool_dir))
            # Update module name for the import statement
            module_name = os.path.splitext(tool_script)[0]
            tool_module = self.import_module_from_path(module_name, module_path)
            
            # Check if the 'main' function exists in the module
            if hasattr(tool_module, 'main') and callable(getattr(tool_module, 'main')):
                tool_module.main()
                self.log_to_case_file(f"{tool_name} tool selected and executed.")
            else:
                raise AttributeError(f"The '{tool_name}' script does not have a callable 'main' function.")
            
        except FileNotFoundError:
            console.print(f"[red]Error: The script '{tool_script}' was not found in the '{tool_dir}' directory.[/red]")
            self.log_to_case_file(f"Error: {tool_name} script not found.")
        except AttributeError as e:
            console.print(f"[red]Error: {e}[/red]")
            self.log_to_case_file(f"Error: {e}")
        except Exception as e:
            console.print(f"[red]An unexpected error occurred while running the '{tool_name}' tool: {e}[/red]")
            self.log_to_case_file(f"Unexpected error in {tool_name}: {e}")

    def do_help(self, arg):
        """Display help information"""
        if arg:
            cmd.Cmd.do_help(self, arg)
        else:
            # Create a table to display the help information
            help_table = Table(title="Available Commands", box=None)
            help_table.add_column("Command", style="bold magenta")
            help_table.add_column("Description", style="bold white")
            help_table.add_row("new", "Create a new case")
            help_table.add_row("list", "List all archived cases")
            help_table.add_row("note", "Add a note to the current case file")
            help_table.add_row("tool", "Select a tool to analyze the case")
            help_table.add_row("exit", "Exit the CASE system")
            help_table.add_row("help", "Show this help message")

            console.print(help_table)

    def do_list(self, arg):
        """List all archived cases."""
        files = os.listdir(self.archive_folder)
        case_files = [f for f in files if f.endswith(".txt")]
        if case_files:
            console.print(Panel(f"Archived Cases:\n" + "\n".join(case_files), title="Case Files"))
        else:
            console.print("No case files found.", style="bold yellow")

    def import_module_from_path(self, module_name, module_path):
        """Import a module from a given file path."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

if __name__ == '__main__':
    CaseManager().cmdloop()
