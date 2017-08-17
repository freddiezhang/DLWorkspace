from __future__ import absolute_import
from __future__ import print_function
import random
import time
import logging
import unittest
#import xmlrunner
import sys
from distutils import config
from threading import RLock
from aria import LogManager, EventProperties, PiiKind, LogConfiguration, LogManagerConfiguration, utilities
from aria import batcher
from parameterized import parameterized


class SampleVariables(object):
    EVENTS_TO_SEND = 10000     # Number of events to be send
    EVENT_SIZE = 2048           # This is the size measured at bond serialization time
    tenant_token = "a132b83d43f94f6da418c8aae54585fd-856ad6a4-66c1-4b4a-8ca0-2c514a34e459-7426"
    tenant_token2 = "4c824cfb53154a9b8e709962774ae879-e4db1514-2b8d-42e8-9700-9b9b3880278e-7210"

def getRandomHexNumberAsString(length):
    
    outputString = ""
    letters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', u'❤', u'☀']
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

# Creates the logger and returns the logger
def init_sample(configuration, tenant_token = SampleVariables.tenant_token):
    LogManager.initialize(tenant_token, configuration)
    logger = LogManager.get_logger("", tenant_token)
    return logger

# Returns one event created
def get_event(keys):
    # Create a event that has 2 KB formed form random values
    event_properties = EventProperties('stratus_orders')
    event_properties.set_property("Prop_AppVersion", "1.1.1.007")
    event_properties.set_property("Prop_UserId", getRandomHexNumberAsString(64))
    current_time_ms = utilities.AriaUtilities.get_current_time_epoch_ms()
    prev_login_in_ms = current_time_ms - random.Random().randint(1, 100) * 24 * 60 * 60 * 1000
    event_properties.set_property("Prop_PrevLogin", utilities.AriaUtilities.convert_ms_to_isoformat(prev_login_in_ms))
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
    event_properties.set_property("Prop_SessionId14", getRandomHexNumberAsString(8), PiiKind.PiiKind_SmtpAddress)
    
    for i in range(keys):
        event_properties.set_property("key" + str(i), getRandomHexNumberAsString(8), PiiKind.PiiKind_Uri)
    event_properties.set_property('unicode_value', u"❤ ☀ ☆ ☂ ☻ ♞ ☯ ☭ ")
    
    return event_properties

# Send events
def send_events(logger, event_count, event_keys, timer_to_sleep, event_in_between_time_to_sleep, sleep):
    SampleVariables.EVENTS_TO_SEND = event_count
    event_properties = get_event(event_keys)
    
    for i in range(event_count):
        if sleep == True:
            if i % event_in_between_time_to_sleep == 0:
                time.sleep(timer_to_sleep)
        event_id = logger.log_event(event_properties)
        while event_id < 0:
            time.sleep(0.00001)
            event_id = logger.log_event(event_properties)  

        with AriaResults.lockResults:
            AriaResults.events_send.append(event_id)

def send_events_2_logger(logger1, logger2, event_count, event_keys, timer_to_sleep, event_in_between_time_to_sleep, sleep):
    SampleVariables.EVENTS_TO_SEND = event_count
    event_properties = get_event(event_keys)

    for i in range(event_count):
        if sleep == True:
            if i % event_in_between_time_to_sleep == 0:
                time.sleep(timer_to_sleep)
        event_id = logger1.log_event(event_properties)
        event_id2 = logger2.log_event(event_properties)

        if event_id == -1:
            continue

        with AriaResults.lockResults:
            AriaResults.events_send.append(event_id)

        if event_id2 == -1:
            continue

        with AriaResults.lockResults:
            AriaResults.events_send.append(event_id2)

# This is used to show the callback capabilities
def update(tenant, sequence_list, result):
    with AriaResults.lockResults:
        if tenant not in AriaResults.result_map:
            AriaResults.result_map[tenant] = {}
        if result not in AriaResults.result_map[tenant]:
            AriaResults.result_map[tenant][result] = 0

        AriaResults.result_map[tenant][result] += len(sequence_list)
        AriaResults.events_received_callback += len(sequence_list)

        for i in sequence_list:
            if i in AriaResults.events_send:
                AriaResults.events_send.remove(i)
            else:
                print("This is " + str(i) + " and it was not expected, tenant=" + str(tenant) + " result=" + str(result))
                AriaResults.events_send.remove(i)

class AriaResults(object):
    lockResults = RLock()
    events_send = []
    events_received_callback = 0
    result_map = {}

class TestAriaSDKLongHaul(unittest.TestCase):
    def setUp(self):
        print("In method:" + self._testMethodName)
        pass

    def tearDown(self):
        print(AriaResults.result_map)
        print(AriaResults.events_received_callback)
        AriaResults.events_send = []
        AriaResults.events_received_callback = 0
        AriaResults.result_map = {}
        time.sleep(30)

    def test_2_loggers_stress(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        tenant_token2 = SampleVariables.tenant_token2
        logger = init_sample(configuration, tenant_token)
        logger2 = LogManager.get_logger("", tenant_token2)
        LogManager.add_subscriber(update)

        send_events_2_logger(logger1=logger,logger2=logger2, event_count=50000, event_keys=50, timer_to_sleep=0, event_in_between_time_to_sleep=0, sleep=False)

        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == 2 * SampleVariables.EVENTS_TO_SEND)

        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

        if -5 in AriaResults.result_map[tenant_token2]:
            self.assertTrue(AriaResults.result_map[tenant_token2][200] + AriaResults.result_map[tenant_token2][
                -5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token2][200] == SampleVariables.EVENTS_TO_SEND)

    def test_2_loggers_long_haul(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        tenant_token2 = SampleVariables.tenant_token2
        logger = init_sample(configuration, tenant_token)
        logger2 = LogManager.get_logger("", tenant_token2)
        LogManager.add_subscriber(update)

        send_events_2_logger(logger1=logger,logger2=logger2, event_count=50000, event_keys=50, timer_to_sleep=1, event_in_between_time_to_sleep=100, sleep=True)

        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == 2 * SampleVariables.EVENTS_TO_SEND)

        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

        if -5 in AriaResults.result_map[tenant_token2]:
            self.assertTrue(AriaResults.result_map[tenant_token2][200] + AriaResults.result_map[tenant_token2][
                -5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token2][200] == SampleVariables.EVENTS_TO_SEND)

    def test_stress_tcp_1(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, tcp_connections=1, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=50000, event_keys=1, timer_to_sleep=0, event_in_between_time_to_sleep=0, sleep=False)
        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_stress_tcp_6(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, tcp_connections=6, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=50000, event_keys=1, timer_to_sleep=0, event_in_between_time_to_sleep=0, sleep=False)
        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_stress(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration = log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)
        
        send_events(logger = logger, event_count = 50000, event_keys = 1, timer_to_sleep = 0, event_in_between_time_to_sleep = 0, sleep = False)
        LogManager.flush(timeout = 30)
        
        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_stress2(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=50000, event_keys=10, timer_to_sleep=0, event_in_between_time_to_sleep=0,
                    sleep=False)
        LogManager.flush(timeout=50)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_long_haul(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=50000, event_keys=10, timer_to_sleep=0.1, event_in_between_time_to_sleep=100, sleep=True)
        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)


    def test_long_haul2(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=50000, event_keys=10, timer_to_sleep=1, event_in_between_time_to_sleep=100, sleep=True)
        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)
