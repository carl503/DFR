from typing import Final
from os.path import join
import libtorrent as lt
import os
import shutil

TORRENT_PATH: Final = "/var/lib/docker/volumes/transmission/_data/transmission-home/torrents"
DOWNLOAD_PATH: Final = "/mnt/pool/downloads/completed"
LABELS: Final = ["radarr", "tv-sonarr", ""]
IGNORE_FOLDERS: Final = ["tv-sonarr", "radarr", "moana"]

def main():
    dangling_files = find_dangling_files()
    if len(dangling_files) == 0: print("There are no dangling files, exiting")
    else:
        print_dangling_files_info(dangling_files)
        delete_files(dangling_files, (answer := input("Please type yes to remove the listed files: ").lower())  == "yes" or answer == "y")

def find_dangling_files():
    local_files = set([join(DOWNLOAD_PATH, file_name) for file_name in os.listdir(DOWNLOAD_PATH) if file_name not in IGNORE_FOLDERS])
    return local_files.difference(get_all_torrent_folders())

def delete_files(files, delete=False):
    for file in (f for f in files if delete):
        if os.path.isfile(file): os.remove(file)
        elif os.path.isdir(file): shutil.rmtree(file)
        print(f"Deleting file: {file} permanently")  

    if not delete: print("Files won't be deleted exiting")

def print_dangling_files_info(paths):
    size = sum([os.path.getsize(join(root, file)) for path in paths for root, _, files in os.walk(path) for file in files])
    print("The following files can be safely deleted:")
    print(*paths, sep="\n")
    print(f"Total size: {size / 1_000_000_000} GB")

def get_all_torrent_folders():
    torrent_folders = set()
    for torrent_file in (join(TORRENT_PATH, tf) for tf in os.listdir(TORRENT_PATH)):
        if os.path.isfile(torrent_file) and torrent_file.endswith(".torrent"):
            try:
                torrent_info = lt.torrent_info(torrent_file)
                location = [loc for count, path in enumerate(LABELS) if (os.path.exists(loc := join(DOWNLOAD_PATH, LABELS[count], torrent_info.name())))]
                if len(location) == 1: torrent_folders.add(location[0])
            except RuntimeError:
                print(f"An error occured while trying to read torrent {torrent_file}")

    return torrent_folders

if __name__ == "__main__":
    main()