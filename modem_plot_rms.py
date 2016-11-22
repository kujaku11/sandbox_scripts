# -*- coding: utf-8 -*-
"""
Created on Mon Nov 03 16:08:08 2014

@author: jpeacock-pr
"""

import mtpy.modeling.modem_new as modem
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.colorbar as mcb
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
import os


class Plot_RMS_Maps(object):
    """
    plots the RMS as (data-model)/(error) in map view for all components
    of the data file.  Gets this infomration from the .res file output
    by ModEM.
    
    """
    
    def __init__(self, residual_fn, **kwargs):
        self.residual_fn = residual_fn
        self.residual = None
        self.save_path = kwargs.pop('save_path', os.path.dirname(self.residual_fn))

        self.period_index = kwargs.pop('period_index', 0)        
        
        self.subplot_left = kwargs.pop('subplot_left', .1)
        self.subplot_right = kwargs.pop('subplot_right', .9)
        self.subplot_top = kwargs.pop('subplot_top', .95)
        self.subplot_bottom = kwargs.pop('subplot_bottom', .1)
        self.subplot_hspace = kwargs.pop('subplot_hspace', .1)
        self.subplot_vspace = kwargs.pop('subplot_vspace', .01)

        self.font_size = kwargs.pop('font_size', 8)
        
        self.fig_size = kwargs.pop('fig_size', [7.75, 6.75])
        self.fig_dpi = kwargs.pop('fig_dpi', 200)
        self.fig_num = kwargs.pop('fig_num', 1)
        
        self.rms_max = kwargs.pop('rms_max', 5)
        self.rms_min = kwargs.pop('rms_min', 0)
        
        self.tick_locator = kwargs.pop('tick_locator', None)
        self.pad_x = kwargs.pop('pad_x', None)
        self.pad_y = kwargs.pop('pad_y', None)
        
        # colormap for rms, goes white to black from 0 to rms max and 
        # red below 1 to show where the data is being over fit
        self.rms_cmap_dict = {'red':((0.0, 1.0, 1.0), 
                                    (0.2, 1.0, 1.0),
                                    (1.0, 0.0, 0.0)),
                             'green':((0.0, 0.0, 0.0), 
                                      (0.2, 1.0, 1.0),
                                      (1.0, 0.0, 0.0)),
                             'blue':((0.0, 0.0, 0.0),
                                     (0.2, 1.0, 1.0),
                                     (1.0, 0.0, 0.0))}
                      
        self.rms_cmap = colors.LinearSegmentedColormap('rms_cmap', 
                                                       self.rms_cmap_dict, 
                                                       256)
                                                       
        self.plot_z_list = [{'label':r'$Z_{xx}$', 'index':(0, 0), 'plot_num':1},
                           {'label':r'$Z_{xy}$', 'index':(0, 1), 'plot_num':2},
                           {'label':r'$Z_{yx}$', 'index':(1, 0), 'plot_num':3},
                           {'label':r'$Z_{yy}$', 'index':(1, 1), 'plot_num':4},
                           {'label':r'$T_{x}$', 'index':(0, 0), 'plot_num':5},
                           {'label':r'$T_{y}$', 'index':(0, 1), 'plot_num':6}]
                           
    def read_residual_fn(self):
        if self.residual is None:
            self.residual = modem.Data()
            self.residual.read_data_file(self.residual_fn)
        else:
            pass
        
    def plot(self):
        """
        plot rms in map view
        """

        self.read_residual_fn()

        font_dict = {'size':self.font_size+2, 'weight':'bold'}
        rms_1 = 1./self.rms_max
        
        if self.tick_locator is None:
            x_locator = np.round((self.residual.data_array['lon'].max()-
                                    self.residual.data_array['lon'].min())/5, 2)
            y_locator = np.round((self.residual.data_array['lat'].max()-
                                    self.residual.data_array['lat'].min())/5, 2)
                                    
            if x_locator > y_locator:
                tick_locator = x_locator
            
            elif x_locator < y_locator:
                tick_locator = y_locator
            
        if self.pad_x is None:
            self.pad_x = tick_locator/2
        if self.pad_y is None:
            self.pad_y = tick_locator/2
        
        
        plt.rcParams['font.size'] = self.font_size
        plt.rcParams['figure.subplot.left'] = self.subplot_left
        plt.rcParams['figure.subplot.right'] = self.subplot_right
        plt.rcParams['figure.subplot.bottom'] = self.subplot_bottom
        plt.rcParams['figure.subplot.top'] = self.subplot_top
        plt.rcParams['figure.subplot.wspace'] = self.subplot_hspace
        plt.rcParams['figure.subplot.hspace'] = self.subplot_vspace
        fig = plt.figure(self.fig_num, self.fig_size, dpi=self.fig_dpi)
        
        for p_dict in self.plot_z_list:
            ax = fig.add_subplot(3, 2, p_dict['plot_num'], aspect='equal')
            
            ii = p_dict['index'][0]
            jj = p_dict['index'][0]
            
            for r_arr in self.residual.data_array:
                # calulate the rms self.residual/error
                if p_dict['plot_num'] < 5:
                    rms = r_arr['z'][self.period_index, ii, jj].__abs__()/\
                                (r_arr['z_err'][self.period_index, ii, jj].real)
                    
                else: 
                    rms = r_arr['tip'][self.period_index, ii, jj].__abs__()/\
                                (r_arr['tip_err'][self.period_index, ii, jj].real)
        
                #color appropriately
                if np.nan_to_num(rms) == 0.0:
                    marker_color = (1, 1, 1)
                    marker = '.'
                    marker_size = .001
                    marker_edge_color = (1, 1, 1)
                if rms > self.rms_max:
                    marker_color = (0, 0, 0)
                    marker = 's'
                    marker_size = 10
                    marker_edge_color = (0, 0, 0)
                    
                elif rms >= 1 and rms <= self.rms_max:
                    r_color = 1-rms/self.rms_max+rms_1
                    marker_color = (r_color, r_color, r_color)
                    marker = 's'
                    marker_size = 10
                    marker_edge_color = (0, 0, 0)
                    
                elif rms < 1:
                    r_color = 1-rms/self.rms_max
                    marker_color = (1, r_color, r_color)
                    marker = 's'
                    marker_size = 10
                    marker_edge_color = (0, 0, 0)
                    
                ax.plot(r_arr['lon'], r_arr['lat'], 
                        marker=marker,
                        ms=marker_size,
                        mec=marker_edge_color,
                        mfc=marker_color,
                        zorder=3)
            
            if p_dict['plot_num'] == 1 or p_dict['plot_num'] == 3:
                ax.set_ylabel('Latitude (deg)', fontdict=font_dict)
                plt.setp(ax.get_xticklabels(), visible=False)
                
            elif p_dict['plot_num'] == 2 or p_dict['plot_num'] == 4:
                plt.setp(ax.get_xticklabels(), visible=False)
                plt.setp(ax.get_yticklabels(), visible=False)
                
            elif p_dict['plot_num'] == 6:
                plt.setp(ax.get_yticklabels(), visible=False)
                ax.set_xlabel('Longitude (deg)', fontdict=font_dict)
                
            else:
                ax.set_xlabel('Longitude (deg)', fontdict=font_dict)
                ax.set_ylabel('Latitude (deg)', fontdict=font_dict)
                
            ax.text(self.residual.data_array['lon'].min()+.005-self.pad_x, 
                    self.residual.data_array['lat'].max()-.005+self.pad_y,
                    p_dict['label'],
                    verticalalignment='top',
                    horizontalalignment='left',
                    bbox={'facecolor':'white'},
                    zorder=3)
                    
            ax.tick_params(direction='out')
            ax.grid(zorder=0, color=(.75, .75, .75))
            
            #[line.set_zorder(3) for line in ax.lines]
            
            ax.set_xlim(self.residual.data_array['lon'].min()-self.pad_x, 
                        self.residual.data_array['lon'].max()+self.pad_x)
                        
            ax.set_ylim(self.residual.data_array['lat'].min()-self.pad_y, 
                        self.residual.data_array['lat'].max()+self.pad_y)
            
            ax.xaxis.set_major_locator(MultipleLocator(tick_locator))
            ax.yaxis.set_major_locator(MultipleLocator(tick_locator))
            ax.xaxis.set_major_formatter(FormatStrFormatter('%2.2f'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%2.2f'))
            
        
        
        #cb_ax = mcb.make_axes(ax, orientation='vertical', fraction=.1)
        cb_ax = fig.add_axes([.925, .225, .02, .45])
        color_bar = mcb.ColorbarBase(cb_ax, 
                                     cmap=self.rms_cmap, 
                                     norm=colors.Normalize(vmin=self.rms_min, 
                                                           vmax=self.rms_max),
                                     orientation='vertical')
        
        color_bar.set_label('RMS', fontdict=font_dict)
        
        fig.suptitle('period = {0:.5g} (s)'.format(self.residual.period_list[self.period_index]), 
                     fontdict={'size':12, 'weight':'bold'})
        plt.show()
        
    def redraw_plot(self):
        plt.close('all')
        self.plot()

    def save_figure(self, save_path=None, save_fn_basename=None, 
                    save_fig_dpi=None, fig_format='png', fig_close=True):
        """
        save figure in the desired format
        """
        if save_path is not None:
            self.save_path = save_path
        
        if save_fn_basename is not None:
            pass
        else:
            save_fn_basename = '{0:02}_RMS_{1:.5g}_s.{2}'.format(self.period_index,
                                self.residual.period_list[self.period_index],
                                fig_format)
        save_fn = os.path.join(self.save_path, save_fn_basename) 
        
        if save_fig_dpi is not None:
            self.fig_dpi = save_fig_dpi
        
        self.fig.savefig(save_fn,  dpi=self.fig_dpi)
        print 'saved file to {0}'.format(save_fn)
                    
        if fig_close == True:
            plt.close('all')
            
    def plot_loop(self, fig_format='png'):
        """
        loop over all periods and save figures accordingly
        """
        
        for f_index in range(self.residual.period_list.shape[0]):
            self.period_index = f_index
            self.plot()
            self.save_figure(fig_format=fig_format)
            

rms_plot = Plot_RMS_Maps(r"c:\MinGW32-xy\Peacock\ModEM\WS_StartingModel_03_tipper\cov3_mb_tipper_NLCG_028.res")
rms_plot.fig_num = 2
rms_plot.read_residual_fn()
rms_plot.residual.data_array['z_err'] *= .5
rms_plot.plot_loop(fig_format='pdf')
