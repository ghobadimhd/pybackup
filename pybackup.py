#!/usr/bin/python3
from datetime import datetime
import tarfile
import yaml
import subprocess as sp
import os
import shutil
import getpass

def read_config(config_path):
    with open(config_path, 'r') as config_file:
        raw_config = config_file.read()
    # set default parameter
    config = yaml.load(raw_config)
    config['name'] = config.get('name', 'pybackup')
    config['name_append_date'] = config.get('name_append_date', True)
    config['date_format'] = config.get('date_format', "%Y-%m-%d")
    config['archive_all'] = config.get('archive_all', True)
    config['remove_raw_dir'] = config.get('remove_raw_dir', True)
    config['compress_type'] = config.get('compress_type', 'bz2')
    config['send_email'] = config.get('send_email', False)
    config['base_dir'] = config.get('base_dir', os.path.abspath(os.curdir))
    config['rotate'] = config.get('rotate', 0)
    # check configuration parameter
    if 'databases' in config:
        config['mysql_user'] = config.get('mysql_user', getpass.getuser())
        config['mysql_password'] = config.get('mysql_password', None)

    return config

def make_archive(name, files, compress_type='bz2'):
    try:
        tar = tarfile.open(name+'.tar.' + compress_type, 'w:' + compress_type)
        files = [files] if not isinstance(files, list) else files
        for file in files:
            print('archiving : ' + file)
            tar.add(file)
            print(file)
        tar.close()
    except IOError as e:
        print('archive error : '+ e.strerror + '\n\tfilename :' + e.filename)

def mysqldump(database, file, user, password=None):
    if password is None:
        cmd = 'mysqldump -u  {0} {2} -r {3}'.format(user, password, database, file + '.sql')
    else:
        cmd = 'mysqldump -u  {0} --password={1} {2} -r {3}'.format(user, password, database, file + '.sql')

    print('dumping database : ' + database)
    status, stdout = sp.getstatusoutput(cmd)
    if status > 0:
        print("mysqldump error: " + stdout)
        return False
    else:
        return True

def change_dir(directory):
    """chdir to directory if not exists to try to make it"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.isdir(directory):
        return False
    try:
        os.chdir(directory)
        return True
    except Exception as e:
        print('change_dir error : ' + e.str)
        return False

def main():
    config = read_config('/etc/pybackup.yaml')
    if config['name_append_date']:
        today = datetime.today()
        date = ('{:'+config['date_format'] +'}').format(today)
        backup_name = config['name'] + '-' + date
    else:
        backup_name = config['name']
    # chdir to base_dir
    if not change_dir(os.path.join(config['base_dir'],backup_name)):
        print("error : failed to chdir ")
        print('abort')
        exit(1)

    for archive in config.get('archives', []):
        src = archive['src']
        dest = archive['dest']
        if not isinstance(dest, str):
            print('error: destination most be a path')
            continue
        make_archive(dest, src, config['compress_type'])

    for database in config.get('databases', []):
        mysqldump(database['name'], database['file'], config['mysql_user'], config['mysql_password'])

    if config.get('archive_all', False):
        os.chdir(config['base_dir'])
        make_archive(backup_name, backup_name)

    if config['remove_raw_dir']:
        print('removing : ' + backup_name)
        shutil.rmtree(os.path.join(config['base_dir'],backup_name))
if __name__ == '__main__':
    main()
