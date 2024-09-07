import cmd
import os
import re
from datetime import datetime
import importlib.util
import logging
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import colorama


colorama.init(autoreset=True)

class CaseFileCLI(cmd.Cmd):
    prompt = 'casefile> '
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.current_case_number = None
        self.log_file = None
        self.current_tool_choice = None
        self.case_created = False
        self.console = Console()
        self.archive_folder = "archive cases"
        self.ensure_archive_cases_folder()
        self.setup_logging()

    def ensure_archive_cases_folder(self):
        """Ensure that the 'archive cases' folder exists."""
        if not os.path.isdir(self.archive_folder):
            os.makedirs(self.archive_folder)

    def setup_logging(self):
        """Set up logging for the CLI."""
        if self.current_case_number:
            case_file_name = f"case {self.current_case_number}.txt"
            self.log_file = os.path.join(self.archive_folder, case_file_name)
            if not os.path.exists(self.log_file):
                self.console.print(f"[red]Case file {case_file_name} does not exist. Logging will not be set up.[/red]")
                self.log_file = None
        else:
            self.log_file = None

        if self.log_file:
            logging.basicConfig(filename=self.log_file, level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')
            logging.info('CaseFileCLI initialized.')

    def log_to_case_file(self, message):
        """Log a message to the current case file."""
        if self.log_file:
            logging.info(message)

    def add_user_data(self, file_path):
        """Prompt the user to enter data and append it to the file."""
        self.console.print(Panel("Please enter the following details:", title="Input", subtitle="Case Details"))

        # Collect and format additional fields
        while True:
            try:
                date_input = input("Date (DD-MM-YYYY): ")
                date_obj = datetime.strptime(date_input, "%d-%m-%Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                break
            except ValueError:
                self.console.print("[red]Invalid date format. Please enter the date as 'DD-MM-YYYY' (e.g., '10-08-2024').[/red]")

        investigator_name = input("Name of the Investigator: ")
        case_description = input("Description of the Case: ")

        with open(file_path, 'a') as file:
            file.write(f"Date: {formatted_date}\n")
            file.write(f"Name of the Investigator: {investigator_name}\n")
            file.write(f"Description of the Case: {case_description}\n")
            file.write("\nUser Data:\n")

        # Update prompt to reflect the new case number
        self.prompt = f"case {self.current_case_number}> "
        self.console.print(f"Prompt updated to '{self.prompt}'.", style="bold green")

        # Log user data addition
        self.log_to_case_file("User data added.")

    def do_load(self, line):
        """Load the case file with the specified case number."""
        case_number = input("Enter case number (format XXX-XXX): ").strip()
        if not case_number:
            self.console.print("[red]Case number is required.[/red]")
            return

        case_file_name = f"case {case_number}.txt"
        case_file_path = os.path.join(self.archive_folder, case_file_name)
        
        if os.path.exists(case_file_path):
            try:
                with open(case_file_path, 'r') as file:
                    content = file.read()
                self.console.print(f"[bold]Content of '{case_file_name}':[/bold]\n")
                self.console.print(content)
                
                # Update the prompt to reflect the current case number
                self.current_case_number = case_number
                self.prompt = f"case {case_number}> "
                self.case_created = True
                
                # Re-setup logging to use the case-specific file
                self.setup_logging()
                
                # Log the case load event
                if self.log_file:
                    logging.info(f"Loaded case file: {case_file_name}")
                
            except Exception as e:
                self.console.print(f"[red]An error occurred while reading the file: {e}[/red]")
                if self.log_file:
                    logging.error(f"Error reading file {case_file_name}: {e}")
        else:
            self.console.print(f"[red]The case file '{case_file_name}' does not exist in 'archive cases'.[/red]")

    def do_tool(self, arg):
        """Select a tool to use."""
        if not self.case_created:
            self.console.print("[red]You must create a case before selecting a tool.[/red]")
            return

        self.console.print(Panel("Choose which tool you need:", title="Tool Selection"))

        ListOfTools = [
            [1, 'Email Analysis', "Case_Section/Case_Tools", "Email_Analysis.py"],
            [2, 'PDF Analysis', "Case_Section/Case_Tools", "PDF_Analysis.py"],
            [3, 'ISO Analysis', "Case_Section/Case_Tools", "ISO_Analysis.py"],
            [4, 'OVA Analysis', "Case_Section/Case_Tools", "OVA_Analysis.py"],
            [5, 'URL Analysis', "Case_Section/Case_Tools", "URL_Analysis.py"],
            [6, 'JSON Analysis', "Case_Section/Case_Tools", "JSON_Analysis.py"],
            [7, 'DB', "Case_Section/CASES/Case_DB", "main_DB.py"],
            [8, 'IMAGE Analysis', "Case_Section/Case_Tools", "IMAGE_Analysis.py"],
            [9, 'CODE Analysis', "Case_Section/Case_Tools", "CODE_Analysis.py"],
            [10, 'EXE / DMG Analysis', "Case_Section/Case_Tools", "EXE_DMG_Analysis.py"],
            [11, 'EVENT VIEWER', "Case_Section/Case_Tools", "EVENT_VIEWER_Analysis.py"]
        ]

        for tool in ListOfTools:
            self.console.print(f"{tool[0]}: {tool[1]}")

        while True:
            Choice = input("Choose the tool you need or type 'exit' to quit: ")

            if Choice == 'exit':
                self.console.print("Bye!", style="bold red")
                if self.current_case_number:
                    self.log_to_case_file("User exited tool selection.")
                break
            for tool in ListOfTools:
                if Choice == str(tool[0]):
                    self.select_tool(tool[1], tool[2], tool[3])
                    break
            else:
                self.console.print("Invalid choice, please select again.", style="bold yellow")

    def select_tool(self, tool_name, tool_dir, tool_script):
        """Helper method to select and run a tool."""
        self.console.print(f"{tool_name} was selected", style="bold cyan")
        module_path = os.path.join(tool_dir, tool_script)
        try:
            tool_module = self.import_module_from_path(tool_name.replace(" ", "_"), module_path)
            tool_module.main()
            self.log_to_case_file(f"{tool_name} tool selected and executed.")
        except FileNotFoundError:
            self.console.print(f"[red]The script for {tool_name} does not exist.[/red]")
        except Exception as e:
            self.console.print(f"[red]Error executing tool: {e}[/red]")

    def import_module_from_path(self, module_name, file_path):
        """Dynamically import a module from a given file path."""
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def do_list_cases(self, line):
        """List all case files in the archive cases folder."""
        files = os.listdir(self.archive_folder)
        case_files = [f for f in files if f.endswith('.txt')]
        if not case_files:
            self.console.print("[red]No case files found in the archive cases folder.[/red]")
            return

        table = Table(title="List of Case Files")
        table.add_column("Case Number", style="bold cyan")
        table.add_column("File Name", style="dim")

        for case_file in case_files:
            case_number = case_file.split(' ')[1].split('.')[0]
            table.add_row(case_number, case_file)

        self.console.print(table)

    def do_note(self, arg):
        """Add a note to the current case file."""
        if not self.case_created:
            self.console.print("[red]No case created. Please create a case before adding notes.[/red]")
            return

        note = input("Enter your note: ")
        if note:
            with open(self.log_file, 'a') as file:
                file.write(f"NOTE: {note}\n")
            self.console.print(f"Note added to case file.")
            self.log_to_case_file(f"Note added: {note}")

    def do_help(self, arg):
        """Display help message."""
        self.console.print(Panel("Available Commands:", title="Help", subtitle="Commands Overview"))

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Command", style="bold green")
        table.add_column("Description", style="dim")

        commands = [
            ('load', 'Load an existing case file'),
            ('list_cases', 'List all case files in archive cases'),
            ('note', 'Add a note to the current case file'),
            ('tool', 'Select a tool to use'),
            ('help', 'Display this help message'),
            ('exit', 'Exit the CaseFileCLI')
        ]

        for command, description in commands:
            table.add_row(command, description)

        self.console.print(table)

    def do_exit(self, arg):
        """Exit the CLI."""
        self.console.print("Exiting CaseFileCLI. Goodbye!", style="bold red")
        if self.current_case_number:
            self.log_to_case_file("User exited CLI.")
        return True

if __name__ == '__main__':
    file_path = "path_to_your_file.txt"  # Replace with actual file path
    cli = CaseFileCLI(file_path)
    cli.cmdloop()
