from os.path import join
from torrentool.api import Torrent
import os
import shutil

torrent_path = "/home/torrent/transmission/config/torrents"
base_path = "/mnt/pool/downloads/completed/"
paths = [base_path, os.path.join(base_path, "tv-sonarr"), os.path.join(base_path, "radarr")]
ignore_folders = set(["tv-sonarr", "radarr", "moana"])
found_files = set()
completed_download_files = set()

def remove_file(full_path):
    if os.path.exists(full_path):
        if os.path.isfile(full_path):
            print(f"Lösche Datei: {full_path}")
            #os.remove(full_path)
        elif os.path.isdir(full_path):
            print(f"Lösche Ordner: {full_path}")
            #shutil.rmtree(full_path)

for path in paths:
    completed_download_files |= set(os.listdir(path))

for torrent in os.listdir(torrent_path):
    try:
        file = Torrent.from_file(os.path.join(torrent_path, torrent)).files[0].name.split("/")[0]
        if file in completed_download_files: found_files.add(file)
    except IndexError:
        print(f"Torrent {torrent} konnte nicht verarbeitet werden!")

files_to_delete = completed_download_files.difference(found_files) - ignore_folders

if len(files_to_delete) > 0:
    print(f"Die folgenden Dateien können gelöscht werden:")
    for file_to_delete in files_to_delete:
        for path in paths:
            if file_to_delete in os.listdir(path):
                remove_file(os.path.join(path, file_to_delete))
                break # Optimierung muss noch getestet werden
else:
    print(f"Es gibt keine Dateien, welche nicht einem Torrent zugeordnet werden können.")