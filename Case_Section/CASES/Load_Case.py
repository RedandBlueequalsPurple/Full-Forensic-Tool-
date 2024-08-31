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

        self.console.print(Panel("Choose which tool you need:", title="Tool Selection"))

        ListOfTools = [
            [1, 'Email'], [2, 'PDF'], [3, 'ISO'], [4, 'OVA'], [5, 'URL'],
            [6, 'JSON'], [7, 'DB'], [8, 'PNG'], [9, 'CODE'], [10, 'EXE / DMG'], [11, 'EVENT VIEWER']
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
            self.console.print(f"[red]Error: The script '{tool_script}' was not found in the '{tool_dir}' directory.[/red]")
            self.log_to_case_file(f"Error: {tool_name} script not found.")
        except AttributeError:
            self.console.print(f"[red]Error: The '{tool_name}' script does not have a 'main' function.[/red]")
            self.log_to_case_file(f"Error: {tool_name} script lacks 'main' function.")
        except Exception as e:
            self.console.print(f"[red]An unexpected error occurred while running the '{tool_name}' tool: {e}[/red]")
            self.log_to_case_file(f"Unexpected error in {tool_name}: {e}")

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

            if self.log_file:
                logging.info(f"Note added by {investigator_name}: {note_content}")

        except Exception as e:
            self.console.print(f"[red]An error occurred while adding the note: {e}[/red]")
            if self.log_file:
                logging.error(f"Error adding note: {e}")

    def do_help(self, arg):
        """Display this help message."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Command", style="bold green")
        table.add_column("Description", style="bold yellow")

        commands = [
            ("load", "Load an existing case file"),
            ("list_cases", "List all case files in 'archive cases'"),
            ("note", "Add a note to the current case file"),
            ("tool", "Select a tool to use"),
            ("help", "Display this help message"),
            ("exit", "Exit the CaseFileCLI")
        ]

        for command, description in commands:
            table.add_row(command, description)

        self.console.print(table)

    def do_exit(self, arg):
        """Exit the CLI."""
        if self.current_case_number:
            self.log_to_case_file("User exited the CLI.")
        self.console.print("Goodbye!", style="bold red")
        return True

if __name__ == '__main__':
    cli = CaseFileCLI("casefile.txt")
    cli.cmdloop()
