import json
import vt
import asyncio
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('event_history.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def extract_keys(obj, keys=set()):
    """Recursively extract all unique keys from a JSON object."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            keys.add(key)
            extract_keys(value, keys)
    elif isinstance(obj, list):
        for item in obj:
            extract_keys(item, keys)
    return keys

def extract_values(obj, values=set(), key_map=None):
    """Recursively extract all unique values from a JSON object and map keys to their values."""
    if key_map is None:
        key_map = {}
        
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key not in key_map:
                key_map[key] = set()
            if isinstance(value, (dict, list)):
                extract_values(value, values, key_map)
            else:
                values.add(value)
                key_map[key].add(value)
    elif isinstance(obj, list):
        for item in obj:
            extract_values(item, values, key_map)
    return key_map

def count_values_per_key(key_map):
    """Get count of values for each key."""
    return {key: len(values) for key, values in key_map.items()}

def get_config():
    """API Key and Server Configuration"""
    return {
        'api_key': '9bcb54f31badf1de44a5ea1b0f501f02a42ac46389133cf554b80409219dbdd8'
    }

async def submit_to_virustotal(value, vt_client):
    """Submit a value (hash or URL) to VirusTotal using vt-py."""
    try:
        if len(value) == 64 and all(c in '0123456789abcdefABCDEF' for c in value):
            # File hash
            response = await vt_client.get_object_async(f'files/{value}')
        else:
            # URL (URL encoding may be necessary)
            response = await vt_client.get_object_async(f'urls/{value}')
        
        result = response.as_dict()
        
        logger.debug(f"Submitted {value} to VirusTotal. Response: {json.dumps(result, indent=2)}")
        return result

    except vt.error.APIError as e:
        logger.error(f"API Error: {e}")
        return {'error': f"API Error: {e}"}
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        return {'error': f"Unexpected Error: {e}"}

async def analyze_values(values, vt_client):
    """Analyze values using VirusTotal."""
    for value in values:
        logger.info(f"Analyzing value: {value}")
        result = await submit_to_virustotal(value, vt_client)
        if 'error' in result:
            logger.warning(f"Error for {value}: {result['error']}")
        else:
            logger.info(f"Analysis result for {value}: {json.dumps(result, indent=2)}")

async def main():
    logger.info("JSON Analysis tool execution started.")
    try:
        # Fetch API Key and create VirusTotal client
        config = get_config()
        API_KEY = config['api_key']
        vt_client = vt.Client(API_KEY)
        logger.debug(f"VirusTotal client initialized with API key: {API_KEY}")

        # Get JSON file path
        print("Please give the path to the JSON file")
        file_path = input().strip()
        logger.debug(f"User provided JSON file path: {file_path}")

        # Read JSON data from file
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            logger.info(f"Successfully read JSON file: {file_path}")
        except FileNotFoundError:
            logger.error(f"The file '{file_path}' does not exist.")
            print(f"The file '{file_path}' does not exist.")
            return
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from the file '{file_path}'.")
            print(f"Failed to decode JSON from the file '{file_path}'.")
            return

        # Get all keys and values
        all_keys = extract_keys(data)
        keys_values_map = extract_values(data)
        keys_values_count = count_values_per_key(keys_values_map)

        # Log and print keys
        logger.debug(f"Extracted Keys: {all_keys}")
        print("Keys:")
        for key in all_keys:
            print(f"{key}")

        # Log and print values
        all_values = {val for values in keys_values_map.values() for val in values}
        logger.debug(f"Extracted Values: {all_values}")
        print("\nValues:")
        for value in all_values:
            print(value)

        # Log and print keys and values together
        logger.debug(f"Keys and Values Map: {keys_values_map}")
        print("\nKeys and Values:")
        for key, values in keys_values_map.items():
            for value in values:
                print(f"{key} : {value}")

        # Continuous querying
        print("\nEnter 'exit' to quit.")
        print("Enter 'keys' to list all keys.")
        print("Enter 'sum key' to list all keys with the count of values.")
        
        while True:
            query = input("Enter your choice: ").strip()
            logger.debug(f"User input: {query}")

            if query.lower() == 'exit':
                break

            if query.lower() == 'keys':
                print("\nKeys:")
                for key in all_keys:
                    print(key)
            elif query.lower() == 'sum key':
                # Print keys with serial numbers
                print("\nKeys with Serial Numbers:")
                key_list = list(keys_values_count.keys())
                for idx, key in enumerate(key_list, start=1):
                    print(f"{idx}. {key}: {keys_values_count[key]} values")
                
                # Allow user to choose a key by its serial number or name
                while True:
                    choice = input("\nEnter the number or name of the key to see its values (or 0 to cancel): ").strip()
                    logger.debug(f"User key choice: {choice}")
                    if choice == '0':
                        break
                    if choice.isdigit():
                        try:
                            choice_num = int(choice)
                            if 1 <= choice_num <= len(key_list):
                                chosen_key = key_list[choice_num - 1]
                            else:
                                print("Invalid choice number. Please enter a number from the list.")
                                continue
                        except ValueError:
                            print("Invalid input. Please enter a valid number.")
                            continue
                    else:
                        chosen_key = choice

                    if chosen_key in keys_values_map:
                        print(f"\nValues for key '{chosen_key}':")
                        values_list = list(keys_values_map[chosen_key])
                        for value in values_list:
                            print(value)
                        
                        # Log and analyze values for the chosen key
                        logger.info(f"Running VirusTotal analysis on values for key '{chosen_key}': {values_list}")
                        await analyze_values(values_list, vt_client)
                        break
                    else:
                        print(f"Key '{chosen_key}' not found. Please enter a valid key.")
                        logger.warning(f"User attempted to query non-existing key: {chosen_key}")
                        
            elif query in keys_values_map:
                print(f"\nValues for key '{query}':")
                for value in keys_values_map[query]:
                    print(value)
            else:
                print(f"No values found for key '{query}' or invalid key.")
                logger.warning(f"No values found for key '{query}' or invalid key.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("JSON Analysis tool execution finished.")

# Run the main function
asyncio.run(main())
