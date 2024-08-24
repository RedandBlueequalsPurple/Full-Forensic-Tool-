import pytsk3
import datetime
import json
import os
import logging
from tqdm import tqdm

# Setup logging
log_file = 'event_history.log'
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def file_info_to_dict(fs, entry, path="/"):
    file_data = {}
    file_data['path'] = f"{path}{entry.info.name.name.decode('utf-8')}"
    file_data['type'] = entry.info.meta.type
    file_data['size'] = entry.info.meta.size
    file_data['inode'] = entry.info.meta.addr
    file_data['uid'] = entry.info.meta.uid
    file_data['gid'] = entry.info.meta.gid
    file_data['mode'] = entry.info.meta.mode
    file_data['timestamps'] = {
        'created': datetime.datetime.fromtimestamp(entry.info.meta.crtime).isoformat() if entry.info.meta.crtime else 'N/A',
        'modified': datetime.datetime.fromtimestamp(entry.info.meta.mtime).isoformat() if entry.info.meta.mtime else 'N/A',
        'accessed': datetime.datetime.fromtimestamp(entry.info.meta.atime).isoformat() if entry.info.meta.atime else 'N/A',
        'changed': datetime.datetime.fromtimestamp(entry.info.meta.ctime).isoformat() if entry.info.meta.ctime else 'N/A'
    }

    if entry.info.meta.size > 0:
        file_object = fs.open_meta(inode=entry.info.meta.addr)
        data = file_object.read_random(0, entry.info.meta.size)
        file_data['file_data'] = data[:100].decode('utf-8', errors='replace')

    return file_data

def directory_to_dict(fs, directory, path="/", visited_inodes=None, progress_bar=None):
    if visited_inodes is None:
        visited_inodes = set()
    
    dir_data = []
    for entry in directory:
        if entry.info.meta is None:
            continue
        
        inode = entry.info.meta.addr
        if inode in visited_inodes:
            continue
        visited_inodes.add(inode)

        file_data = file_info_to_dict(fs, entry, path)
        dir_data.append(file_data)
        
        if progress_bar:
            progress_bar.update(1)
        
        if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
            try:
                sub_directory_path = f"{path}{entry.info.name.name.decode('utf-8')}/"
                sub_directory = fs.open_dir(path=sub_directory_path)
                file_data['contents'] = directory_to_dict(fs, sub_directory, path=sub_directory_path, visited_inodes=visited_inodes, progress_bar=progress_bar)
            except (OSError, IOError) as e:
                logging.error(f"Unable to open directory {sub_directory_path} - {e}")
                print(f"Warning: Unable to open directory {sub_directory_path} - {e}")
    
    return dir_data

def count_files_and_directories(fs, directory, path="/", visited_inodes=None):
    if visited_inodes is None:
        visited_inodes = set()
    
    count = 0
    for entry in directory:
        if entry.info.meta is None:
            continue
        
        inode = entry.info.meta.addr
        if inode in visited_inodes:
            continue
        visited_inodes.add(inode)

        count += 1
        if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
            try:
                sub_directory_path = f"{path}{entry.info.name.name.decode('utf-8')}/"
                sub_directory = fs.open_dir(path=sub_directory_path)
                count += count_files_and_directories(fs, sub_directory, path=sub_directory_path, visited_inodes=visited_inodes)
            except (OSError, IOError) as e:
                logging.error(f"Unable to open directory {sub_directory_path} - {e}")
                print(f"Warning: Unable to open directory {sub_directory_path} - {e}")
    
    return count

def analyze_iso(iso_path):
    img = pytsk3.Img_Info(iso_path)
    fs = pytsk3.FS_Info(img)

    root_directory = fs.open_dir(path="/")
    
    total_items = count_files_and_directories(fs, root_directory)
    
    with tqdm(total=total_items, desc="Analyzing ISO", unit="item") as progress_bar:
        analysis_data = directory_to_dict(fs, root_directory, progress_bar=progress_bar)
    
    return analysis_data

def main():
    logging.info("Starting ISO analysis")

    iso_path = input("Please enter the path to the ISO file: ")
    logging.info(f"ISO path provided: {iso_path}")

    try:
        data = analyze_iso(iso_path)
    except Exception as e:
        logging.error(f"Error analyzing ISO: {e}")
        print(f"Error: {e}")
        return
    
    json_dir = "JSON"
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
        logging.info(f"Created JSON directory at {json_dir}")
    
    # Extract the ISO file name without the extension
    iso_file_name = os.path.splitext(os.path.basename(iso_path))[0]
    
    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create the JSON file name using the ISO file name and timestamp
    json_file_name = f"{iso_file_name}_{timestamp}.json"
    json_file_path = os.path.join(json_dir, json_file_name)
    
    # Ask the user whether to save to JSON or display the data
    choice = input("Would you like to save the data to a JSON file (1) or display it (2)? Enter 1 or 2: ")
    logging.info(f"User choice: {choice}")
    
    if choice == "1":
        try:
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            logging.info(f"Analysis data saved to {json_file_path}")
            print(f"Analysis data saved to {json_file_path}")
        except Exception as e:
            logging.error(f"Error saving JSON file: {e}")
            print(f"Error saving JSON file: {e}")
    elif choice == "2":
        print(json.dumps(data, indent=4))
    else:
        logging.warning("Invalid choice provided by the user")
        print("Invalid choice. Exiting without saving or displaying data.")

    logging.info("ISO analysis completed")

# This allows the script to be run as a standalone program or imported as a module
if __name__ == "__main__":
    main()
