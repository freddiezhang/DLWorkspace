from __future__ import absolute_import
from __future__ import print_function
import random
import time
from aria import LogManager, EventProperties, PiiKind, LogConfiguration, LogManagerConfiguration
import logging

def init_sample():
    '''
        This will initialize LogManager and return both a logger and the log manager
    '''
    
    # Here you can specify the log_config
    log_config = LogConfiguration(log_level=logging.DEBUG)
    
    # Create the configuraiton for LogManager. There is a default one but you can specify multiple things. 
    configuration = LogManagerConfiguration(tcp_connections=2 ,max_events_in_memory=15000, log_configuration = log_config, drop_event_if_max_is_reached = False)#, process_number=2, batching_threads_count=1)
    
    # Initialize logManager with the tocken and the configurations
    LogManager.initialize(SampleVariables.tenant_token, configuration)

    # Return the logger that it will be used for this sample
    logger = LogManager.get_logger("", SampleVariables.tenant_token)
    return logger

def run_simple_test(logger):
    '''
        Creates some events properties and then sends that event multiple times
    '''

    event_properties = EventProperties("eventProperties")
    event_properties.set_property("Prop1", "1")
    event_properties.set_property("Prop_SearchQuery", "Longest river", PiiKind.PiiKind_QueryString)
    
    for i in range(SampleVariables.EVENTS_TO_SEND):
        # Event ID is a number that can be used to map it with the envent send. It is just an indexing number, not a real event ID used anywere else.
        event_id = logger.log_event(event_properties)

        # Do this if you think you will send more events than the SDK can handle and don't want to lose any events
        while event_id < 0:
            time.sleep(0.00001)
            event_id = logger.log_event(event_properties)
        
        AriaResults.events_send.append(event_id)

def update(tenant, sequence_list, result):
    '''
        tenant is the tenant for witch the events were sent
        sequence_list is a list of events for witch the update was triggered.
        result if it's > 0 then is an http stack code, if not then is a SubscribeStatus
    '''
    resultStr = str(result)

    if result not in AriaResults.result_map:
        AriaResults.result_map[result] = 0
        
    AriaResults.result_map[result] += len(sequence_list)
    AriaResults.events_received_callback += len(sequence_list)

    for i in sequence_list:
        AriaResults.events_send.remove(i)

class SampleVariables(object):
    EVENTS_TO_SEND = 1000    # Number of events to be send
    tenant_token = "a132b83d43f94f6da418c8aae54585fd-856ad6a4-66c1-4b4a-8ca0-2c514a34e459-7426" # Put your tenant here

class AriaResults(object):
    events_send = []
    events_received_callback = 0
    result_map = {}

if __name__ == "__main__":
    localLogger = init_sample()
    LogManager.add_subscriber(update)
    run_simple_test(localLogger)

    #Always call flush at the end of your program to ensure all the events are sent
    LogManager.flush(timeout=0)
    print(AriaResults.result_map)
