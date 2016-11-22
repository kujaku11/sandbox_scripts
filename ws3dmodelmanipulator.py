# -*- coding: utf-8 -*-
"""
Created on Mon May 20 16:00:13 2013

@author: jpeacock-pr
"""

import mtpy.modeling.ws3dtools as ws
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import numpy as np
from matplotlib.ticker import MultipleLocator
import matplotlib.colorbar as mcb
import matplotlib.colors as colors


class WS3DModelManipulator(object):
    """
    will plot a model from wsinv3d or init file so the user can manipulate the 
    resistivity values relatively easily.  At the moment only plotted
    in map view.
    
    
    """

    def __init__(self, model_fn=None, init_fn=None, data_fn=None,
                 reslst=None, mapscale='km', plot_yn='y', xlimits=None, 
                 ylimits=None, cbdict={}):
        
        self.model_fn = model_fn
        self.init_fn = init_fn
        self.data_fn = data_fn
        
        #make a default resistivity list to change values
        if reslst is None:
            self.reslst = np.array([.3, 1, 10, 50, 100, 500, 1000, 5000],
                                   dtype=np.float)
        
        else:
            self.reslst = reslst
            
        #make a dictionary of values to write to file.
        self.resdict = dict([(res, ii) for ii,res in enumerate(self.reslst,1)])
        
        #--> set map scale
        self.mapscale = mapscale
        
        #--> set map limits
        self.xlimits = xlimits
        self.ylimits = ylimits
        
        self.cbdict = cbdict

        self.font_size = 7
        self.dpi = 300
        self.fignum = 1
        self.figsize = [8,8]
        self.cmap = 'jet_r'
        self.depth_index = 0
        
        #station locations in relative coordinates read from data file
        self.station_x = None
        self.station_y = None
        
        #plot on initialization
        self.plot_yn = plot_yn
        if self.plot_yn=='y':
            self.plot()
    
    #---read files-------------------------------------------------------------    
    def read_file(self):
        """
        reads in initial file or model file and set attributes:
            -resmodel
            -xgrid
            -ygrid
            -zgrid
            -reslst if initial file
            
        """

        if self.model_fn is not None and self.init_fn is None:
            mtuple = ws.readModelFile(self.model_fn)
            self.xg = mtuple[0]
            self.yg = mtuple[1]
            self.zg = mtuple[2]
            self.res = mtuple[3]
            
        elif self.init_fn is not None and self.model_fn is None:
            mtuple = ws.readInit3D(self.init_fn)
            self.xg = mtuple[0]
            self.yg = mtuple[1]
            self.zg = mtuple[2]
            self.res = mtuple[5]
            self.reslst = mtuple[3]
        elif self.init_fn is None and self.model_fn is None:
            print 'Need to input either an initial file or model file to plot'
        else:
            print 'Input just initial file or model file not both.'
            
        if self.data_fn is not None:
            dtuple = ws.readDataFile(self.data_fn)
            self.station_x = dtuple[3]
            self.station_y = dtuple[4]
            
            
            
    #---plot model-------------------------------------------------------------    
    def plot(self):
        """
        plots the model with:
            -a radio dial for depth slice 
            -radio dial for resistivity value
            
        """
        cmin = np.log10(min(self.reslst))
        cmax = np.log10(max(self.reslst))
        
        #-->Plot properties
        plt.rcParams['font.size'] = self.font_size
        
        fdict = {'size':self.font_size+2, 'weight':'bold'}
    
        cblabeldict = {-5:'$10^{-5}$',
                       -4:'$10^{-4}$',
                       -3:'$10^{-3}$',
                       -2:'$10^{-2}$',
                       -1:'$10^{-1}$',
                        0:'$10^{0}$',
                        1:'$10^{1}$',
                        2:'$10^{2}$',
                        3:'$10^{3}$',
                        4:'$10^{4}$',
                        5:'$10^{5}$',
                        6:'$10^{6}$',
                        7:'$10^{7}$',
                        8:'$10^{8}$'}
        
        self.read_file()
        
        #--> scale the map coordinates
        if self.mapscale=='km':
            dscale = 1000.
        if self.mapscale=='m':
            dscale = 1.
            
        self.xg /= dscale
        self.yg /= dscale
        self.zg /= dscale
        
        #make a mesh grid for plotting
        xgrid, ygrid = np.meshgrid(self.xg, self.yg)
        
        self.fig = plt.figure(self.fignum, figsize=self.figsize, dpi=self.dpi)
        self.ax1 = self.fig.add_subplot(1, 1, 1, aspect='equal')
        
        plt.clf()
        self.ax1.pcolormesh(xgrid, ygrid, 
                            np.log10(np.rot90(self.res[:,:,self.depth_index],3)),
                            cmap=self.cmap,
                            vmin=cmin,
                            vmax=cmax)
                       
        #plot the stations
        if self.station_x is not None:
            for ee,nn in zip(self.station_x, self.station_y):
                self.ax1.text(ee/dscale, nn/dscale,
                              '*',
                              verticalalignment='center',
                              horizontalalignment='center',
                              fontdict={'size':self.font_size-2,
                                        'weight':'bold'})

        #set axis properties
        if self.xlimits is not None:
            self.ax1.set_xlim(self.xlimits)
        else:
            self.ax1.set_xlim(xmin=self.yg.min(), xmax=self.yg.max())
        
        if self.ylimits is not None:
            self.ax1.set_ylim(self.ylimits)
        else:
            self.ax1.set_xlim(xmin=self.xg.min(), xmax=self.xg.max())
            
        self.ax1.xaxis.set_minor_locator(MultipleLocator(100*1./dscale))
        self.ax1.yaxis.set_minor_locator(MultipleLocator(100*1./dscale))
        
        self.ax1.set_ylabel('Northing ('+self.map_scale+')',fontdict=fdict)
        self.ax1.set_xlabel('Easting ('+self.map_scale+')',fontdict=fdict)
        
        self.ax1.set_title('Depth = {:.3f} '.format(self.zg[self.depth_index])+\
                      '('+self.map_scale+')',
                      fontdict=fdict)
        
        #plot the grid if desired              
        for xx in self.xg:
            self.ax1.plot([self.yg.min(), self.yg.max()],
                           [xx, xx],
                           lw=.1,
                           color='k')
        for yy in self.yg:
            self.ax1.plot([yy, yy], 
                          [self.xg.min(), self.xg.max()],
                           lw=.1,
                           color='k')
        
        #plot the colorbar
        try:
            self.cb_dict['orientation']
        except KeyError:
            self.cb_dict['orientation']='horizontal'
        
        if self.cb_dict['orientation']=='horizontal':
            try:
                self.ax2 = self.fig.add_axes(self.cb_dict['position'])
            except KeyError:
                self.ax2 = self.fig.add_axes((self.ax1.axes.figbox.bounds[3]-.225,
                                    self.ax1.axes.figbox.bounds[1]+.05,.3,.025))
                                    
        elif self.cb_dict['orientation']=='vertical':
            try:
                self.ax2 = self.fig.add_axes(self.cb_dict['position'])
            except KeyError:
                self.ax2 = self.fig.add_axes((self.ax1.axes.figbox.bounds[2]-.15,
                                    self.ax1.axes.figbox.bounds[3]-.21,.025,.3))
        
        self.cb = mcb.ColorbarBase(self.ax2,cmap=self.cmap,
                                   norm=colors.Normalize(vmin=min(self.reslst),
                                                         vmax=max(self.reslst)),
                                   orientation=self.cb_dict['orientation'])
                            
        if self.cb_dict['orientation']=='horizontal':
            self.cb.ax.xaxis.set_label_position('top')
            self.cb.ax.xaxis.set_label_coords(.5,1.3)
            
            
        elif self.cb_dict['orientation']=='vertical':
            self.cb.ax.yaxis.set_label_position('right')
            self.cb.ax.yaxis.set_label_coords(1.25,.5)
            self.cb.ax.yaxis.tick_left()
            self.cb.ax.tick_params(axis='y',direction='in')
                            
        self.cb.set_label('Resistivity ($\Omega \cdot$m)',
                     fontdict={'size':self.font_size})
        self.cb.set_ticks(np.arange(min(self.reslst),max(self.reslst)+1))
        self.cb.set_ticklabels([cblabeldict[cc] 
                            for cc in np.arange(cmin,cmax+1)])
                            
        plt.show()

                        

        
        
            
        
        