import os
import re
import cmd
import importlib.util
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
import colorama
colorama.init(autoreset=True)

# Initialize the console for rich output
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
            [1, 'Email'], [2, 'PDF'], [3, 'ISO'], [4, 'OVA'], [5, 'URL'],
            [6, 'JSON'], [7, 'DB'], [8, 'PNG'], [9, 'CODE'], [10, 'EXE / DMG'], [11, 'EVENT VIEWER']
        ]

        for tool in ListOfTools:
            console.print(f"{tool[0]}: {tool[1]}")

        while True:
            Choice = input("Choose the tool you need or type 'exit' to quit: ")

            if Choice == 'exit':
                console.print("Bye!", style="bold red")
                if self.current_case_file:
                    self.log_to_case_file("User exited tool selection.")
                break
            elif Choice == "1":
                self.select_tool("Email Analysis", "Case_Section/Case_Tools", "Email_Analysis.py")
                break
            elif Choice == "2":
                self.select_tool("PDF Analysis", "Case_Section/Case_Tools", "PDF_Analysis.py")
                break
            elif Choice == "3":
                self.select_tool("ISO Analysis", "Case_Section/Case_Tools", "ISO_Analysis.py")
                break
            elif Choice == "4":
                self.select_tool("OVA Analysis", "Case_Section/Case_Tools", "OVA_Analysis.py")
                break
            elif Choice == "5":
                self.select_tool("URL Analysis", "Case_Section/Case_Tools", "URL_Analysis.py")
                break
            elif Choice == "6":
                self.select_tool("JSON Analysis", "Case_Section/Case_Tools", "JSON_Analysis.py")
                break
            elif Choice == "7":
                self.select_tool("DB", "Case_Section/Case_DB", "main_DB.py")
                break
            elif Choice == "8":
                self.select_tool("PNG Analysis", "Case_Section/Case_Tools", "PNG_Analysis.py")
                break
            elif Choice == "9":
                self.select_tool("CODE Analysis", "Case_Section/Case_Tools", "CODE_Analysis.py")
                break
            elif Choice == "10":
                self.select_tool("EXE / DMG Analysis", "Case_Section/Case_Tools", "EXE_DMG_Analysis.py")
                break
            elif Choice == "11":
                self.select_tool("EVENT VIEWER Analysis", "Case_Section/Case_Tools", "EVENT_VIEWER_Analysis.py")
                break
            else:
                console.print("Invalid choice, please select again.", style="bold yellow")

    def select_tool(self, tool_name, tool_dir, tool_script):
        """Helper method to select and run a tool."""
        console.print(f"{tool_name} was selected", style="bold cyan")
        module_path = os.path.join(tool_dir, tool_script)
        try:
            tool_module = self.import_module_from_path(tool_name.replace(" ", "_"), module_path)
            tool_module.main()
            self.log_to_case_file(f"{tool_name} tool selected and executed.")
        except FileNotFoundError:
            console.print(f"[red]Error: The script '{tool_script}' was not found in the '{tool_dir}' directory.[/red]")
            self.log_to_case_file(f"Error: {tool_name} script not found.")
        except AttributeError:
            console.print(f"[red]Error: The '{tool_name}' script does not have a 'main' function.[/red]")
            self.log_to_case_file(f"Error: {tool_name} script lacks 'main' function.")
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
        case_files = [f for f in files if f.startswith("case ") and f.endswith(".txt")]
        if case_files:
            case_table = Table(title="Archived Cases", box=None)
            case_table.add_column("Case Number", style="bold magenta")
            for case_file in sorted(case_files):
                case_number = case_file.split('.')[0]
                case_table.add_row(case_number)
            console.print(case_table)
        else:
            console.print("[yellow]No archived cases found.[/yellow]")

    def do_note(self, arg):
        """Add a note to the current case file."""
        if not self.case_created:
            console.print("[red]You must create a case before adding a note.[/red]")
            return

        investigator_name = input("Enter the investigator's name: ")
        note = input("Enter your note: ")

        self.log_to_case_file(f"Note added by {investigator_name}: {note}")

    def do_exit(self, arg):
        """Exit the Case Manager CLI."""
        console.print("Thank you for using the Case Manager CLI. Goodbye!", style="bold red")
        return True

    def import_module_from_path(self, module_name, module_path):
        """Dynamically import a module from the given file path."""
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Module file '{module_path}' does not exist.")

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

if __name__ == '__main__':
    CaseManager().cmdloop()
