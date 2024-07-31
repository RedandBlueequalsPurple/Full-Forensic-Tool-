import json

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

print("Please give the path to the JSON file")
file_path = input().strip()

try:
    # Read JSON data from file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Get all keys and values
    all_keys = extract_keys(data)
    keys_values_map = extract_values(data)
    keys_values_count = count_values_per_key(keys_values_map)

    # Print each key on a separate line
    print("Keys:")
    for key in all_keys:
        print(f"{key}")

    # Print each value on a separate line
    print("\nValues:")
    for value in {val for values in keys_values_map.values() for val in values}:
        print(value)

    # Print the keys and values together
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
                    for value in keys_values_map[chosen_key]:
                        print(value)
                    break
                else:
                    print(f"Key '{chosen_key}' not found. Please enter a valid key.")
                    
        elif query in keys_values_map:
            print(f"\nValues for key '{query}':")
            for value in keys_values_map[query]:
                print(value)
        else:
            print(f"No values found for key '{query}' or invalid key.")
            
except FileNotFoundError:
    print(f"The file '{file_path}' does not exist.")
except json.JSONDecodeError:
    print(f"Failed to decode JSON from the file '{file_path}'.")
