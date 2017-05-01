#!/usr/bin/python3
import sys
from datetime import datetime
import tarfile
import yaml
import subprocess as sp
import os
import shutil
import getpass
import archive

DEFAULT_CONFIG_FILE = '/etc/pybackup.yaml'

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
    config['archive_engine'] = config.get('archive_engine', 'tar')
    # check configuration parameter
    if 'databases' in config:
        config['mysql_user'] = config.get('mysql_user', getpass.getuser())
        config['mysql_password'] = config.get('mysql_password', None)
        config['mysql_password'] = str(config['mysql_password'])

    return config

def make_archive(name, files, compress_type='bz2', remove_old=False, engine='tar'):
    engines = {'tar':archive.tar_create, 'tarfile':archive.tarfile_create}
    engines[engine](name, files, compress_type, remove_old)

def mysqldump(database, file, user, password=None):

    cmd = ['mysqldump', database, '-u', user, '-r', file + '.sql']
    if password is not None:
        cmd.append('--password='+password)
    print('dumping database : ' + database)

    process = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    if process.returncode > 0:
        print("mysqldump error: " + process.stderr)
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
    # load config file 
    if len(sys.argv) > 2 and sys.argv[1] =='-c':
        config_file = sys.argv[2]
    else:
        print('using default config path : ' + DEFAULT_CONFIG_FILE)
        config_file = DEFAULT_CONFIG_FILE
    
    # parse config file
    config = read_config(config_file)
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
        make_archive(dest, src, config['compress_type'], engine=config['archive_engine'])

    for database in config.get('databases', []):
        mysqldump(database['name'], database['file'], config['mysql_user'], config['mysql_password'])

    if config.get('archive_all', False):
        os.chdir(config['base_dir'])
        make_archive(backup_name, backup_name)

    if config['remove_raw_dir']:
        print('removing : ' + backup_name + ' raw directory ...')
        shutil.rmtree(os.path.join(config['base_dir'],backup_name))
if __name__ == '__main__':
    main()
