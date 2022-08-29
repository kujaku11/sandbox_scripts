#!/usr/bin/env python
# coding: utf-8

# # Read Phoenix data into MTH5
#
# This example demonstrates how to read Phoenix data into an MTH5 file.  The data comes from example data in [PhoenixGeoPy](https://github.com/torresolmx/PhoenixGeoPy). Here I downloaded those data into a local folder on my computer by forking the main branch.

# ## Imports

# In[1]:


from pathlib import Path

from mth5.mth5 import MTH5
from mth5 import read_file
from mth5.io.phoenix.readers.phx_json import ReceiverMetadataJSON


# ## Data Directory
#
# Specify the station directory.  Phoenix files place each channel in a folder under the station directory named by the channel number.  There is also a `recmeta.json` file that has metadata output by the receiver that can be useful.  In the `PhoenixGeopPy/sample_data` there are 2 folders one for native data, these are `.bin` files which are the raw data in counts sampled at 24k.  There is also a folder for segmented files, these files are calibrated to millivolts and decimate or segment the data according to the recording configuration.  Most of the time you would use the segmented files?

# In[2]:


station_dir = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\mt\phoenix_example_data\10291_2019-09-06-015630"
)


# ## Receiver Metadata
#
# The data logger or receiver will output a `JSON` file that contains useful metadata that is missing from the data files.  The `recmeta.json` file can be read into an object with methods to translate to `mt_metadata` objects.

# In[3]:


receiver_metadata = ReceiverMetadataJSON(station_dir.joinpath(r"recmeta.json"))


# ## Initiate MTH5
#
# First initiate an MTH5 file, can use the receiver metadata to fill in some `Survey` metadata

# In[4]:


m = MTH5()
m.open_mth5(station_dir.joinpath("mth5_from_phoenix.h5"), "w")


# ### Add Survey

# In[5]:


survey_metadata = receiver_metadata.survey_metadata
survey_group = m.add_survey(survey_metadata.id)


# ### Add Station
#
# Add a station and station metadata

# In[6]:


station_metadata = receiver_metadata.station_metadata
station_group = survey_group.stations_group.add_station(
    station_metadata.id, station_metadata=station_metadata
)


# ## Loop through channels
#
# Here we will loop through each channel which is a folder under the station directory.  Inside the folder are files with extensions of `.td_24k` and `td_150`.
#
# - `.td_24k` are usually bursts of a few seconds of data sampled at 24k samples per second to get high frequency information.  When these files are read in the returned object is a list of `mth5.timeseries.ChannelTS` objects that represent each burst.
# - `td_150` is data continuously sampled at 150 samples per second.  These files usually have a set length, commonly an hour. The returned object is a `mth5.timeseries.ChannelTS`.

# ### Read Continuous data
#
# We only need to open the first `.td_150` file as it will automatically read the sequence of files.  We need to do this because the header of the `.td_150` file only contains the master header which has the start time of when the recording started and not the start time of the file, that's in the file name, which is not stable.

# #### Add a Run for continuous data
#
# Here we will add a run for the continuous data labelled `sr150_001`.  This is just a suggestion, you could name it whatever makes sense to you.

# In[7]:


run_metadata = receiver_metadata.run_metadata
run_metadata.id = "sr150_001"
run_metadata.sample_rate = 150.0
continuous_run = station_group.add_run(
    run_metadata.id, run_metadata=run_metadata
)


# In[8]:


for ch_dir in station_dir.iterdir():
    if ch_dir.is_dir():
        ch_metadata = receiver_metadata.get_ch_metadata(int(ch_dir.stem))
        # need to set sample rate to 0 so it does not override existing value
        ch_metadata.sample_rate = 0
        ch_150 = read_file(
            sorted(list(ch_dir.glob("*.td_150")))[0],
            **{"channel_map": receiver_metadata.channel_map}
        )
        ch_150.channel_metadata.update(ch_metadata)
        ch_dataset = continuous_run.from_channel_ts(ch_150)
        continuous_run.validate_run_metadata()
        continuous_run.write_metadata()


# ### Read Segmented data
#
# Segmented data are busts of high frequency sampling, typically a few seconds every few minutes.  This will create a log of runs, so we will label the runs sequentially `sr24k_001`.  Now you may need to add digits onto the end depending on how long your sampling was.
#
# **Note**: this is currently not optimized, so may run slowly.
#

# In[9]:


# get_ipython().run_cell_magic(
#     "time",
#     "",
#     'for ch_dir in station_dir.iterdir():\n    if ch_dir.is_dir():\n        ch_metadata = receiver_metadata.get_ch_metadata(int(ch_dir.stem))\n        # need to set sample rate to 0 so it does not override existing value\n        ch_metadata.sample_rate = 0\n        ch_segments = read_file(\n            sorted(list(ch_dir.glob("*.td_24k")))[0],\n            **{"channel_map":receiver_metadata.channel_map}\n        )\n        for ii, seg_ts in enumerate(ch_segments):\n            # update run metadata\n    \n            run_id = f"sr24k_{ii:03}"\n            if not run_id in station_group.groups_list:\n                run_metadata.id = run_id\n                run_metadata.sample_rate = 24000\n                run_group = station_group.add_run(run_id, run_metadata=run_metadata)\n            else:\n                run_group = station_group.get_run(run_id)\n            \n            # update channel metadata\n            seg_ts.channel_metadata.update(ch_metadata)\n            \n            # add channel\n            run_group.from_channel_ts(seg_ts)\n            \n            # update run metadata\n            run_group.validate_run_metadata()\n            run_group.write_metadata()\n',
# )


# # #### Update metadata before closing
# #
# # Need to update the metadata to account for added stations, runs, and channels.

# # In[10]:


# station_group.validate_station_metadata()
# station_group.write_metadata()

# survey_group.update_survey_metadata()
# survey_group.write_metadata()


# In[11]:


# m.close_mth5()
