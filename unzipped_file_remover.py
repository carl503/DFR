from typing import Final
from torrentool.api import Torrent
import libtorrent as lt
import os
import shutil

TORRENT_PATH: Final = "/var/lib/docker/volumes/transmission/_data/transmission-home/torrents"
DOWNLOAD_PATH: Final = "/mnt/pool/downloads/completed"
LABELS: Final = ["radarr", "tv-sonarr", ""]

def main():
    files_to_delete = get_files_to_delete()
    get_file_size(files_to_delete)
    delete_files(files_to_delete)

def get_files_to_delete():
    files_to_delete = []
    for torrent_file in os.listdir(TORRENT_PATH):
        torrent_file = os.path.join(TORRENT_PATH, torrent_file)
        if os.path.isfile(torrent_file) and torrent_file.endswith(".torrent"):
            torrent_info = lt.torrent_info(torrent_file)
            location = get_torrent_data_location(torrent_info.name())
            if location != -1 and get_num_of_files(location) != torrent_info.num_files():
                files_to_delete += [*find_files_not_in_torrent(location, torrent_info)]

    return files_to_delete

def delete_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)
        print(f"Deleting file: {file} permanently")  

def get_file_size(torrents):
    size = 0
    for torrent in torrents:
        size += os.path.getsize(torrent)
    
    print(f"Total size: {size / 1_000_000_000} GB")

def find_files_not_in_torrent(location, torrent_info):
    torrent_files = set([torrent_info.files().file_path(index, location.replace(torrent_info.name(), "")) for index in range(torrent_info.num_files())])
    files_on_disk = set()

    for root, _, files in os.walk(location):
        for file in files:
            files_on_disk.add(os.path.join(torrent_info.name(), root, file))

    return files_on_disk.difference(torrent_files)
            

def get_num_of_files(location):
    total = 1
    if os.path.isdir(location):
        total = 0
        for _, _, files in os.walk(location):
            total += len(files)
    
    return total

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