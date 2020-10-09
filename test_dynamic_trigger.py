# -*- coding: utf-8 -*-
"""

Created on Wed Sep 30 13:06:50 2020

:author: Jared Peacock

:license: MIT

"""

from mth5 import metadata

class ChangeTrigger(object):
    def __getattr__(self, name):
        obj = getattr(self.instance, name)

        # KEY idea for catching contained class attributes changes:
        # recursively create ChangeTrigger derived class and wrap
        # object in it if getting attribute is class instance/object

        if hasattr(obj, '__dict__'):
            return self.__class__(obj)
        else:
            return obj 

    def __setattr__(self, name, value):
        if getattr(self.instance, name) != value:
            self._on_change(name, value)
        setattr(self.instance, name, value)

    def __init__(self, obj):
        object.__setattr__(self, 'instance', obj)

    def _on_change(self, name, value):
        raise NotImplementedError('Subclasses must implement this method')
        
        
# def update_dict(old_dict, new_dict):
#     return old_dict.update(new_dict)

# class Trigger(ChangeTrigger):
#     def _on_change(self, name, value):
    
# # class AttrTrigger(ChangeTrigger):
# #     def _on_change(self, name, value):
        
        
        
 
# class TS():
#     # manager = Manager()
#     def __init__(self):
#         self.m = Trigger(metadata.Survey())
#         self.x = {}
        

s = Trigger(TS())
s.m.comments = 'test'

# survey = Trigger(metadata.Survey())
# m = metadata.Survey()
# xattr = m.to_dict()['survey']
# survey.country = "test"

