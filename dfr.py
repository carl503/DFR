from typing import Final
import libtorrent as lt
import os
import shutil

TORRENT_PATH: Final = "/var/lib/docker/volumes/transmission/_data/transmission-home/torrents"
DOWNLOAD_PATH: Final = "/mnt/pool/downloads/completed"
LABELS: Final = ["radarr", "tv-sonarr", ""]
IGNORE_FOLDERS: Final = ["tv-sonarr", "radarr", "moana"]

def main():
    dangling_files = find_dangling_files()
    print_file_size(dangling_files)
    # Set true to delete files
    delete_files(dangling_files, True)

def find_dangling_files():
    local_files = set([os.path.join(DOWNLOAD_PATH, file_name) for file_name in os.listdir(DOWNLOAD_PATH)])
    local_files -= set([os.path.join(DOWNLOAD_PATH, file_name) for file_name in IGNORE_FOLDERS])
    torrent_folders = get_all_torrent_folders()
    return local_files.difference(torrent_folders)

def delete_files(files, delete=False):
    for file in files:
        if os.path.exists(file) and delete:
            if os.path.isfile(file):
                os.remove(file)
            elif os.path.isdir(file):
                shutil.rmtree(file)
            print(f"Deleting file: {file} permanently")  
        elif not delete:
            print("Safe mode enabled please set delete to true")
            return

def print_file_size(paths):
    size = 0
    for path in paths:
        for root, _, files in os.walk(path):
            for file in files:
                size += os.path.getsize(os.path.join(root, file))
    
    print(f"Total size: {size / 1_000_000_000} GB")

def get_all_torrent_folders():
    torrent_folders = set()
    for torrent_file in os.listdir(TORRENT_PATH):
        torrent_file = os.path.join(TORRENT_PATH, torrent_file)
        if os.path.isfile(torrent_file) and torrent_file.endswith(".torrent"):
            torrent_info = lt.torrent_info(torrent_file)
            location = get_torrent_data_location(torrent_info.name())
            if location != -1:
                torrent_folders.add(location)
    return torrent_folders

def get_torrent_data_location(torrent_name):
    index = 0
    try:
        while(not os.path.exists(location := os.path.join(DOWNLOAD_PATH, LABELS[index], torrent_name))):
            index += 1
    except IndexError:
        print(f"Unable to find location for torrent {torrent_name}")
        location = -1

    return location

if __name__ == "__main__":
    main()