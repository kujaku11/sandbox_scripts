# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 17:39:21 2013

@author: jpeacock-pr
"""

import os
import shutil

githubpath=r"c:\Users\jpeacock-pr\Documents\GitHub\mtpy\mtpy"
pyspath = r"c:\Python27\Lib\site-packages\mtpy"
#folders=['imaging','core','analysis', 'modeling']
folders=['modeling']


for folder in folders:
    for fn in os.listdir(os.path.join(pyspath,folder)):
        if os.path.isfile(os.path.join(githubpath,folder,fn)):
            fnp=os.path.join(pyspath,folder,fn)
            timep=os.path.getmtime(fnp)
            fng=os.path.join(githubpath,folder,fn)
            timeg=os.path.getmtime(fng)
    #        print fn1, t1
    #        print fn2, t2
            if timep>timeg:
                shutil.copy(fnp,fng)
                print 'copied %s to %s' % (fnp,fng)
    #        elif t2>t1:
    #            shutil.copy(fn2,fn1)
    #            print 'copied %s to %s' % (fn2,fn1)
    