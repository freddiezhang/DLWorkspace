from __future__ import absolute_import
import re
from .pii import PiiKind
import sys

class ClientMessageType(object):
    ClientEvent = 1 
    ClientAggregate = 2
    
class EventProperties(object):
    def __init__(self, name):       
        from .utilities import AriaUtilities
        if (re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9_]){2,98}[a-zA-Z0-9]$").match(name)):
            self.name = name
        else:
            raise ValueError("Invalid event name")
        self.time_stamp_in_epoch_ms = AriaUtilities.get_current_time_epoch_ms()        
        self.message_type = ClientMessageType.ClientEvent
        self.__properties = {}
        self.__pii_properties = {}
        
    def set_property(self, key, value, piiKind = PiiKind.PiiKind_None):
        """ Sets the given key, value pair to the property bag """
        if (piiKind == PiiKind.PiiKind_None):
            if sys.version_info[0] < 3:
                self.__properties[key] = str(value) if type(value) != unicode else value
            else:
                self.__properties[key] = str(value) if type(value) != str else value
                try:
                    self.__properties[key] = bytes(self.__properties[key], 'latin1')
                except:
                    self.__properties[key] = self.__properties[key].encode('utf8')
                    self.__properties[key] = ''.join(chr(i) for i in self.__properties[key])
                    self.__properties[key] = bytes(self.__properties[key], 'latin1')
        else:
            if sys.version_info[0] < 3:
                self.__pii_properties[key] = (value, piiKind)
            else:
                newValue = str(value) if type(value) != str else value
                try:
                    newValue = bytes(newValue, 'latin1')
                except:
                    newValue = newValue.encode('utf8')
                    newValue = ''.join(chr(i) for i in newValue)
                    newValue = bytes(newValue, 'latin1')
                self.__pii_properties[key] = (newValue, piiKind)
        
    def get_properties(self):
        return self.__properties
    
    def get_pii_properties(self):
        return self.__pii_properties