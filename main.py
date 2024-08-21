import os
import sys
import logging

# Configure logging for the main script
logging.basicConfig(filename='event_history.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_tool_selection(choice, module_name):
    logging.info(f"Tool selected: {choice} ({module_name})")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Choose which tool you need:")
ListOfTools = [
    [0, 'CASE Section'], [1, 'Email'], [2, 'PDF'], [3, 'ISO'], [4, 'OVA'], [5, 'URL'],
    [6, 'JSON'], [7, 'DB'], [8, 'PNG'], [9, 'CODE'], [10, 'EXE / DMG'], [11, 'EVENT VIEWER']
]

for tool in ListOfTools:
    print(f"{tool[0]}: {tool[1]}")

while True:
    Choice = input("Choose the tool you need or type 'exit' to quit: ")
    
    if Choice == 'exit':
        print("Bye!")
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

    if Choice in tool_mapping:
        module_name, import_path = tool_mapping[Choice]
        print(f"{module_name} was selected")
        log_tool_selection(Choice, module_name)
        
        try:
            if Choice == "7":
                import DB.main_DB as main_DB
                logging.info("Starting DB CLI.")
                main_DB.DBCLI().cmdloop()  # This will start the CLI for the DB tool
            else:
                module = __import__(import_path, fromlist=['main'])
                logging.info(f"Running main function of {module_name}.")
                module.main()
        except Exception as e:
            logging.error(f"Failed to import or run module '{import_path}' with error: {e}")
    else:
        print("Invalid choice. Please select a valid tool.")
        logging.warning(f"Invalid choice entered: {Choice}")
