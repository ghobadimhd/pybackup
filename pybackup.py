#!/usr/bin/python3
from datetime import datetime
import tarfile
import yaml
import subprocess as sp
import os
def read_config(config_path):
    with open(config_path, 'r') as config_file:
        raw_config = config_file.read()
    return yaml.load(raw_config)

def make_archive(name, files):
    try:
        tar = tarfile.open(name+'.tar.bz2', 'w:bz2')
        files = [files] if not isinstance(files, list) else files
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

def main():
    config = read_config('/etc/pybackup.yaml')
    today = datetime.today()
    date = '{0}-{1}-{2}'.format(today.year, today.month, today.day)
    backup_name = config.get('name', '') + '-' + date
    #check base_dir exitst if it's not make it
    if not os.path.exists(config['base_dir']):
        os.makedirs(config['base_dir'])

    # change directory to base_dir
    os.chdir(config['base_dir'])
    os.makedirs(backup_name)
    os.chdir(backup_name)

    for archive in config.get('archives', []):
        src = archive['src']
        dest = archive['dest']
        #print(src)
        if not isinstance(dest, str):
            print('error: destination most be a path')
            continue
        make_archive(dest, src)

    for database, file in config.get('mysql', []):
        mysqldump(config['user'], config['password'], database, file)

    if config.get('archive_all', False):
        os.chdir(base_dir)
        make_archive(backup_name,backup_name+'tar.bz2')

if __name__ == '__main__':
    main()
