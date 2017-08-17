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

class TestAriaSDKBVT(unittest.TestCase):
    def setUp(self):
        print("In method:" + self._testMethodName)
        pass

    def tearDown(self):
        print(AriaResults.result_map)
        print(AriaResults.events_received_callback)
        AriaResults.events_send = []
        AriaResults.events_received_callback = 0
        AriaResults.result_map = {}
        time.sleep(5)

    def test_sample(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration = log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger = logger, event_count = 500, event_keys = 50, timer_to_sleep = 0, event_in_between_time_to_sleep = 0, sleep = False)
        LogManager.flush(timeout = 30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_2_loggers(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        tenant_token2 = SampleVariables.tenant_token2
        logger = init_sample(configuration, tenant_token)
        logger2 = LogManager.get_logger("", tenant_token2)
        LogManager.add_subscriber(update)

        send_events_2_logger(logger1=logger,logger2=logger2, event_count=500, event_keys=50, timer_to_sleep=0, event_in_between_time_to_sleep=0, sleep=False)

        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == 2 * SampleVariables.EVENTS_TO_SEND)
        self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)
        self.assertTrue(AriaResults.result_map[tenant_token2][200] == SampleVariables.EVENTS_TO_SEND)

    def test_zero_flush(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=500, event_keys=50, timer_to_sleep=0, event_in_between_time_to_sleep=0, sleep=False)
        LogManager.flush(timeout=0)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def _big_event_size(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration = log_config, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger = logger, event_count = 1, event_keys = 200000, timer_to_sleep = 0, event_in_between_time_to_sleep = 0, sleep = False)
        LogManager.flush(timeout = 30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        self.assertTrue(AriaResults.result_map[tenant_token][-3] == SampleVariables.EVENTS_TO_SEND)

    def test_no_process(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration = log_config, batching_threads_count=1, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger = logger, event_count = 500, event_keys = 50, timer_to_sleep = 0, event_in_between_time_to_sleep = 0, sleep = False)
        LogManager.flush(timeout = 30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_one_process(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration = log_config, batching_threads_count=1, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger = logger, event_count = 500, event_keys = 50, timer_to_sleep = 0, event_in_between_time_to_sleep = 0, sleep = False)
        LogManager.flush(timeout = 30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_six_process_1_batch(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, batching_threads_count=1, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=500, event_keys=50, timer_to_sleep=1, event_in_between_time_to_sleep=200, sleep=True)
        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_one_process_4_batch(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, batching_threads_count=4, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=500, event_keys=50, timer_to_sleep=1, event_in_between_time_to_sleep=200, sleep=True)
        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_6_process_4_batch(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, batching_threads_count=4, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=500, event_keys=50, timer_to_sleep=1, event_in_between_time_to_sleep=200, sleep=True)
        LogManager.flush(timeout=30)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_daemon_true(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration = log_config, all_threads_daemon=True, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger = logger, event_count = 500, event_keys = 50, timer_to_sleep = 1, event_in_between_time_to_sleep = 100, sleep = True)
        LogManager.flush(timeout=5)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)

    def test_daemon_false(self):
        log_config = LogConfiguration(log_level=logging.DEBUG, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(log_configuration=log_config, all_threads_daemon=False, drop_event_if_max_is_reached = False)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        LogManager.add_subscriber(update)

        send_events(logger=logger, event_count=500, event_keys=50, timer_to_sleep=1, event_in_between_time_to_sleep=100, sleep=True)
        LogManager.flush(timeout=5)

        self.assertTrue(AriaResults.events_received_callback == SampleVariables.EVENTS_TO_SEND)
        if -5 in AriaResults.result_map[tenant_token]:
            self.assertTrue(AriaResults.result_map[tenant_token][200] + AriaResults.result_map[tenant_token][-5] == SampleVariables.EVENTS_TO_SEND)
        else:
            self.assertTrue(AriaResults.result_map[tenant_token][200] == SampleVariables.EVENTS_TO_SEND)


class TestAriaUnitTests(unittest.TestCase):
    def setUp(self):
        print("In method:" + self._testMethodName)
        pass

    def tearDown(self):
        print(AriaResults.result_map)
        print(AriaResults.events_received_callback)
        AriaResults.events_send = []
        AriaResults.events_received_callback = 0
        AriaResults.result_map = {}
        try:
            LogManager.flush(timeout=0)
        except:
            pass

    @parameterized.expand([(PiiKind.PiiKind_None, "Value"),
                            (PiiKind.PiiKind_GenericData,"Value"),
                            (PiiKind.PiiKind_None,"Value"),
                            (PiiKind.PiiKind_DistinguishedName,"Value"),
                            (PiiKind.PiiKind_GenericData,"Value"),
                            (PiiKind.PiiKind_IPv4Address,"Value"),
                            (PiiKind.PiiKind_IPv6Address,"Value"),
                            (PiiKind.PiiKind_MailSubject,"Value"),
                            (PiiKind.PiiKind_PhoneNumber,"Value"),
                            (PiiKind.PiiKind_QueryString,"Value"),
                            (PiiKind.PiiKind_SipAddress,"Value"),
                            (PiiKind.PiiKind_SmtpAddress,"Value"),
                            (PiiKind.PiiKind_Identity,"Value"),
                            (PiiKind.PiiKind_Uri,"Value"),
                            (PiiKind.PiiKind_Fqdn,"Value"),
                            (PiiKind.PiiKind_IPv4AddressLegacy,"Value"),
                            (PiiKind.PiiKind_None, u"❤Value"),
                            (PiiKind.PiiKind_GenericData, u"❤Value"),
                            (PiiKind.PiiKind_None, u"❤Value"),
                            (PiiKind.PiiKind_DistinguishedName, u"❤Value"),
                            (PiiKind.PiiKind_GenericData, u"❤Value"),
                            (PiiKind.PiiKind_IPv4Address, u"❤Value"),
                            (PiiKind.PiiKind_IPv6Address, u"❤Value"),
                            (PiiKind.PiiKind_MailSubject, u"❤Value"),
                            (PiiKind.PiiKind_PhoneNumber, u"❤Value"),
                            (PiiKind.PiiKind_QueryString, u"❤Value"),
                            (PiiKind.PiiKind_SipAddress, u"❤Value"),
                            (PiiKind.PiiKind_SmtpAddress, "u❤Value"),
                            (PiiKind.PiiKind_Identity, u"❤Value"),
                            (PiiKind.PiiKind_Uri, u"❤Value"),
                            (PiiKind.PiiKind_Fqdn, u"❤Value"),
                            (PiiKind.PiiKind_IPv4AddressLegacy, u"❤Value"),
    ])
    def test_EventPropertiesPII(self, piiType, value):
        propertyName = "Property"
        event = EventProperties(propertyName)
        event.set_property(propertyName, value, piiType)

        if piiType == PiiKind.PiiKind_None:
            self.assertTrue(propertyName in event.get_properties())
            self.assertTrue(propertyName not in event.get_pii_properties())
        else:
            self.assertTrue(propertyName in event.get_pii_properties())
            self.assertTrue(propertyName not in event.get_properties())

    @parameterized.expand([(1,),
                           (2,),
                           (3,),
                           (4,),
                           (5,),
                           (6,),])
    def test_LogConfiguration(self, tcpConnections):
        if tcpConnections > 6:
            self.assertRaises(Exception, LogManagerConfiguration(tcp_connections=tcpConnections))

        configuration = LogManagerConfiguration(tcp_connections=tcpConnections)
        log_config = LogConfiguration(log_level=logging.ERROR, file_prefix=self._testMethodName)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        self.assertTrue(len(LogManager.aria_sender_threads) == configuration.TCP_CONNECTIONS)
        LogManager.flush(timeout=5)

    @parameterized.expand([(1,),
                           (2,),
                           (3,),
                           (5,),
                           (10,),
                           (12,),])
    def test_LogConfiguration(self, batcherThreads):
        log_config = LogConfiguration(log_level=logging.ERROR, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(batching_threads_count=batcherThreads, log_configuration = log_config)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        result = len(batcher.Batcher.bathcer_thread_list) == batcherThreads + 1     # We must count the "Lazy Thread"
        LogManager.flush(timeout=10)
        self.assertTrue(result)

    @parameterized.expand([(1,),
                       (200,),
                       (300,),
                       (5212,),
                       (101,),
                       (1211,), ])
    def test_MaxEventsToBatch(self, eventsToBatch):
        log_config = LogConfiguration(log_level=logging.ERROR, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(max_events_to_batch = eventsToBatch, log_configuration=log_config)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)
        result = LogManager.configuration.MAX_EVENTS_TO_BATCH == eventsToBatch  # We must count the "Lazy Thread"
        LogManager.flush(0)
        self.assertTrue(result)

    @parameterized.expand([(100,),
                           (200,),
                           (1000,),
                           (500,),
                           (10000,),])
    def test_MaxEventsInMemory(self, eventsInMemory):
        log_config = LogConfiguration(log_level=logging.ERROR, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(max_events_in_memory=eventsInMemory, log_configuration=log_config)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)

        # Try to send 10 times the amound of EventsInMemory to see if at anypoit it exeeds the nubmer
        event_properties = EventProperties("Event")
        maxEventsInMemory = 0

        for i in range(10 * eventsInMemory):
            logger.log_event(event_properties)
            maxEventsInMemory = max(maxEventsInMemory, LogManager.events_in_memory);

        result = maxEventsInMemory <= eventsInMemory  # We must count the "Lazy Thread"
        LogManager.flush(0)
        self.assertTrue(result)

    @parameterized.expand([(True,),
                           (False,),])
    def test_DropEvents(self, dropEvents):
        maxEventsInMemory = 100
        log_config = LogConfiguration(log_level=logging.ERROR, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(max_events_in_memory = maxEventsInMemory, drop_event_if_max_is_reached=dropEvents, log_configuration=log_config)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)

        # Try to send 10 times the amound of EventsInMemory to see if at anypoit it exeeds the nubmer
        event_properties = EventProperties("Event")

        result = dropEvents
        for i in range(maxEventsInMemory * 10):
            eventID = logger.log_event(event_properties)
            if dropEvents:
                result &= eventID > 0       # Doesn't matter what happens our event is added
            else:
                result |= eventID < 0          # We will reach a point where we have to drop events, and in this case it will be our event

        LogManager.flush(0)
        self.assertTrue(result)

    @parameterized.expand([(100,  2, 100, 1000, True, 4, True),
                           (200,  1, 200, 1000, True, 5, True),
                           (1000, 6, 200, 100, True, 1, True),
                           (500,  2, 300, 1000, True, 3, False),
                           (1000, 2, 100, 1000, False, 2, True),
                           (100, 3, 300, 1000, True, 3, False),
                           (200, 4, 200, 1000, False, 1, True),
                           (1000, 5, 200, 1000, True, 2, False),
                           (500, 6, 100, 1000, False, 4, True),
                           (1000, 3, 100, 1000, True, 4, False),
                           ])
    def test_FlushAndTrearDown(self,
                               eventsToSend,
                               tcp_connections,
                               max_events_to_batch,
                               max_events_in_memory,
                               drop_event_if_max_is_reached,
                               batching_threads_count,
                               all_threads_daemon):
        log_config = LogConfiguration(log_level=logging.ERROR, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(tcp_connections=tcp_connections,
                                                log_configuration=log_config,
                                                max_events_to_batch=max_events_to_batch,
                                                max_events_in_memory=max_events_in_memory,
                                                drop_event_if_max_is_reached=drop_event_if_max_is_reached,
                                                batching_threads_count=batching_threads_count,
                                                all_threads_daemon=all_threads_daemon)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)

        # Try to send 10 times the amound of EventsInMemory to see if at anypoit it exeeds the nubmer
        event_properties = EventProperties("Event")

        for i in range(eventsToSend):
            logger.log_event(event_properties)

        try:
            LogManager.flush(0)
        except Exception as e:
            self.assertTrue(False)


    @parameterized.expand([(100,  2, 100, 1000, True, 4, True),])
    def test_SendEventsAfterFlush(self,
                               eventsToSend,
                               tcp_connections,
                               max_events_to_batch,
                               max_events_in_memory,
                               drop_event_if_max_is_reached,
                               batching_threads_count,
                               all_threads_daemon):
        log_config = LogConfiguration(log_level=logging.ERROR, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(tcp_connections=tcp_connections,
                                                log_configuration=log_config,
                                                max_events_to_batch=max_events_to_batch,
                                                max_events_in_memory=max_events_in_memory,
                                                drop_event_if_max_is_reached=drop_event_if_max_is_reached,
                                                batching_threads_count=batching_threads_count,
                                                all_threads_daemon=all_threads_daemon)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)

        # Try to send 10 times the amound of EventsInMemory to see if at anypoit it exeeds the nubmer
        event_properties = EventProperties("Event")

        for i in range(eventsToSend):
            logger.log_event(event_properties)

        LogManager.flush(0)
        try:
            for i in range(eventsToSend):
                logger.log_event(event_properties)
        except Exception as e:
            self.assertTrue(False)

    @parameterized.expand([(10, 100, 2, 100, 1000, True, 4, True), ])
    def test_SendEventsAfterFlushRepedetly(self,
                                  repeatTime,
                                  eventsToSend,
                                  tcp_connections,
                                  max_events_to_batch,
                                  max_events_in_memory,
                                  drop_event_if_max_is_reached,
                                  batching_threads_count,
                                  all_threads_daemon):
        log_config = LogConfiguration(log_level=logging.ERROR, file_prefix=self._testMethodName)
        configuration = LogManagerConfiguration(tcp_connections=tcp_connections,
                                                log_configuration=log_config,
                                                max_events_to_batch=max_events_to_batch,
                                                max_events_in_memory=max_events_in_memory,
                                                drop_event_if_max_is_reached=drop_event_if_max_is_reached,
                                                batching_threads_count=batching_threads_count,
                                                all_threads_daemon=all_threads_daemon)
        tenant_token = SampleVariables.tenant_token
        logger = init_sample(configuration, tenant_token)

        # Try to send 10 times the amound of EventsInMemory to see if at anypoit it exeeds the nubmer
        event_properties = EventProperties("Event")

        for j in range(repeatTime):
            try:
                for i in range(eventsToSend):
                    logger.log_event(event_properties)
                LogManager.flush(0)
            except Exception as e:
                self.assertTrue(False)

    @parameterized.expand([(10, 100, 2, 100, 1000, True, 4, True), ])
    def test_SendEventsAfterFlushRepedetlyWithInit(self,
                                  repeatTime,
                                  eventsToSend,
                                  tcp_connections,
                                  max_events_to_batch,
                                  max_events_in_memory,
                                  drop_event_if_max_is_reached,
                                  batching_threads_count,
                                  all_threads_daemon):
        for j in range(repeatTime):
            log_config = LogConfiguration(log_level=logging.ERROR, file_prefix=self._testMethodName)
            configuration = LogManagerConfiguration(tcp_connections=tcp_connections,
                                                    log_configuration=log_config,
                                                    max_events_to_batch=max_events_to_batch,
                                                    max_events_in_memory=max_events_in_memory,
                                                    drop_event_if_max_is_reached=drop_event_if_max_is_reached,
                                                    batching_threads_count=batching_threads_count,
                                                    all_threads_daemon=all_threads_daemon)
            tenant_token = SampleVariables.tenant_token
            logger = init_sample(configuration, tenant_token)

            # Try to send 10 times the amound of EventsInMemory to see if at anypoit it exeeds the nubmer
            event_properties = EventProperties("Event")
            try:
                for i in range(eventsToSend):
                    logger.log_event(event_properties)
                LogManager.flush(0)
            except Exception as e:
                self.assertTrue(False)