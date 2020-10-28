#
"""
===================
Filters for MT Data
===================

    Includes:
    ---------
        * *adaptive_notch_filter* to remove power line noise
        * *remove_periodic_noise* to remove pipeline noise
        

:author: J. Peacock
:date:  2010, 2013
    
"""
import numpy as np
import scipy.signal as sps
import os


def adaptive_notch_filter(
    bx, df=100, notches=[50, 100], notchradius=0.5, freqrad=0.9, rp=0.1
):
    """
    adaptive_notch_filter(bx, df, notches=[50,100], notchradius=.3, freqrad=.9)
    will apply a notch filter to the array bx by finding the nearest peak 
    around the supplied notch locations.  The filter is a zero-phase 
    Chebyshev type 1 bandstop filter with minimal ripples.
    
    Arguments:
    -----------
        **bx** : np.ndarray(len_time_series)
                 time series to filter
                 
        **df** : float
                 sampling frequency in Hz
                 
        **notches** : list of frequencies (Hz) to filter
                      
        **notchradius** : float
                          radius of the notch in frequency domain (Hz)
        
        **freqrad** : float
                      radius to searching for peak about notch from notches
                      
        **rp** : float
                 ripple of Chebyshev type 1 filter, lower numbers means less
                 ripples

    Outputs:
    ---------
        
        **bx** : np.ndarray(len_time_series) 
                 filtered array 
                 
        **filtlst** : list
                      location of notches and power difference between peak of
                      notch and average power.
                      
    ..Example: ::
        
        >>> import RemovePeriodicNoise_Kate as rmp
        >>> # make a variable for the file to load in
        >>> fn = r"/home/MT/mt01_20130101_000000.BX"
        >>> # load in file, if the time series is not an ascii file
        >>> # might need to add keywords to np.loadtxt or use another 
        >>> # method to read in the file
        >>> bx = np.loadtxt(fn)
        >>> # create a list of frequencies to filter out
        >>> freq_notches = [50, 150, 200]
        >>> # filter data
        >>> bx_filt, filt_lst = rmp.adaptiveNotchFilter(bx, df=100. 
        >>> ...                                         notches=freq_notches)
        >>> #save the filtered data into a file
        >>> np.savetxt(r"/home/MT/Filtered/mt01_20130101_000000.BX", bx_filt)
    
    Notes:
    -------
        Most of the time the default parameters work well, the only thing
        you need to change is the notches and perhaps the radius.  I would
        test it out with a few time series to find the optimum parameters.
        Then make a loop over all you time series data. Something like
        
        >>> import os
        >>> dirpath = r"/home/MT"
        >>> #make a director to save filtered time series
        >>> save_path = r"/home/MT/Filtered"
        >>> if not os.path.exists(save_path):
        >>>     os.mkdir(save_path)
        >>> for fn in os.listdir(dirpath):
        >>>     bx = np.loadtxt(os.path.join(dirpath, fn)
        >>>     bx_filt, filt_lst = rmp.adaptiveNotchFilter(bx, df=100. 
        >>>     ...                                         notches=freq_notches)
        >>>     np.savetxt(os.path.join(save_path, fn), bx_filt)
         
    """

    bx = np.array(bx)

    if type(notches) != list:
        notches = [notches]

    df = float(df)  # make sure df is a float
    dt = 1.0 / df  # sampling rate
    n = len(bx)  # length of array
    dfn = df / n  # frequency step
    dfnn = freqrad / dfn  # radius of frequency search
    fn = notchradius  # filter radius

    # transform data into frequency domain to find notches
    BX = np.fft.fft(bx)
    freq = np.fft.fftfreq(n, dt)

    filtlst = []
    for notch in notches:
        fspot = int(round(notch / dfn))
        nspot = np.where(abs(BX) == max(abs(BX[fspot - dfnn : fspot + dfnn])))[0][0]
        dbstop = np.log10(abs(BX[nspot]) - abs(BX).mean())
        if np.nan_to_num(dbstop) == 0.0 or dbstop < 3:
            filtlst.append("No need to filter \n")
            pass
        else:
            filtlst.append([freq[nspot], dbstop])
            ws = 2 * np.array([freq[nspot] - fn, freq[nspot] + fn]) / df
            wp = 2 * np.array([freq[nspot] - 2 * fn, freq[nspot] + 2 * fn]) / df
            ford, wn = sps.cheb1ord(wp, ws, 1, dbstop)
            b, a = sps.cheby1(1, 0.5, wn, btype="bandstop")
            bx = sps.filtfilt(b, a, bx)

    return bx, filtlst


def remove_periodic_noise(filename, dt, noiseperiods, save="n"):
    """
    removePeriodicNoise will take a window of length noise period and 
    compute the median of signal for as many windows that can fit within the 
    data.  This median window is convolved with a series of delta functions at
    each window location to create a noise time series. This is then 
    subtracted from the data to get a 'noise free' time series.
    
    Arguments:
    ----------
        **filename** : string (full path to file) or array
                      name of file to have periodic noise removed from
                      can be an array
                      
        **dt** : float
                 time sample rate (s)
                 
        **noiseperiods** : list
                           a list of estimated periods with a range of values
                           to look around [[noiseperiod1,df1]...] where df1 is
                           a fraction value find the peak about noiseperiod1 
                           must be less than 1. (0 is a good start, but
                           if you're periodic noise drifts, might need to
                           adjust df1 to .2 or something)
        **save** : [ 'y' | 'n' ]
                    * 'y' to save file to:
                        os.path.join(os.path.dirname(filename), 'Filtered', fn)
                    * 'n' to return the filtered time series
    
    Outputs:
    --------
    
        **bxnf** : np.ndarray
                   filtered time series
                   
        **pn** : np.ndarray
                periodic noise time series
                
        **fitlst** : list
                     list of peaks found in time series
                     
    ..Example: ::
        
        >>> import RemovePeriodicNoise_Kate as rmp
        >>> # make a variable for the file to load in
        >>> fn = r"/home/MT/mt01_20130101_000000.BX"
        >>> # filter data assuming a 12 second period in noise and save data
        >>> rmp.remove_periodic_noise(fn, 100., [[12,0]], save='y')
    
    Notes:
    -------
        Test out the periodic noise period at first to see if it drifts.  Then
        loop over files
        
        >>> import os
        >>> dirpath = r"/home/MT"
        >>> for fn in os.listdir(dirpath):
        >>>     rmp.remove_periodic_noise(fn, 100., [[12,0]], save='y') 
        
    """

    if type(noiseperiods) != list:
        noiseperiods = [noiseperiods]

    dt = float(dt)
    # sampling frequency
    df = 1.0 / dt

    filtlst = []
    pnlst = []
    for kk, nperiod in enumerate(noiseperiods):
        # if the nperiod is the first one load file or make an array of the input
        if kk == 0:
            # load file
            if type(filename) is str:
                bx = np.loadtxt(filename)
                m = len(bx)
            else:
                bx = np.array(filename)
                m = len(bx)
        # else copy the already filtered array
        else:
            bx = bxnf.copy()
            m = len(bx)

        # get length of array
        T = len(bx)

        # frequency step
        dfn = df / T
        # make a frequency array that describes BX
        pfreq = np.fft.fftfreq(int(T), dt)

        # get noise period in points along frequency axis
        nperiodnn = round((1.0 / nperiod[0]) / dfn)

        # get region to look around to find exact peak
        try:
            dfnn = nperiodnn * nperiod[1]
        except IndexError:
            dfnn = 0.2 * nperiodnn

        # comput FFT of input to find peak value
        BX = np.fft.fft(bx)
        # if dfnn is not 0 then look for max with in region nperiod+-dfnn
        if dfnn != 0:
            nspot = np.where(
                abs(BX) == max(abs(BX[nperiodnn - dfnn : nperiodnn + dfnn]))
            )[0][0]
        else:
            nspot = nperiodnn
        # output the peak frequency found
        filtlst.append("Found peak at : " + str(pfreq[nspot]) + " Hz \n")

        # make nperiod the peak period in data points
        nperiod = (1.0 / pfreq[nspot]) / dt

        # create list of time instances for windowing
        # nlst=np.arange(start=nperiod,stop=T-nperiod,step=nperiod,dtype='int')
        nlst = np.arange(start=0, stop=m, step=nperiod, dtype="int")

        # convolve a series of delta functions with average of periodic window
        dlst = np.zeros(T)  # delta function list
        dlst[0] = 1
        winlst = np.zeros((len(nlst), int(nperiod)))
        for nn, ii in enumerate(nlst):
            if T - ii < nperiod:
                dlst[ii] = 1
            else:
                winlst[nn] = bx[ii : ii + int(nperiod)]
                dlst[ii] = 1

        # compute median window to remove any influence of outliers
        medwin = np.median(winlst, axis=0)

        # make a time series by convolving
        pn = np.convolve(medwin, dlst)[0:T]

        # remove noise from data
        bxnf = bx - pn

        pnlst.append(pn)
    if len(pnlst) > 1:
        pn = np.sum(pnlst, axis=0)
    else:
        pn = np.array(pn)
    if save == "y":
        savepath = os.path.join(os.path.dirname(filename), "Filtered")
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        # savepathCN=os.path.join(savepath,'CN')
        np.savetxt(os.path.join(savepath, filename), bxnf, fmt="%.7g")
        print "Saved filtered file to {0}".format(os.path.join(savepath, filename))
    else:
        return bxnf, pn, filtlst
