from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
import colorama
import logging
from datetime import datetime
import random

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

# Create colored text for the "Coder :" line
coder_text = Text()
coder_text.append("Coder : ", style="bold")
coder_text.append("Red", style="red")
coder_text.append(" and ", style="bold")
coder_text.append("Blue", style="blue")
coder_text.append(" equals ", style="bold")
coder_text.append("Purple", style="magenta")

# Create the header message
header_content = Text()
header_content.append("Free Section\n", style="bold magenta")
header_content.append("\n")  # Add an empty line for spacing
header_content.append(f"{current_date}\n", style="bold yellow")
header_content.append("\n")  # Add an empty line for spacing
header_content.append(coder_text)

# Create the panel with appropriate padding and border
header_panel = Panel(
    header_content,
    border_style="bold cyan",
    padding=(1, 2),
    expand=True
)

# Display the header panel with colored text inside
console.print(header_panel)
logging.info(f"Displayed header: {header_content}")

# Display warning note
note_message = "[bold red]Note: I am not responsible for illegal use of the software[/bold red]"
console.print(note_message)
logging.warning(note_message)

# Define the colors to use
colors = ["bold red", "bold green", "bold blue", "bold yellow", "bold magenta", "bold cyan", "bold white"]

# Tools list with random colors
tools_table = Table(show_header=False, show_edge=False, show_lines=False, title="[bold magenta]Tool Options[bold magenta]")

# Define tools list excluding option 0
ListOfTools = [
    [1, 'Email Analysis'], [2, 'PDF Analysis'], [3, 'ISO Analysis'], 
    [4, 'OVA Analysis'], [5, 'URL Analysis'], [6, 'JSON Analysis'], [7, 'DB'], 
    [8, 'IMAGE Analysis'], [9, 'CODE Analysis'], [10, 'EXE / DMG Analysis'], 
    [11, 'EVENT VIEWER']
]

# Add tools to the table with random colors
for tool in ListOfTools:
    random_color = random.choice(colors)  # Pick a random color
    tools_table.add_row(f"{tool[0]}", f"[{random_color}]{tool[1]}[/{random_color}]")
logging.info("Tools list populated in the table with random colors.")

# Display the tools table
console.print(Panel(tools_table, title="Select a Tool", border_style="bold cyan"))
logging.info("Displayed tools table.")

# Tool mapping with correct import paths
tool_mapping = {
    "1": ("Email Analysis", "Tools.Email_Analysis"),
    "2": ("PDF Analysis", "Tools.PDF_Analysis"),
    "3": ("ISO Analysis", "Tools.ISO_Analysis"),
    "4": ("OVA Analysis", "Tools.OVA_Analysis"),
    "5": ("URL Analysis", "Tools.URL_Analysis"),
    "6": ("JSON Analysis", "Tools.JSON_Analysis"),
    "7": ("DB", "Free_Section.DB.main_DB"),
    "8": ("IMAGE Analysis", "Tools.IMAGE_Analysis"),
    "9": ("CODE Analysis", "Tools.CODE_Analysis"),
    "10": ("EXE / DMG Analysis", "Tools.EXE_DMG_Analysis"),
    "11": ("EVENT VIEWER", "Tools.Event_Viewer")
}

# Function to dynamically import modules
def dynamic_import(import_path):
    try:
        components = import_path.split('.')
        module = __import__(components[0], fromlist=components[1:])
        for comp in components[1:]:
            module = getattr(module, comp)
        return module
    except ImportError as e:
        error_message = f"Failed to import module '{import_path}' with error: {e}"
        logging.error(error_message)
        raise ImportError(error_message)

while True:
    choice = console.input("Select a tool (number) or type 'exit' to quit: ")
    logging.info(f"User input: {choice}")

    if choice == 'exit':
        console.print("[bold red]Exiting...[/bold red]")
        logging.info("User exited the tool selection.")
        break

    if choice in tool_mapping:
        module_name, import_path = tool_mapping[choice]
        console.print(f"[bold green]{module_name} was selected[/bold green]")
        log_tool_selection(choice, module_name)

        try:
            logging.info(f"Attempting to import and run module: {import_path}")
            if choice == "7":
                import Free_Section.DB.main_DB as main_DB
                logging.info("Starting DB CLI.")
                main_DB.DBCLI().cmdloop()  # This will start the CLI for the DB tool
            else:
                module = dynamic_import(import_path)
                logging.info(f"Running main function of {module_name}.")
                module.main()
        except Exception as e:
            error_message = f"Failed to import or run module '{import_path}' with error: {e}"
            console.print(f"[bold red]{error_message}[/bold red]")
            logging.error(error_message)
    else:
        invalid_choice_message = "[bold red]Invalid choice. Please select a valid tool.[/bold red]"
        console.print(invalid_choice_message)
        logging.warning(f"Invalid choice entered: {choice}")
