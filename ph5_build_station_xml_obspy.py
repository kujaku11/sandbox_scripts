# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 14:43:36 2019

@author: jpeacock
"""

import obspy
from obspy.core.inventory import Inventory, Network, Station, Channel, Site
from obspy.core.inventory.util import Equipment, Comment
from obspy.core.util import AttribDict
import pandas as pd

survey_csv = r"c:\Users\jpeacock\Documents\imush\Archive\survey_summary.csv"
survey_df = pd.read_csv(survey_csv)


# We'll first create all the various objects. These strongly follow the
# hierarchy of StationXML files.
inv = Inventory(networks=[],
                source="MT Test")

net = Network(code="MT",
              # A list of stations. We'll add one later.
              stations=[],
              description="Test stations.",
              # Start-and end dates are optional.
              start_date=obspy.UTCDateTime(2016, 1, 2))
inv.networks.append(net)

for row, station_df in survey_df.iterrows(): 
    sta = Station(code=station_df['siteID'],
                  latitude=station_df['lat'],
                  longitude=station_df['lon'],
                  elevation=station_df['nm_elev'],
                  creation_date=obspy.UTCDateTime(2016, 1, 2),
                  site=Site(name=station_df['siteID']))
    
    for comp in ['ex', 'ey', 'hx', 'hy', 'hz']:
        if station_df['{0}_azm'.format(comp)] is not None:
            if 'h' in comp:
                cha = Channel(code=comp.upper(),
                              location_code="",
                              latitude=station_df['lat'],
                              longitude=station_df['lon'],
                              elevation=station_df['nm_elev'],
                              depth=0,
                              azimuth=station_df['{0}_azm'.format(comp)],
                              dip=0,
                              sample_rate=station_df['sampling_rate'])
                cha.channel_number = station_df['{0}_num'.format(comp)]
                cha.sensor = Equipment(serial_number=station_df['{0}_id'.format(comp)])
            elif 'e' in comp:
                cha = Channel(code=comp.upper(),
                              location_code="",
                              latitude=station_df['lat'],
                              longitude=station_df['lon'],
                              elevation=station_df['nm_elev'],
                              depth=0,
                              azimuth=station_df['{0}_azm'.format(comp)],
                              dip=0,
                              sample_rate=station_df['sampling_rate'])
#                cha.comments = Comment(['Dipole Length (m) = {0:.1f}'.format(station_df['{0}_len'.format(comp)])])

            sta.channels.append(cha)
    # Now tie it all together.
    #cha.response = response
    
    net.stations.append(sta)

# And finally write it to a StationXML file. We also force a validation against
# the StationXML schema to ensure it produces a valid StationXML file.
#
# Note that it is also possible to serialize to any of the other inventory
# output formats ObsPy supports.
inv.write("station.xml", format="STATIONXML", validate=True)