import cmd
import subprocess
import sys
import os
import logging
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
import colorama
colorama.init(autoreset=True)

# Initialize the rich console
console = Console()

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def run_New_Case():
    """Run the New_Case script."""
    logger.info("Attempting to run the New_Case script.")
    console.print(Panel("Please wait while we are preparing everything you need to create a new case!", title="New Case", style="bold blue"))
    New_Case_path = os.path.join(script_dir, 'New_Case.py')
    logger.debug(f"New_Case path: '{New_Case_path}'")
    console.print(f"[bold yellow]New_Case path:[/bold yellow] '{New_Case_path}'", highlight=True)
    if os.path.exists(New_Case_path):
        try:
            subprocess.run([sys.executable, New_Case_path], check=True)
            logger.info("New_Case script executed successfully.")
            console.print("[green]New_Case script executed successfully.[/green]")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred while running New_Case script: {e}")
            console.print(f"[red]Error occurred while running New_Case script: {e}[/red]")
    else:
        error_message = f"Error: File '{New_Case_path}' does not exist."
        console.print(f"[red]{error_message}[/red]")  # Error handling
        logger.error(error_message)

def run_Load_Case():
    """Run the Load_Case script."""
    logger.info("Attempting to run the Load_Case script.")
    console.print(Panel("Please wait while we are loading the requested case...", title="Load Case", style="bold blue"))
    Load_Case_path = os.path.join(script_dir, 'Load_Case.py')
    logger.debug(f"Load_Case path: '{Load_Case_path}'")
    console.print(f"[bold yellow]Load_Case path:[/bold yellow] '{Load_Case_path}'", highlight=True)
    if os.path.exists(Load_Case_path):
        try:
            subprocess.run([sys.executable, Load_Case_path], check=True)
            logger.info("Load_Case script executed successfully.")
            console.print("[green]Load_Case script executed successfully.[/green]")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred while running Load_Case script: {e}")
            console.print(f"[red]Error occurred while running Load_Case script: {e}[/red]")
    else:
        error_message = f"Error: File '{Load_Case_path}' does not exist."
        console.print(f"[red]{error_message}[/red]")  # Error handling
        logger.error(error_message)

def main():
    class CaseSanction(cmd.Cmd):
        intro = "Welcome to the CASE sanction system. Type 'help' or '?' to list commands.\n"
        prompt = "(CASE) "

        def __init__(self):
            super().__init__()
            # Customize each line with the specified color
            welcome_message = Text()
            welcome_message.append("Hello, you are in the CASE sanction.\n\n", style="red")
            welcome_message.append("You can choose to open a new investigation or continue an old one.\n\n", style="blue")
            welcome_message.append("Please note that all your actions will be logged in this program and will be added to the report.\n\n", style="purple")
            welcome_message.append("Evidence in the form of log events will be recorded for everything you do during the investigation.\n\n", style="rgb(255,105,180)")  # Updated to custom pink
            
            console.print(Panel(welcome_message, title="Welcome", border_style="bold green"))
            logger.info("CASE sanction system initialized.")

        def do_new(self, arg):
            """Create a new case"""
            logger.info("User selected 'new' command to create a new case.")
            console.print("[cyan]Creating a new case...[/cyan]")
            run_New_Case()  # Invoke the New_Case script

        def do_load(self, arg):
            """Load an existing case"""
            logger.info("User selected 'load' command to load an existing case.")
            console.print("[cyan]Loading the requested case...[/cyan]")
            run_Load_Case()  # Invoke the Load_Case script

        def do_exit(self, arg):
            """Exit the CASE sanction system"""
            logger.info("User exited the CASE sanction system.")
            console.print("[yellow]Exiting the CASE sanction system.[/yellow]")
            return True  # Returning True exits the command loop

        def do_help(self, arg):
            """Display help information"""
            logger.info(f"Help command invoked with argument: '{arg}'")
            if arg:
                cmd.Cmd.do_help(self, arg)
            else:
                help_table = Table(title="Available Commands", box=None)
                help_table.add_column("Command", style="bold magenta")
                help_table.add_column("Description", style="bold white")
                help_table.add_row("new", "Create a new case")
                help_table.add_row("load", "Load an existing case")
                help_table.add_row("exit", "Exit the CASE sanction system")
                help_table.add_row("help", "Show this help message")
                console.print(help_table)

    # Define the directory containing the script files relative to the current script's location
    global script_dir
    script_dir = os.path.join(os.path.dirname(__file__), 'Case_Section/CASES')  # Adjust path as necessary
    logger.debug(f"Script directory: {script_dir}")

    CaseSanction().cmdloop()

if __name__ == "__main__":
    main()
