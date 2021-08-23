from typing import Final
from os.path import join
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
    for torrent_file in (join(TORRENT_PATH, tf) for tf in os.listdir(TORRENT_PATH)):
        if os.path.isfile(torrent_file) and torrent_file.endswith(".torrent"):
            try:
                torrent_info = lt.torrent_info(torrent_file)
                location = [loc for count, path in enumerate(LABELS) if (os.path.exists(loc := join(DOWNLOAD_PATH, LABELS[count], torrent_info.name())))]
                if len(location) and get_num_of_files(location[0]) != torrent_info.num_files():
                    files_to_delete += [*find_files_not_in_torrent(location[0], torrent_info)]
            except RuntimeError:
                print(f"An error occured while trying to read torrent {torrent_file}")

    return files_to_delete

def delete_files(files, delete=False):
    for file in (f for f in files if os.path.exists(f) and delete):
        #os.remove(file)
        print(f"Deleting file: {file} permanently")

    if not delete: print("Files won't be deleted exiting")

def get_file_size(torrents):
    size = sum([os.path.getsize(torrent) for torrent in torrents])
    print(f"Total size: {size / 1_000_000_000} GB")

def find_files_not_in_torrent(location, torrent_info):
    torrent_files = set([torrent_info.files().file_path(index, location.replace(torrent_info.name(), "")) for index in range(torrent_info.num_files())])
    files_on_disk = set([join(torrent_info.name(), root, file) for root, _, files in os.walk(location) for file in files])

    return files_on_disk.difference(torrent_files)        

def get_num_of_files(location):
    total = 1
    if os.path.isdir(location): total = sum([len(files) for _, _, files in os.walk(location)])
    return total

if __name__ == "__main__":
    main()