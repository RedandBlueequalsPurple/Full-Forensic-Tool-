import cmd
import os
from datetime import datetime
import importlib.util
import logging
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
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
                self.console.print(f"[red]Case file {case_file_name} does not exist. Logging will not be set up.[/red]")
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
            self.console.print(f"[bold]Files in '{folder_path}':[/bold]")
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    self.console.print(f" - {filename}")
        else:
            self.console.print(f"[red]The folder '{folder_path}' does not exist.[/red]")

    def do_load(self, line):
        """Load the case file with the specified case number."""
        case_number = input("Enter case number (format XXX-XXX): ").strip()
        if not case_number:
            self.console.print("[red]Case number is required.[/red]")
            return

        case_file_name = f"case {case_number}.txt"
        case_file_path = os.path.join("archive cases", case_file_name)
        
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

        tools = {
            "1": ("Email", "Email_Analysis.py"),
            "2": ("PDF", "PDF_Analysis.py"),
            "3": ("ISO", "ISO_Analysis.py"),
            "4": ("OVA", "OVA_Analysis.py"),
            "5": ("URL", "URL_Analysis.py"),
            "6": ("JSON", "JSON_Analysis.py"),
            "7": ("DB", "main_DB.py"),
            "8": ("PNG", "PNG_Analysis.py"),
            "9": ("CODE", "CODE_Analysis.py"),
            "10": ("EXE / DMG", "EXE_DMG_Analysis.py"),
            "11": ("EVENT VIEWER", "EVENT_VIEWER_Analysis.py")
        }

        self.console.print("[bold]Choose which tool you need:[/bold]")
        for key, (name, _) in tools.items():
            self.console.print(f"{key}: {name}")

        choice = input("Choose the tool you need or type 'exit' to quit: ").strip()

        if choice == 'exit':
            self.console.print("Bye!")
            self.log_to_case_file("User exited tool selection.")
            return

        if choice in tools:
            tool_name, module_file = tools[choice]
            self.console.print(f"[bold]{tool_name} Analysis was selected[/bold]")
            module_path = os.path.join("Tools", module_file)
            
            if choice == "7":
                module_path = os.path.join(os.path.dirname(__file__), "../..", "FULL FORNSIC TOOL/DB", module_file)
                main_DB = self.import_module_from_path("main_DB", module_path)
                main_DB.DBCLI().cmdloop()
            else:
                tool_module = self.import_module_from_path(tool_name.replace(" ", "_"), module_path)
                tool_module.main()

            self.log_to_case_file(f"{tool_name} tool selected and executed.")
        else:
            self.console.print("[red]Invalid choice. Please try again.[/red]")
            self.log_to_case_file("Invalid tool selection attempted.")

    def log_to_case_file(self, message):
        """Log a message to the current case file."""
        if self.log_file:
            logging.info(message)

    def import_module_from_path(self, module_name, module_path):
        """Dynamically import a module from the given file path."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def do_list_cases(self, arg):
        """List all case files in the 'archive cases' folder."""
        self.list_files_in_archive_cases()

    def do_note(self, arg):
        """Add a note to the current case file."""
        if not self.case_created:
            self.console.print("[red]You must create a case before adding a note.[/red]")
            return

        investigator_name = input("Enter the investigator's name: ").strip()
        if not investigator_name:
            self.console.print("[red]Investigator's name is required.[/red]")
            return

        note_content = input("Enter your note: ").strip()

        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open(self.log_file, 'a') as file:
                file.write(f"Date: {date_added}\n")
                file.write(f"Investigator: {investigator_name}\n")
                file.write(f"Note: {note_content}\n")
                file.write("-" * 40 + "\n")

            self.console.print("[green]Note added successfully.[/green]")

            # Log the note addition event
            if self.log_file:
                logging.info("Added note to case file.")

        except Exception as e:
            self.console.print(f"[red]An error occurred while adding the note: {e}[/red]")
            if self.log_file:
                logging.error(f"Error adding note to file: {e}")

    def do_exit(self, arg):
        """Exit the CaseFileCLI."""
        self.console.print("Exiting...")
        return True

    def do_help(self, arg):
        """Display help information"""
        if arg:
            cmd.Cmd.do_help(self, arg)
        else:
            # Create a table to display the help information
            help_table = Table(title="Available Commands", box=None)
            help_table.add_column("Command", style="bold magenta")
            help_table.add_column("Description", style="bold white")
            help_table.add_row("load", "Load an existing case file")
            help_table.add_row("list_cases", "List all archived cases")
            help_table.add_row("note", "Add a note to the current case file")
            help_table.add_row("tool", "Select a tool to analyze the case")
            help_table.add_row("exit", "Exit the CASE system")
            help_table.add_row("help", "Show this help message")

            self.console.print(help_table)

if __name__ == '__main__':
    case_file_cli = CaseFileCLI(file_path="")
    case_file_cli.cmdloop()
