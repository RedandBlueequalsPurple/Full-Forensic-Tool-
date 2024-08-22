import cmd
import subprocess
import sys
import os
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def main():
    logger.info("CASE Section execution started.")
    try:
        # Tool logic here
        logger.debug("Executing CASE Section logic.")
        # Example action
        logger.info("CASE Section action completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("CASE Section execution finished.")




# Define the directory containing the script files relative to the current script's location
# Update this to point to the correct directory where CASES is located
script_dir = os.path.join(os.path.dirname(__file__), '../CASES')  # Adjust path as necessary
print(f"Script directory: {script_dir}")  # Debugging line

def run_New_Case():
    """Run the New_Case script."""
    print("Please wait while we are making all you need to make a new case!...")  # Fixed typo
    New_Case_path = os.path.join(script_dir, 'New_Case.py')
    print(f"New_Case path: '{New_Case_path}'")  # Debugging line
    if os.path.exists(New_Case_path):
        subprocess.run([sys.executable, New_Case_path])
    else:
        print(f"Error: File '{New_Case_path}' does not exist.")  # Error handling

def run_Load_Case():
    """Run the Load_Case script."""
    print("Please wait while we are loading the case you asked ...")  # Fixed typo
    Load_Case_path = os.path.join(script_dir, 'Load_Case.py')
    print(f"Load_Case path: '{Load_Case_path}'")  # Debugging line
    if os.path.exists(Load_Case_path):
        subprocess.run([sys.executable, Load_Case_path])
    else:
        print(f"Error: File '{Load_Case_path}' does not exist.")  # Error handling

def main():
    class CaseSanction(cmd.Cmd):
        intro = "Welcome to the CASE sanction system. Type 'help' or '?' to list commands.\n"
        prompt = "(CASE) "

        def __init__(self):
            super().__init__()
            print("Hello, you are in the CASE sanction.\n\n"
                  "You can choose to open a new investigation or continue an old one.\n\n"
                  "Please note that all your actions will be logged in this program and will be added to the report.\n\n"
                  "Evidence in the form of log events will be recorded for everything you do during the investigation.\n\n")

        def do_new(self, arg):
            """Create a new case"""
            print("Creating a new case...")
            run_New_Case()  # Invoke the New_Case script

        def do_load(self, arg):
            """Load an existing case"""
            print("Loading the requested case...")
            run_Load_Case()  # Invoke the Load_Case script

        def do_exit(self, arg):
            """Exit the CASE sanction system"""
            print("Exiting the CASE sanction system.")
            return True  # Returning True exits the command loop

        def do_help(self, arg):
            """Display help information"""
            if arg:
                cmd.Cmd.do_help(self, arg)
            else:
                print("Available commands:\n"
                      "  new    - Create a new case\n"
                      "  load   - Load an existing case\n"
                      "  exit   - Exit the CASE sanction system\n"
                      "  help   - Show this help message\n")

    CaseSanction().cmdloop()

if __name__ == "__main__":
    main()
