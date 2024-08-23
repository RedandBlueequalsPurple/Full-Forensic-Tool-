import logging
import sys

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Redirect stdout and stderr to the logger
class StreamToLogger(object):
    def __init__(self, logger, log_level):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

# Redirect stdout and stderr to the logger
sys.stdout = StreamToLogger(logger, logging.INFO)
sys.stderr = StreamToLogger(logger, logging.ERROR)

def handle_tool_selection(selection):
    """Handle tool selection."""
    if selection == '8':
        message = "STAY TUNED, WILL BE ADDED IN THE FUTURE"
        logger.info(message)
        print(message)  # This will appear on the screen
    else:
        logger.info(f"Tool {selection} selected.")
        # Handle other tool selections here
        # Example: Handle selection '1', '2', etc.

def main():
    while True:
        selection = input("Select a tool (number) or type 'exit' to quit: ").strip()
        if selection.lower() == 'exit':
            logger.info("Exiting the program.")
            break
        handle_tool_selection(selection)

if __name__ == "__main__":
    main()
