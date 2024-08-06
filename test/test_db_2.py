import data_store

def command_loop():
    print("Entering query mode. Type 'exit' to quit, 'show all' to display all entries, 'show md5' to display all MD5 hashes with source files, 'show sha1' to display all SHA1 hashes with source files, 'show sha256' to display all SHA256 hashes with source files, 'show tag' to display all TAG values with source files, 'show value' to display all VALUE values with source files, 'show enabled' to display all ENABLED values with source files.")
    print("You can also type 'show [key]' to display specific hardware specifications.")
    while True:
        query = input("Enter command: ").strip()
        if query.lower() == 'exit':
            break
        elif query.lower() == 'show all':
            data_store.display_all_entries_with_all_keys()
        elif query.lower() == 'show md5':
            data_store.display_all_md5()
        elif query.lower() == 'show sha1':
            data_store.display_all_sha1()
        elif query.lower() == 'show sha256':
            data_store.display_all_sha256()
        elif query.lower() == 'show tag':
            data_store.display_all_tag()
        elif query.lower() == 'show value':
            data_store.display_all_value()
        elif query.lower() == 'show enabled':
            data_store.display_all_enabled()
        elif query.lower().startswith('show '):
            key = query[5:].strip()  # Extract key after 'show '
            display_function_name = f"display_{key.lower()}"
            if hasattr(data_store, display_function_name):
                getattr(data_store, display_function_name)()
            else:
                print(f"No such key: {key}")
        else:
            results = data_store.query_data_store(query)
            if results:
                field_names = ["MD5", "SHA1", "SHA256", "Source File"] + list(data_store.get_all_keys())
                rows = [[result.get('MD5', ''), result.get('SHA1', ''), result.get('SHA256', ''), result.get('source_file', '')] + [result.get(key, '') for key in data_store.get_all_keys()] for result in results]
                table_str = data_store.create_pretty_table_with_separators(field_names, rows)
                print(table_str)
            else:
                print("No matching results found.")

if __name__ == "__main__":
    data_store.process_new_files()  # Process new files at startup
    command_loop()
