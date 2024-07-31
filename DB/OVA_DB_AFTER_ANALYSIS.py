import json
import sys
import os

def process_metadata(metadata):
    """Process metadata as needed."""
    print("Processing metadata...")
    # For demonstration, just print metadata
    print(metadata)

def load_metadata(metadata_file):
    """Load metadata from a JSON file."""
    if not os.path.isfile(metadata_file):
        print(f"Error: The file {metadata_file} does not exist.")
        return None
    with open(metadata_file, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

def query_metadata(metadata, query):
    """Query metadata based on a simple keyword search."""
    results = []
    def search(element):
        if query.lower() in str(element).lower():
            results.append(element)
        for child in element.get('children', []):
            search(child)
    search(metadata)
    return results

def print_usage():
    """Print usage instructions for the script."""
    usage_message = """
Usage: python OVA_DB_AFTER_ANALYSIS.py <metadata_file> [<query>]

Arguments:
  <metadata_file>    Path to the JSON file containing metadata.
  [<query>]          Optional query term to search in the metadata.

Description:
  If <query> is provided, the script will search for the term in the metadata
  and print the matching results.
  If <query> is not provided, the script will simply process and print the
  entire metadata.

Examples:
  python OVA_DB_AFTER_ANALYSIS.py metadata.json
  python OVA_DB_AFTER_ANALYSIS.py metadata.json search_term
    """
    print(usage_message)

def cli_mode():
    """CLI mode for querying metadata."""
    if len(sys.argv) < 2:
        print("Error: Missing required arguments.")
        print_usage()
        sys.exit(1)

    metadata_file = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else None

    metadata = load_metadata(metadata_file)

    if metadata is None:
        print("Failed to load metadata.")
        sys.exit(1)

    if query:
        results = query_metadata(metadata, query)
        if results:
            print(f"Results for '{query}':")
            for result in results:
                print(json.dumps(result, indent=4))
        else:
            print(f"No results found for '{query}'.")
    else:
        # Process metadata if no query is provided
        process_metadata(metadata)

def main():
    cli_mode()

if __name__ == "__main__":
    main()
