from aria import LogManager, EventProperties, PiiKind, LogConfiguration, LogManagerConfiguration
import random
import time
import threading
from datetime import datetime

def get_current_time_epoch_ms():
    return int(time.time()) * 1000

# Helper methods
def getRandomHexNumberAsString(length):
    
    outputString = ""

    letters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', '❤','☀']

    rand = random.Random()

    for i in range(length):
        outputString = outputString + letters[rand.randint(0, 15)]

    return outputString

def getRandomIPV4Address():
    rand = random.Random()
    return str(rand.randint(1,255)) + "." + \
           str(rand.randint(1,255)) + "." + \
           str(rand.randint(1,255)) + "." + \
           str(rand.randint(1,255))

def getRandomIPV6Address():
    # 2001:4898:e0:b4:888b:4d93:a1f3:749b
    return  getRandomHexNumberAsString(4) + ":" + \
            getRandomHexNumberAsString(4) + ":" + \
            getRandomHexNumberAsString(2) + ":" + \
            getRandomHexNumberAsString(2) + ":" + \
            getRandomHexNumberAsString(4) + ":" + \
            getRandomHexNumberAsString(4) + ":" + \
            getRandomHexNumberAsString(4) + ":" + \
            getRandomHexNumberAsString(4)

def convert_ms_to_isoformat(time_in_ms):
        date_time = datetime.fromtimestamp(time_in_ms / 1000.0)
        return str(date_time.isoformat())

def init_sample():
    import logging
    log_manager = LogManager;
    
    # Here you can specify the log_config
    log_config = LogConfiguration(log_level=logging.DEBUG)
    
    # Here you can specify the configuration for LogManager 
    configuration = LogManagerConfiguration(tcp_connections=4 ,max_events_in_memory=30000, log_configuration = log_config, drop_event_if_max_is_reached = False)
    
    log_manager.initialize(SampleVariables.tenant_token, configuration)
    logger = log_manager.get_logger("", SampleVariables.tenant_token)
    return logger, log_manager
    
def run_simple_test(logger):
    
    max_val = 0

    # Create a event that has 2 KB formed form random values
    event_properties = EventProperties('stratus_orders')
    event_properties.set_property("Prop_AppVersion", "1.1.1.007")
    event_properties.set_property("Prop_UserId", getRandomHexNumberAsString(64))
    current_time_ms = get_current_time_epoch_ms()
    prev_login_in_ms = current_time_ms - random.Random().randint(1, 100) * 24 * 60 * 60 * 1000
    event_properties.set_property("Prop_PrevLogin", convert_ms_to_isoformat(prev_login_in_ms))
    event_properties.set_property("Prop_IP4Address", getRandomIPV4Address(), PiiKind.PiiKind_IPv4Address)
    event_properties.set_property("Prop_IP6Address", getRandomIPV6Address(), PiiKind.PiiKind_IPv6Address)
    event_properties.set_property("Prop_Subject", "Hello Aria", PiiKind.PiiKind_MailSubject)
    event_properties.set_property("Prop_SearchQuery", "Longest river", PiiKind.PiiKind_QueryString)
    event_properties.set_property("Prop_SessionId", getRandomHexNumberAsString(8), PiiKind.PiiKind_None)
    event_properties.set_property("Prop_SessionId1", getRandomHexNumberAsString(8), PiiKind.PiiKind_Fqdn)
    event_properties.set_property("Prop_SessionId2", getRandomHexNumberAsString(8), PiiKind.PiiKind_GenericData)
    event_properties.set_property("Prop_SessionId4", getRandomHexNumberAsString(8), PiiKind.PiiKind_DistinguishedName)
    event_properties.set_property("Prop_SessionId5", getRandomHexNumberAsString(8), PiiKind.PiiKind_Identity)
    event_properties.set_property("Prop_SessionId6", getRandomHexNumberAsString(8), PiiKind.PiiKind_IPv4Address)
    event_properties.set_property("Prop_SessionId9", getRandomHexNumberAsString(8), PiiKind.PiiKind_IPv6Address)
    event_properties.set_property("Prop_SessionId0", getRandomHexNumberAsString(8), PiiKind.PiiKind_MailSubject)
    event_properties.set_property("Prop_SessionId10_", getRandomHexNumberAsString(8), PiiKind.PiiKind_PhoneNumber)
    event_properties.set_property("Prop_SessionId12", getRandomHexNumberAsString(8), PiiKind.PiiKind_QueryString)
    event_properties.set_property("Prop_SessionId13", getRandomHexNumberAsString(8), PiiKind.PiiKind_SipAddress)
    event_properties.set_property("Prop_SessionId14pstn", getRandomHexNumberAsString(8), PiiKind.PiiKind_SmtpAddress)
    
    for i in range(50):
        event_properties.set_property("key" + str(i), getRandomHexNumberAsString(8), PiiKind.PiiKind_Uri)

    # Adding unicode 
    event_properties.set_property('unicode_value', u"❤ ☀ ☆ ☂ ☻ ♞ ☯ ☭ ")
    event_properties.set_property('pstn_unicode_value', u"❤ ☀ ☆ ☂ ☻ ♞ ☯ ☭ ")
    event_properties.set_property('unicodpstne_value', u"❤ ☀ ☆ ☂ ☻ ♞ ☯ ☭ ")        
    # Send all the events one after the other
    for i in range(SampleVariables.EVENTS_TO_SEND):
        event_id = logger.log_event(event_properties)
        
        # Do this if you think you will send more events than the SDK can handle and don't want to lose any events
        while event_id < 0:
            time.sleep(0.00001)
            event_id = logger.log_event(event_properties)
        
        AriaResults.events_send.append(event_id)
        max_val = max(log_manager.records_in_memory(), max_val)
    print ("Maximum events held in the system at a certain point is:" + str(max_val))

# This is used to show the callback capabilities
def update(tenant, sequence_list, result):
    if result not in AriaResults.result_map:
        AriaResults.result_map[result] = 0
        
    AriaResults.result_map[result] += len(sequence_list)
    AriaResults.events_received_callback += len(sequence_list)

    for i in sequence_list:
        if i in AriaResults.events_send:
            AriaResults.events_send.remove(i)
        else:
            print("This is " + str(i) + " and it was not expected, tenant=" + str(tenant) + " result=" + str(result))
            AriaResults.events_send.remove(i)

class SampleVariables(object):
    EVENTS_TO_SEND = 50000      # Number of events to be send
    EVENT_SIZE = 2048           # This is the size measured at bond serialization time
    tenant_token = "a132b83d43f94f6da418c8aae54585fd-856ad6a4-66c1-4b4a-8ca0-2c514a34e459-7426"

class AriaResults(object):
    events_send = []
    events_received_callback = 0
    result_map = {}
            
def print_information():
    print("Test information:\nDo not use this tenant_token except for testing the sample, this is ARIA's tenant, do not abuse it!")
    print("Test setup:")
    print("Tenant token=" + str(SampleVariables.tenant_token))
    print("Events to be send=" + str(SampleVariables.EVENTS_TO_SEND))
    print("Event size=" + str(SampleVariables.EVENT_SIZE/1024) + "KB")
    print("____________GO SEND EVENTS_____________")

def print_after_math(time):
    print("_________")
    print("|Summary|")
    print("After flush this many events are in the system. All of them are dropped = " + str(log_manager.records_in_memory()))    
    print("Callback results:")
    print("Events received back through callback = " + str(AriaResults.events_received_callback))
    for i in AriaResults.result_map:
        print("Result = " + str(i) + " Number of events = " + str(AriaResults.result_map[i]))
    print("SDK stats:")
    print("Total time = " + str(time))
    print("Events/s = " + str(SampleVariables.EVENTS_TO_SEND / time))
    print("MB/s = " + str(SampleVariables.EVENTS_TO_SEND / time * SampleVariables.EVENT_SIZE / (1024 * 1024)))

if __name__ == "__main__":
    print_information()
    
    start = time.clock()
    logger, log_manager = init_sample()
    end = time.clock()
    
    print("Initialization time took:" + str((end-start)) + "s")
    
    start = time.clock()
    log_manager.add_subscriber(update)
    run_simple_test(logger)
    log_manager.flush(timeout=60)             # This should be called at the end of the program. Do not use the log_manager or logger after.
    end = time.clock()
    
    #time.sleep(1)
    print_after_math((end-start))