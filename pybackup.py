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
            print('archiving : '+file)
            tar.add(file)
        tar.close()
    except IOError as e:
        print(e.strerror)

def mysqldump(user, password, database, file):
    cmd = 'mysqldump -u  {0} --password={1} {2} -r {3}'.format(user, password, database, file+'.sql')
    print('dumping database : '+database)
    status, stdout = sp.getstatusoutput(cmd)
    if status > 0:
        print("mysqldump error: " + stdout)
        return False
    else:
        return True

def main():
    config = read_config('/etc/pybackup.yaml')
    today = datetime.today()
    date = '{:%Y-%m-%d}'.format(today)
    backup_name = config.get('name', '') + '-' + date
    #check base_dir exitst if it's not make it
    if not os.path.exists(config['base_dir']):
        os.makedirs(config['base_dir'])

    # change directory to base_dir
    os.chdir(config['base_dir'])
    if not os.path.exists(backup_name):
        os.makedirs(backup_name)
    os.chdir(backup_name)

    for archive in config.get('archives', []):
        src = archive['src']
        dest = archive['dest']
        if not isinstance(dest, str):
            print('error: destination most be a path')
            continue
        make_archive(dest, src)

    for database in config.get('databases', []):
        mysqldump(config['mysql_user'], config['mysql_password'], database['name'], database['file'])

    if config.get('archive_all', False):
        os.chdir(config['base_dir'])
        make_archive(backup_name, backup_name)

if __name__ == '__main__':
    main()
