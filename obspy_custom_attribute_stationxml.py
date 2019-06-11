# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 19:26:01 2019

@author: jpeacock
"""

from obspy import Inventory
from obspy.core.inventory import Network
from obspy.core.util import AttribDict

ns = 'http://some-page.de/xmlns/1.0'

Channel = AttribDict()
Channel.namespace = ns
Channel.value = AttribDict()

Channel.value.my_nested_tag1 = AttribDict()
Channel.value.my_nested_tag1.namespace = ns
Channel.value.my_nested_tag1.value = 1.23E+10

Channel.value.my_nested_tag2 = AttribDict()
Channel.value.my_nested_tag2.namespace = ns
Channel.value.my_nested_tag2.value = True

inv = Inventory([Network('XX')], 'XX')
inv[0].extra = AttribDict()
inv[0].extra.Channel = Channel
inv.write('my_inventory.xml', format='STATIONXML',
          nsmap={'somepage_ns': 'http://some-page.de/xmlns/1.0'})