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
                console.print("Email Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "Email_Analysis.py")
                Email_Analysis = self.import_module_from_path("Email_Analysis", module_path)
                Email_Analysis.main()
                self.log_to_case_file("Email Analysis tool selected and executed.")
                break
            elif Choice == "2":
                console.print("PDF Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "PDF_Analysis.py")
                PDF_Analysis = self.import_module_from_path("PDF_Analysis", module_path)
                PDF_Analysis.main()
                self.log_to_case_file("PDF Analysis tool selected and executed.")
                break
            elif Choice == "3":
                console.print("ISO Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "ISO_Analysis.py")
                ISO_Analysis = self.import_module_from_path("ISO_Analysis", module_path)
                ISO_Analysis.main()
                self.log_to_case_file("ISO Analysis tool selected and executed.")
                break
            elif Choice == "4":
                console.print("OVA Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "OVA_Analysis.py")
                OVA_Analysis = self.import_module_from_path("OVA_Analysis", module_path)
                OVA_Analysis.main()
                self.log_to_case_file("OVA Analysis tool selected and executed.")
                break
            elif Choice == "5":
                console.print("URL Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "URL_Analysis.py")
                URL_Analysis = self.import_module_from_path("URL_Analysis", module_path)
                URL_Analysis.main()
                self.log_to_case_file("URL Analysis tool selected and executed.")
                break
            elif Choice == "6":
                console.print("JSON Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "JSON_Analysis.py")
                JSON_Analysis = self.import_module_from_path("JSON_Analysis", module_path)
                JSON_Analysis.main()
                self.log_to_case_file("JSON Analysis tool selected and executed.")
                break
            elif Choice == "7":
                console.print("DB was selected", style="bold cyan")
                module_path = os.path.join("DB", "main_DB.py")
                main_DB = self.import_module_from_path("main_DB", module_path)
                main_DB.main()
                self.log_to_case_file("DB was selected and executed")
                break
            elif Choice == "8":
                console.print("PNG Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "PNG_Analysis.py")
                PNG_Analysis = self.import_module_from_path("PNG_Analysis", module_path)
                PNG_Analysis.main()
                self.log_to_case_file("PNG Analysis tool selected and executed.")
                break
            elif Choice == "9":
                console.print("CODE Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "CODE_Analysis.py")
                CODE_Analysis = self.import_module_from_path("CODE_Analysis", module_path)
                CODE_Analysis.main()
                self.log_to_case_file("CODE Analysis tool selected and executed.")
                break
            elif Choice == "10":
                console.print("EXE / DMG Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "EXE_DMG_Analysis.py")
                EXE_DMG_Analysis = self.import_module_from_path("EXE_DMG_Analysis", module_path)
                EXE_DMG_Analysis.main()
                self.log_to_case_file("EXE / DMG Analysis tool selected and executed.")
                break
            elif Choice == "11":
                console.print("EVENT VIEWER Analysis was selected", style="bold cyan")
                module_path = os.path.join("Tools", "EVENT_VIEWER_Analysis.py")
                EVENT_VIEWER_Analysis = self.import_module_from_path("EVENT_VIEWER_Analysis", module_path)
                EVENT_VIEWER_Analysis.main()
                self.log_to_case_file("EVENT VIEWER Analysis tool selected and executed.")
                break
            else:
                console.print("Invalid choice, please select again.", style="bold yellow")

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
        if not self.current_case_file:
            console.print("[red]No case file created. Please create a case first.[/red]")
            return

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        investigator_name = input("Name of the Investigator: ")
        note_text = input("Note: ")
        with open(self.current_case_file, 'a') as file:
            file.write(f"\n{date_str} - Note by {investigator_name}: {note_text}\n")
        console.print("[green]Note added to the case file.[/green]")
        self.log_to_case_file(f"Note added: {note_text}")

    def import_module_from_path(self, module_name, module_path):
        """Dynamically import a module from a file path."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def do_exit(self, arg):
        """Exit the CLI."""
        console.print("Bye!", style="bold red")
        return True

if __name__ == "__main__":
    CaseManager().cmdloop()
