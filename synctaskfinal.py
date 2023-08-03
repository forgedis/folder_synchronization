from datetime import datetime, timezone
import argparse
import logging
import time
import os
import shutil
import hashlib

'''
Folder synchronization TEST task by Martin Bujnak for Veeam

GitHub repository: https://github.com/forgedis #TODO
'''

def log(message, path, log_path): 
    log = open(log_path, "a")
    base_log_message = f"{datetime.now(timezone.utc).astimezone().isoformat()} | Syncing folders |"
    log.write(f"{base_log_message} {message} {path}\n")
    logging.info(f"{base_log_message} {message} {path}")
    log.close()

def md5(file_path):
    hash = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash.update(chunk)

    return hash.hexdigest()

def sync(source_path, replica_path, log_path):
    '''
    Args:
        source_path: The path to the source folder.
        replica_path: The path to the replica folder.
        log_path: The path to the log file.
    '''
    
    for folder, subfolders, filenames in os.walk(source_path):
        for subfolder in subfolders:
            source_subfolder_path = os.path.join(folder, subfolder)
            replica_subfolder_path = source_subfolder_path.replace(source_path, replica_path)
            
            if not os.path.exists(replica_subfolder_path):
                os.makedirs(replica_subfolder_path)
                log('Created folder:', replica_subfolder_path, log_path)

        for filename in filenames:
            source_file_path = os.path.join(folder, filename)
            replica_file_path = source_file_path.replace(source_path, replica_path)

            if not os.path.exists(replica_file_path):
                    shutil.copy2(source_file_path, replica_file_path)
                    log('Created file:', replica_file_path, log_path)

    for folder, subfolders, filenames in os.walk(replica_path):
        for subfolder in subfolders:
            replica_subfolder_path = os.path.join(folder, subfolder)
            source_subfolder_path = replica_subfolder_path.replace(replica_path, source_path)
            
            if not os.path.exists(source_subfolder_path):
                shutil.rmtree(replica_subfolder_path)
                log('Deleted folder and its content:', replica_subfolder_path, log_path)
        
        for filename in filenames:
            replica_file_path = os.path.join(folder, filename)
            source_file_path = replica_file_path.replace(replica_path, source_path)
            
            if not os.path.exists(source_file_path):
                os.remove(replica_file_path)
                log('Deleted file:', replica_file_path, log_path)

            else:
                if md5(source_file_path) != md5(replica_file_path):
                    shutil.copy2(source_file_path, replica_file_path)
                    log('Updated file:', replica_file_path, log_path)

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    parser = argparse.ArgumentParser()

    parser.add_argument("source_path")
    parser.add_argument("replica_path")
    parser.add_argument("interval", type=int)
    parser.add_argument("log_path")

    args = parser.parse_args()

    while True:
        sync(args.source_path, args.replica_path, args.log_path)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()