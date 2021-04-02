# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 15:19:32 2013

@author: jpeacock-pr
"""

import time
import os
import mtpy.usgs.zen as zen
import numpy as np
import scipy.signal as sps
import struct
import mtpy.processing.filter as mtfilt

#rr_fn2 = r"d:\Peacock\MTData\mbrr\ZEUS3268.Z3D"
rr_fn2 = r"c:\MT\mb187\mb187_20140603_000000_4096_EX.Z3D"
save_path = os.path.dirname(rr_fn2)
comp = 'EX'

starttime = '2014-06-01,02:38:36'
dt_fmt = '%Y-%m-%d,%H:%M:%S'

t1 = time.mktime(time.strptime(starttime, dt_fmt))

header_len = 512*2
gps_stamp = '\xff\xff\xff\xff'
gps_stamp_len = 36
nbytes = 4
gps_week = 1795
df0 = 4096

notches =  list(np.arange(60,2048,60))
notchradius =  0.5
freqrad =  0.5
rp = 0.1
nfkwargs = {'notches':notches, 'notchradius':notchradius,
            'freqrad':freqrad, 'rp':rp}

stamp_lst = ['gps','time', 'lat', 'lon', 'status', 'gps_accuracy', 
             'temperature']
                   
data_types = [np.int32, np.int32, np.float64, np.float64, np.uint32, np.int32, 
              np.float32]
                    
data_type = np.dtype([(st, dt) for st, dt in 
                             zip(stamp_lst, data_types)])

block1_seconds = 5*60          #4096 for 5 minutes
block2_seconds = 15*60         #1024 for 15 minutes
block3_seconds = 5*60*60+40*60 #256 for 5 hours and 40 minutes

block1_df = 4096
block2_df = 1024
block3_df = 256

#number of maximum samples per data block after down sampling 
block1_len = (block1_df)*block1_seconds
block2_len = (block1_df)*block2_seconds
block3_len = (block1_df)*block3_seconds

block_lst = [block1_len, block2_len, block3_len]
block_df = [block1_df, block2_df, block3_df]
block_seconds = [block1_seconds, block2_seconds, block3_seconds]
block_dec = [1,4,16]

sdt_lst = []
sdth_lst = []
t2 = float(t1)
t3 = float(t1)
for ii in range(15):
    for blen, bsec, bdf, bdec, nn in zip(block_lst, block_seconds, 
                                         block_df, block_dec, 
                                         range(len(block_lst))):
        dt2 = time.localtime(t2-15)
        sdate = time.strftime('%Y%m%d', dt2)
        stime = time.strftime('%H%M%S', dt2)
        sdt = time.strftime('%Y-%m-%d,%H:%M:%S', dt2)
        sdt_lst.append(sdt)
        t2 += bsec
        
        dt3 = time.localtime(t3)
        sdate = time.strftime('%Y%m%d', dt3)
        stime = time.strftime('%H%M%S', dt3)
        sdt = time.strftime('%Y-%m-%d,%H:%M:%S', dt3)
        sdth_lst.append(sdt)
        t3 += bsec



#create file instance
rfid2 = file(rr_fn2, 'rb')

#--> get header
header2 = rfid2.read(header_len)

#--> find the first gps stamp
gps_find = -1
gt2 = ''
zt = zen.Zen3D()
while gt2 != sdt_lst[0]:
    test_string = rfid2.read((df0/2+9)*4)
    zt = zen.Zen3D()
    zt._raw_data = test_string
    gps_index = zt.get_gps_stamp_location()
    if gps_index != -1:
        if gps_index >= (df0/2+9)*4-36:
            print 'reading extra'
            zt._raw_data += rfid2.read(gps_stamp_len)

        test_stamp = zt.get_gps_stamp(gps_index)[0]
        gt2 = zt.get_date_time(gps_week, test_stamp['time'])
    else:
        pass 
    
#make sure the values after the gps_stamp are read in
start_string = zt._raw_data[gps_index+gps_stamp_len:]

tt = 0  # index for block length
ss = 1  # index for starting time
gt = sdt_lst[0]
#while tt == 0:

ii = 0  # index for data 
jj = 0  #i index for gps stamps
gps_string = 0

#logfid = file(r"d:\Peacock\MTData\mbrr\SplitLog_{0}.log".format(comp), 'w')
logfid = file(r"c:\MT\mb187\SplitLog_{0}.log".format(comp), 'w')

ftell = rfid2.tell()
while ss < 45:
    while tt < 3:
        print '='*60
        print 'Start {2} Schedule={0},  df={1}'.format(sdt_lst[ss], block_df[tt],
                                         time.ctime())
        #change information in header block to fit the new file
        new_df = block_df[tt]
        new_header = header2.replace('2014-05-25,00:00:00', sdth_lst[ss-1])
        new_header = new_header.replace('4096', str(new_df))
        
        logfid.write('='*72+'\n')
        logfid.write(new_header)
        logfid.write('='*72+'\n')
        
        #decimation factor
        dec = float(block_dec[tt])
        
        #create empty arrays for time series and gps stamps
        ts_array = np.zeros(block_lst[tt])
        stamp_array = np.zeros(block_seconds[tt], dtype=data_type)
        if ss == 1:
            stamp_array[0] = test_stamp
        
        while gt != sdt_lst[ss] and ss <= block3_seconds and \
                                                jj <= block_seconds[tt]:
            if ii == 0:
                test_string = start_string+rfid2.read((df0/2+9)*4)
            else:
               test_string = rfid2.read((df0/2+9)*4)
            zt = zen.Zen3D()
            zt._raw_data = test_string
            try:
                gps_index = zt.get_gps_stamp_location()
            except IndexError:
                zt._raw_data += rfid2.read(36)
                gps_index = zt.get_gps_stamp_location()
            
            #sometimes gps index found does not actually contain gps stamp
            if gps_index < 4:
                gps_index = zt._raw_data.find(gps_stamp)
                
            if gps_index != -1:
                if gps_index >= (df0/2+9)*4-36:
                    zt._raw_data += rfid2.read(gps_stamp_len)
        
                stamp_array[jj], gps_index, gps_dweek = \
                                                    zt.get_gps_stamp(gps_index)
                if stamp_array[jj]['time'] < 86400*2:
                #if gps_dweek != 0:
                    gt = zt.get_date_time(gps_week+1, stamp_array[jj]['time'])
                    new_header = new_header.replace(str(gps_week), 
                                                    str(gps_week+1))
                else:
                    gt = zt.get_date_time(gps_week, stamp_array[jj]['time'])
                logfid.write('{0}{1}  {2}  {3}'.format(' '*4, jj, gt, 
                                                         rfid2.tell()))
                if np.remainder(jj, 4) == 0:
                    logfid.write('\n')
                jj += 1
                
                #read in time series before the gps stamp
                ts_int_array = np.fromstring(zt._raw_data[0:gps_index], 
                                             dtype=np.int32)
                nts = ts_int_array.shape[0]
                ts_array[ii:ii+nts] = ts_int_array
                ii += nts
                
                #check to see if the last stamp found was the end of this block
                if len(zt._raw_data[gps_index+gps_stamp_len:])+ii < ts_array.shape[0]:
                    ts_int_array = np.fromstring(zt._raw_data[gps_index+gps_stamp_len:],
                                                 dtype=np.int32)
                    nts = ts_int_array.shape[0]
                    ts_array[ii:ii+nts] = ts_int_array
                    ii += nts
                #if it was then the starting string for the next file will be the
                #rest of the data.
                else:
                    start_string = zt._raw_data[gps_index+gps_stamp_len:]
                    ii = 0
            
            #put data into time series array    
            elif gps_index == -1:
                ts_int_array = np.fromstring(test_string, dtype=np.int32)
                nts = ts_int_array.shape[0]
                ts_array[ii:ii+nts] = ts_int_array
                ii += nts
                
        #----- write to a file ----
        new_date = sdt_lst[ss-1][0:10].replace('-', '')
        new_time = sdt_lst[ss-1][11:20].replace(':', '')
        new_fn = 'mb156_{0}_{1}_{2}_{3}.Z3D'.format(new_date, 
                                                   new_time, 
                                                   block_df[tt],
                                                   comp.upper())
                                                   
        #decimate the data by chuncks otherwise get a memory error
        #better it in npow(2) windows than on the fly
        if dec != 1:
            new_ts = np.zeros(int(ts_array.shape[0]/dec))
            nfkwargs['df'] = int(block_df[0])
            for nn in range(stamp_array.shape[0]):
                ts_block = ts_array[nn*df0:(nn+1)*df0]
                #apply a notch filter to reduce noise in the data
                ts_blockf, filt_lst = mtfilt.adaptive_notch_filter(ts_block,
                                                                   **nfkwargs)
                
                new_ts_block = sps.resample(ts_blockf, 
                                            int(df0/dec),
                                            window='hanning')
                new_ts[nn*new_df:(nn+1)*new_df] = new_ts_block
            ts_array = new_ts
            del new_ts
            
        #make sure no integers are out of range of i
        ts_array[np.where(ts_array>2.14e9)] = 2.14e9
        ts_array[np.where(ts_array<-2.14e9)] = -2.14e9    
                                                                                            
        nfid = file(os.path.join(r"c:\MT\mb156", new_fn), 'wb')
        nfid.write(new_header)
        for ll in range(stamp_array.shape[0]):
            #write gps stamp
            for skey,stype in zip(stamp_lst,
                                  ['i', 'i', 'd', 'd', 'I', 'i', 'f']):
                #make sure time is in the correct units
                if skey == 'time':
                    nfid.write(struct.pack(stype, stamp_array[ll][skey]*1024))
                
                #make sure lat and lon are in radians
                elif skey == 'lat' or skey == 'lon':
                    nfid.write(struct.pack(stype, 
                                           stamp_array[ll][skey]*np.pi/180))
                
                else:
                    nfid.write(struct.pack(stype, stamp_array[ll][skey]))
                    
            #write time series data between gps stamps
            nfid.write(struct.pack('i'*new_df,
                                   *ts_array[ll*new_df:(ll+1)*new_df]))
    
        nfid.close()
        print 'wrote file to {0}'.format(os.path.join(r"c:\MT\mb1587",
                                                      new_fn))
        print 'Ended at {0}'.format(time.ctime())
        logfid.write('-'*72+'\n')
        logfid.write('{0}{1}'.format(' '*4, os.path.join(r"c:\MT\mb187",
                                                      new_fn)))
        logfid.write('-'*72+'\n')
        #reset values
        ss += 1
        tt += 1
        jj = 0
        ii = 0
    #reset tt --> index for sampling rate, block length, etc
    tt = 0
    jj = 0
    ii = 0

logfid.close()
rfid2.close()
        
