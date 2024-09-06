import subprocess
import sys
import os
import cmd
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Define the directory containing the script files relative to the current script's location
script_dir = os.path.join(os.path.dirname(__file__))

def run_config():
    """Run the config script."""
    logger.info("Running config script...")
    config_path = os.path.join(script_dir, 'config.py')
    subprocess.run([sys.executable, config_path])
    logger.info("Config script execution completed.")

def run_user():
    """Run the user script."""
    logger.info("Running user script...")
    user_path = os.path.join(script_dir, 'user.py')
    subprocess.run([sys.executable, user_path])
    logger.info("User script execution completed.")

def run_server():
    """Run the server script."""
    logger.info("Running server script...")
    server_path = os.path.join(script_dir, 'server.py')
    subprocess.run([sys.executable, server_path])
    logger.info("Server script execution completed.")

def run_vs():
    """Run the VS script."""
    logger.info("Running VS script...")
    vs_path = os.path.join(script_dir, 'VS.py')
    subprocess.run([sys.executable, vs_path])
    logger.info("VS script execution completed.")

class DBCLI(cmd.Cmd):
    prompt = '(DB-cli) '

    def do_config(self, arg):
        """Run the config script."""
        logger.info("DBCLI command: config")
        run_config()

    def do_user(self, arg):
        """Run the user script."""
        logger.info("DBCLI command: user")
        run_user()

    def do_server(self, arg):
        """Run the server script."""
        logger.info("DBCLI command: server")
        run_server()

    def do_vs(self, arg):
        """Run the VS script."""
        logger.info("DBCLI command: vs")
        run_vs()

    def do_exit(self, arg):
        """Exit the CLI."""
        logger.info("Exiting DBCLI.")
        print("Exiting...")
        return True

    def do_help(self, arg):
        """Show help information."""
        logger.info("DBCLI command: help")
        if arg:
            cmd.Cmd.do_help(self, arg)
        else:
            print("\nDocumented commands (type help <topic>):")
            print("========================================")
            print("config   Run the config script")
            print("user     Run the user script")
            print("server   Run the server script")
            print("vs       Run the VS script")
            print("exit     Exit the CLI")
            print("help     Show this help message")

    def default(self, line):
        """Handle unknown commands."""
        logger.warning(f"Unknown command: {line}")
        print(f"*** Unknown syntax: {line}")

def main():
    """Main function to start the DBCLI command loop."""
    logger.info("Starting DBCLI command loop.")
    try:
        db_cli = DBCLI()
        db_cli.cmdloop()
    except Exception as e:
        logger.error(f"An error occurred in the DBCLI: {e}")
    finally:
        logger.info("DBCLI command loop terminated.")

if __name__ == '__main__':
    main()
