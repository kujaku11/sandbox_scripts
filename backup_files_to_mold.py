# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 10:08:47 2015

@author: jpeacock
"""
import os
import paramiko
import getpass
import time

#==============================================================================
# Input variables
#==============================================================================
#folder_list = ['LV', 'MonoBasin', 'ParaviewFiles', 'Proposals', 'PyScripts',
#               'Receipts', 'Reviews', 'TexDocs', 'Travel', 'Forms',
#               'MountainPass', 'Geothermal', 'iMush', 'SanPabloBay', 
#               'SaudiArabia', 'ShanesBugs', 'Antarctica']
folder_list = ['PyScripts', 'ModEM', 'wsinv3d']

#dirpath = r"/mnt/hgfs/jpeacock/Documents"
dirpath = r"/home/jpeacock/Documents"
os.chdir(dirpath)

host = 'mold.wr.usgs.gov'
user_name = input("type username as 'user_name': ")
#os.system('stty -echo')
pass_word = getpass.getpass("type password: ", stream=None)

mold_root = r"/gp/{0}/Documents".format(user_name)
port = 22

log_fid = file(r"/home/jpeacock/file_transfer_{0}.log".format(
                time.strftime('%Y_%m_%d', time.localtime())), 
                'w')
#==============================================================================
# Helper functions
#==============================================================================
def check_dir_path(path, sftp_obj):
    dir_list = path.split(os.sep)
    dir_path = os.path.join(os.sep, dir_list[1], dir_list[2])
    return_string = []
    for ii, dir_test in enumerate(dir_list[3:]):
        dir_path = os.path.join(dir_path, dir_test)
        try:
            sftp_obj.mkdir(dir_path)
            return_string.append('--> made directory {0}\n'.format(dir_path))
        except IOError:
            return_string.append('{0} already exists\n'.format(dir_path))
            
    return return_string
            
def check_fn_exists(fn, sftp_obj):
    fn_dir_path = os.path.dirname(fn)
    r_string = check_dir_path(fn_dir_path, sftp_obj)
    try:
        sftp.stat(fn)
    except IOError, e:
        if e[0] == 2:
            return False, r_string

    return True, r_string
    
def check_fn_date(mold_fn, local_fn, sftp_obj):
    m_time = sftp_obj.stat(mold_fn).st_mtime
    l_time = os.stat(local_fn).st_mtime
    
    # if the local file is newer, larger time, return true to copy
    if l_time > m_time:
        return True
    else:
        return False
    

#==============================================================================
## create a sftp instance
transport = paramiko.Transport(host, port)
transport.connect(username=user_name, password=pass_word)
sftp = paramiko.SFTPClient.from_transport(transport)

# loop over all folders and files
start_time = time.ctime()
for folder in folder_list:
    try:
        sftp.mkdir(os.path.join(mold_root, folder))
    except IOError:
        pass
    for root, dirs, files in os.walk(os.path.join(dirpath, folder), topdown=True):
        mold_root = r"/gp/{0}/{1}".format(user_name, 
                                          root[root.find(user_name[-1])+2:])
        # check the directories in a root path
        for fn_dir in dirs:
            mold_dir = os.path.join(mold_root, fn_dir)
            r_str = check_dir_path(mold_dir, sftp)
            for rr in r_str:
                log_fid.write(rr)
        
        # copy files if they don't already exist
        for fn in files:
            local_path = os.path.join(root, fn)
            mold_path = os.path.join(mold_root, fn)
            
            # check to see if the local files exists, sometimes there are
            # broken links.
            if os.path.isfile(local_path) is False:
                continue
            
            fn_exist, r_str = check_fn_exists(mold_path, sftp)
            if fn_exist == False:
                 sftp.put(local_path, mold_path)
                 log_fid.write('copied: {0} to {1}\n'.format(local_path, mold_path))
            else:
                fn_time = check_fn_date(mold_path, local_path, sftp)
                if fn_time == True:
                    sftp.put(local_path, mold_path)
                    log_fid.write('copied: {0} to {1}\n'.format(local_path, 
                                  mold_path))
         
## close everything        
sftp.close()
transport.close()
log_fid.close()

end_time = time.ctime()

## print time
print 'Started at: {0}'.format(start_time)
print 'Ended   at: {0}'.format(end_time)
