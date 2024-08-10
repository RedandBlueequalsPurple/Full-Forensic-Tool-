import cmd

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

        def do_start(self, arg):
            """Start the CASE sanction process"""
            print("Starting the CASE sanction process...")
            # Add code to start an investigation here

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
                      "  start  - Start the CASE sanction process\n"
                      "  exit   - Exit the CASE sanction system\n"
                      "  help   - Show this help message\n")

    CaseSanction().cmdloop()

if __name__ == "__main__":
    main()
