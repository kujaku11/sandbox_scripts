# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 14:50:31 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================
from mt_metadata.base.helpers import write_lines
from mt_metadata.base import get_schema, Base
from mt_metadata.timeseries.standards import SCHEMA_FN_PATHS
from mt_metadata.timeseries import Diagnostic

# =============================================================================
attr_dict = get_schema("battery", SCHEMA_FN_PATHS)
attr_dict.add_dict(get_schema("diagnostic", SCHEMA_FN_PATHS), "voltage")
test_attr_dict = get_schema("person", SCHEMA_FN_PATHS)
# =============================================================================
class Battery(Base):
    __doc__ = write_lines(attr_dict)

    def __init__(self, **kwargs):

        self.type = None
        self.id = None
        self.voltage = Diagnostic()
        self.comments = None
        self.test = None
        super().__init__(**kwargs)


class DL(Battery):
    __doc__ = write_lines(attr_dict)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self._attr_dict.update(test_attr_dict)


class Old:
    def __init__(self, a={}, **kwargs):
        self._a = a

        for k, v in kwargs.items():
            setattr(k, v)


class New(Old):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._a.update({"b": 10})


# =============================================================================
# Tests
# =============================================================================
b = Base()
print(b.get_attribute_list())
c = Battery()
print(b.get_attribute_list())
d = DL()
print(b.get_attribute_list())
