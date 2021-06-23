# -*- coding: utf-8 -*-
"""
Created on Fri May 14 15:03:24 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from mt_metadata.timeseries.stationxml import XMLInventoryMTExperiment

# Read inventory foerm IRIS Client
client = Client(base_url="IRIS", force_redirect=True)
starttime = UTCDateTime("2004-03-14T14:20:00")
endtime = UTCDateTime("2004-08-26T00:00:00")
inventory = client.get_stations(network="BK", 
                                station="PKD",
                                channel="LQ1,LQ2,LF1,LF2,LF3",
                                starttime=starttime,
                                endtime=endtime,
                                level="response")

inventory.write(r"c:\users\jpeacock\pkd.xml", "stationxml")

translator = XMLInventoryMTExperiment()
mt_experiment = translator.xml_to_mt(inventory_object=inventory)
mt_experiment.to_xml(fn=r"c:\users\jpeacock\pkd_mt_experiment.xml")


