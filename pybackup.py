#!/usr/bin/python3

import yaml
def read_config(config_path):
    with open(config_path, 'r') config_file:
        raw_config = config_file.read()
    return yaml.load(raw_cnofig)

def make_archive(name, files):
    try:
        tar = tarfile.open(name, 'w;bz2')
        files = [files] if isinstance(files,list) else files
        for file in files:
            print(file)
            tar.add(file)
        tar.close()
    except IOError as e:
        print(e.strerror)

