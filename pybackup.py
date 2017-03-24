#!/usr/bin/pyt hon3
import tarfile
import yaml
import subprocess as sp
def read_config(config_path):
    with open(config_path, 'r') as config_file:
        raw_config = config_file.read()
    return yaml.load(raw_config)

def make_archive(name, files):
    try:
        tar = tarfile.open(name, 'w:bz2')
        files = [files] if isinstance(files, list) else files
        for file in files:
            print(file)
            tar.add(file)
        tar.close()
    except IOError as e:
        print(e.strerror)

def mysqldump(user, password, database, file):
    cmd = 'mysqldump -u  {0} -P {1} {2} > {4}'.format(user, password, database, file)
    #cmd = ['mysqldump' , '-u', user, '-p', password, database ]
    status, stdout = sp.getstatusoutput(cmd)
    if status > 0:
        print("mysqldump error: " + stdout)
        return False
    else:
        return True