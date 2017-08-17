from aria.log_manager import LogManager
from aria.log_config import LogConfiguration
from aria.event_properties import EventProperties
from aria import configuration
from datetime import datetime
import time
import sys
import subprocess
import importlib
from . import data_modules
from .data_modules import *

#compatible with both py2.7 and py3
class EventSender(object):

    @staticmethod
    def get_modules(dest, dest_module):
        import os
        classarr = []
        modules_to_import = os.listdir(dest)
        for modulestr in modules_to_import:
            if (modulestr[-3:] == '.py') and (modulestr != '__init__.py'):
                module = importlib.import_module('.' + modulestr[:-3], dest_module)
                #class name should be same as module name
                classobj = getattr(module, modulestr[:-3])
                classarr.append(classobj)
            #pretty messy
            elif (modulestr.count('.') == 0) and (modulestr != 'DO_NOT_WRITE'):
                newdest = dest + '/' + modulestr
                newdest_module = dest_module + '.' + modulestr
                for classobj in EventSender.get_modules(newdest, newdest_module):
                    classarr.append(classobj)
        return classarr

    def send(self, tenant_token):
        logConfig = LogConfiguration()
        config1 = configuration.LogManagerConfiguration(log_configuration = logConfig)
        LogManager.initialize(tenant_token, config1)
        logger = LogManager.get_logger("", tenant_token)
        
        # modules should have a class with the same name
        # the class should have at least two functions: name(), returning the event name 
        # and collect_data(), returning collected data as a value

        #refresh
        #importlib.invalidate_caches()

        classarr = EventSender.get_modules('./monitor/data_modules', 'monitor.data_modules')
        
        # should add implementation for directories later

        import logging
        #should change range and time interval later
        while True:
            # find a way to change this
            event_properties = EventProperties("monitoraria")
            
            for classobj in classarr:
                data = classobj.collect_data()
                print(data)
                # subprocess.call(["echo", data])
                event_properties.set_property(classobj.name(), data)
            id = logger.log_event(event_properties)
            # wait time before checking again
            time.sleep(10)
        

        #should put this in another thread
        LogManager().flush_and_tear_down()
        return
        

