import subprocess
import sys
import os
import cmd
import DB.main_DB as main_DB  # Import the DBCLI class from the main_DB module

# Define the directory containing the script files relative to the current script's location
script_dir = os.path.join(os.path.dirname(__file__))

def run_config():
    """Run the config script."""
    print("Running config script...")
    config_path = os.path.join(script_dir, 'config.py')
    subprocess.run([sys.executable, config_path])

def run_user():
    """Run the user script."""
    print("Running user script...")
    user_path = os.path.join(script_dir, 'user.py')
    subprocess.run([sys.executable, user_path])

def run_server():
    """Run the server script."""
    print("Running server script...")
    server_path = os.path.join(script_dir, 'server.py')
    subprocess.run([sys.executable, server_path])

def run_vs():
    """Run the VS script."""
    print("Running VS script...")
    vs_path = os.path.join(script_dir, 'VS.py')
    subprocess.run([sys.executable, vs_path])

class DBCLI(cmd.Cmd):
    prompt = '(DB-cli) '

    def do_config(self, arg):
        """Run the config script."""
        run_config()

    def do_user(self, arg):
        """Run the user script."""
        run_user()

    def do_server(self, arg):
        """Run the server script."""
        run_server()

    def do_vs(self, arg):
        """Run the VS script."""
        run_vs()

    def do_exit(self, arg):
        """Exit the CLI."""
        print("Exiting...")
        return True

    def do_help(self, arg):
        """Show help information."""
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

# Ensure that the script runs the DBCLI command loop when executed directly
if __name__ == '__main__':
    main_DB.DBCLI().cmdloop()
