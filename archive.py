"""this module for archiving file using tar command
tarfile module """

import os
import tarfile
import subprocess
import shutil
from datetime import datetime

def convert_to_list(param):
    """convert non list parameter to list"""
    param = [param] if not isinstance(param, list) else param
    if isinstance(param, list):
        return param
    else:
        return [param]

def tar_create(name, files, compress_type='bz2', remove_old=False):
    """make archive with tar command"""
    compress_types = {'bz2':'-j', 'gz':'-z', '':''}
    compress_type = '' if compress_type is None else compress_type
    #remove trailing /
    if name[-1] == '/':
        name = name[:-1]
    #add tar postfix to name of file
    name = str.strip(name) + '.tar'
    #add compress type postfix to file
    name = name + '.' + compress_type if compress_type != '' else name

    if compress_type not in compress_types:
        #FIXME: fire proper exeption
        return False

    if os.path.exists(name):
        if remove_old:
            shutil.rmtree(name)
        else:
            # create backup from old file (or directory) with timestamp
            timestamp = datetime.now().timestamp()
            timestamp = str(int(timestamp))
            shutil.move(name, name + '.' + timestamp)

    cmd = ['tar', '-c', compress_types[compress_type], '-f' , name ]
    cmd.extend(convert_to_list(files))
    process = subprocess.run(cmd,stderr=subprocess.PIPE)
    if process.returncode == 0:
        return True
    else:
        print(process.stderr)
        return False

def tarfile_create(name, files, compress_type='bz2', remove_old=False):
    """make tar archive with tarfile module"""
    compress_types = ['bz2', 'gz', '']
    compress_type = '' if compress_type is None else ':' + compress_type
    #remove trailing /
    if name[-1] == '/':
        name = name[:-1]
    #add tar postfix to name of file
    name = str.strip(name) + '.tar'
    #add compress type postfix to file
    name = name + '.' + compress_type if compress_type != '' else name

    if compress_type not in compress_types:
        #FIXME: fire proper exeption
        return False

    if os.path.exists(name):
        if remove_old:
            shutil.rmtree(name)
        else:
            # create backup from old file (or directory) with timestamp
            timestamp = datetime.now().timestamp()
            timestamp = str(int(timestamp))
            shutil.move(name, name + '.' + timestamp)
    try:
        tar = tarfile.open(name, 'w' + compress_type)
        files = convert_to_list(files)
        for file in files:
            print('archiving : ' + file)
            tar.add(file)
            print(file)
        tar.close()
    except IOError as e:
        print('archive error : '+ e.strerror + '\n\tfilename :' + e.filename)