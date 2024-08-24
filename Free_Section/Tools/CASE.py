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

def run_New_Case():
    """Run the New_Case script."""
    logger.info("Attempting to run the New_Case script.")
    print("Please wait while we are making all you need to make a new case!...")  # Fixed typo
    New_Case_path = os.path.join(script_dir, 'New_Case.py')
    logger.debug(f"New_Case path: '{New_Case_path}'")
    print(f"New_Case path: '{New_Case_path}'")  # Debugging line
    if os.path.exists(New_Case_path):
        try:
            subprocess.run([sys.executable, New_Case_path], check=True)
            logger.info("New_Case script executed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred while running New_Case script: {e}")
    else:
        error_message = f"Error: File '{New_Case_path}' does not exist."
        print(error_message)  # Error handling
        logger.error(error_message)

def run_Load_Case():
    """Run the Load_Case script."""
    logger.info("Attempting to run the Load_Case script.")
    print("Please wait while we are loading the case you asked ...")  # Fixed typo
    Load_Case_path = os.path.join(script_dir, 'Load_Case.py')
    logger.debug(f"Load_Case path: '{Load_Case_path}'")
    print(f"Load_Case path: '{Load_Case_path}'")  # Debugging line
    if os.path.exists(Load_Case_path):
        try:
            subprocess.run([sys.executable, Load_Case_path], check=True)
            logger.info("Load_Case script executed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred while running Load_Case script: {e}")
    else:
        error_message = f"Error: File '{Load_Case_path}' does not exist."
        print(error_message)  # Error handling
        logger.error(error_message)

def main():
    class CaseSanction(cmd.Cmd):
        intro = "Welcome to the CASE sanction system. Type 'help' or '?' to list commands.\n"
        prompt = "(CASE) "

        def __init__(self):
            super().__init__()
            welcome_message = ("Hello, you are in the CASE sanction.\n\n"
                               "You can choose to open a new investigation or continue an old one.\n\n"
                               "Please note that all your actions will be logged in this program and will be added to the report.\n\n"
                               "Evidence in the form of log events will be recorded for everything you do during the investigation.\n\n")
            print(welcome_message)
            logger.info("CASE sanction system initialized.")

        def do_new(self, arg):
            """Create a new case"""
            logger.info("User selected 'new' command to create a new case.")
            print("Creating a new case...")
            run_New_Case()  # Invoke the New_Case script

        def do_load(self, arg):
            """Load an existing case"""
            logger.info("User selected 'load' command to load an existing case.")
            print("Loading the requested case...")
            run_Load_Case()  # Invoke the Load_Case script

        def do_exit(self, arg):
            """Exit the CASE sanction system"""
            logger.info("User exited the CASE sanction system.")
            print("Exiting the CASE sanction system.")
            return True  # Returning True exits the command loop

        def do_help(self, arg):
            """Display help information"""
            logger.info(f"Help command invoked with argument: '{arg}'")
            if arg:
                cmd.Cmd.do_help(self, arg)
            else:
                help_message = ("Available commands:\n"
                                "  new    - Create a new case\n"
                                "  load   - Load an existing case\n"
                                "  exit   - Exit the CASE sanction system\n"
                                "  help   - Show this help message\n")
                print(help_message)

    # Define the directory containing the script files relative to the current script's location
    # Update this to point to the correct directory where CASES is located
    global script_dir
    script_dir = os.path.join(os.path.dirname(__file__), '../CASES')  # Adjust path as necessary
    logger.debug(f"Script directory: {script_dir}")

    CaseSanction().cmdloop()

if __name__ == "__main__":
    main()
