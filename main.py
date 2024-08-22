from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import colorama
import logging
from datetime import datetime

# Initialize colorama
colorama.init(autoreset=True)

# Configure logging
logging.basicConfig(
    filename='event_history.log', level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_tool_selection(choice, module_name):
    logging.info(f"Tool selected: {choice} ({module_name})")

# Get the current date
current_date = datetime.now().strftime("%Y-%m-%d")

console = Console()

# Display header with date
console.print(Panel.fit(f"[bold magenta]FULL FORENSIC TOOL[/bold magenta]\n[bold yellow]{current_date}[/bold yellow]", title="Coder : Hackeror828"))

# Display warning note
console.print("[bold red]Note: I am not responsible for illegal use of the software[/bold red]")

# Tools list
tools_table = Table(show_header=False, show_edge=False, show_lines=False, title="Tool Options")

# Define tools list as per the options given
ListOfTools = [
    [0, 'CASE Section'], [1, 'Email Analysis'], [2, 'PDF Analysis'], [3, 'ISO Analysis'], 
    [4, 'OVA Analysis'], [5, 'URL Analysis'], [6, 'JSON Analysis'], [7, 'DB'], 
    [8, 'PNG Analysis'], [9, 'CODE Analysis'], [10, 'EXE / DMG Analysis'], 
    [11, 'EVENT VIEWER']
]

# Add tools to the table
for tool in ListOfTools:
    tools_table.add_row(f"{tool[0]}", tool[1])

# Display the tools table
console.print(Panel(tools_table, title="Select a Tool", border_style="bold cyan"))

while True:
    choice = console.input("Select a tool (number) or type 'exit' to quit: ")

    if choice == 'exit':
        console.print("[bold red]Exiting...[/bold red]")
        logging.info("User exited the tool selection.")
        break

    tool_mapping = {
            "0": ("CASE Section", "Tools.CASE"),
            "1": ("Email Analysis", "Tools.Email_Analysis"),
            "2": ("PDF Analysis", "Tools.PDF_Analysis"),
            "3": ("ISO Analysis", "Tools.ISO_Analysis"),
            "4": ("OVA Analysis", "Tools.OVA_Analysis"),
            "5": ("URL Analysis", "Tools.URL_Analysis"),
            "6": ("JSON Analysis", "Tools.JSON_Analysis"),
            "7": ("DB", "DB.main_DB"),
            "8": ("PNG Analysis", "Tools.PNG_Analysis"),
            "9": ("CODE Analysis", "Tools.CODE_Analysis"),
            "10": ("EXE / DMG Analysis", "Tools.EXE_DMG_Analysis"),
            "11": ("EVENT VIEWER", "Tools.Event_Viewer")
    }

    if choice in tool_mapping:
        module_name, import_path = tool_mapping[choice]
        console.print(f"[bold green]{module_name} was selected[/bold green]")
        log_tool_selection(choice, module_name)

        try:
            # Example logic: just log and print the tool selected
            if choice == "7":
                import DB.main_DB as main_DB
                logging.info("Starting DB CLI.")
                main_DB.DBCLI().cmdloop()  # This will start the CLI for the DB tool
            else:
                module = __import__(import_path, fromlist=['main'])
                logging.info(f"Running main function of {module_name}.")
                module.main()
        except Exception as e:
            console.print(f"[bold red]Failed to import or run module '{import_path}' with error: {e}[/bold red]")
            logging.error(f"Failed to import or run module '{import_path}' with error: {e}")
    else:
        console.print("[bold red]Invalid choice. Please select a valid tool.[/bold red]")
        logging.warning(f"Invalid choice entered: {choice}")
