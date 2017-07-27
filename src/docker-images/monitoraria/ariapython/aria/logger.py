from __future__ import absolute_import
from . import event_properties
from threading import RLock, Thread
from .batcher import Batcher
from .bond_types import Record
from .extension import AriaExtension
from .pii_extension import AriaPiiExtension
from . import bond_types
from .batching_record import BatchingRecord
from sys import exc_info
from .log_config import AriaLog
from .utilities import AriaUtilities
from .stats_manager import StatsConstants

class EventDropReason(object):
    EVENT_NOT_ADDED = -1
    NO_EVENTS_ACCEPTED = -2
    MAX_EVENTS_REACHED = -3
    LOG_MANAGER_NOT_INITIALIZED = -4

class Logger(object):
    
    def __init__(self, source, tenantToken):
        AriaLog.aria_log.info("Logger was initialized")
        self.source = source
        self.tenant_token = tenantToken.lower()
        self.__sequence_id = 0
        self.__init_id = AriaUtilities.generate_guid()
        self.__log_event = RLock()
        self.__lock_flush = RLock()
        self.__is_flushed = False
    
    def log_event(self, arg):
        with self.__lock_flush:
            from aria.log_manager import LogManager
            if self.__is_flushed == True:
                AriaLog.aria_log.debug("Log Event doesn't accept more events, flushed was called")
                return EventDropReason.NO_EVENTS_ACCEPTED

            if LogManager == None or not LogManager.is_initialize:
                return EventDropReason.LOG_MANAGER_NOT_INITIALIZED

            if LogManager != None and LogManager.records_in_memory() >= LogManager.configuration.MAX_EVENTS_IN_MEMORY:
                if LogManager.configuration.DROP_EVENT_IF_MAX_IS_REACHED == False:
                    AriaLog.aria_log.info("Log Event doesn't accept more events, maximum capacity reached")
                    return EventDropReason.MAX_EVENTS_REACHED
                else:
                    AriaLog.aria_log.info("Events will be dropped now")
                    dropped = Batcher.drop_events()
                    if dropped == False:
                        # We have to drop this event also
                        AriaLog.aria_log.info("Log Event doesn't accept more events, maximum capacity reached")
                        return EventDropReason.EVENT_NOT_ADDED
                    # We have to drop events
                    
            sequence_id = 0
            with self.__log_event:
                self.__sequence_id += 1
                sequence_id = self.__sequence_id
            
            if type(arg) is str:
                self.__log_event_to_ariarecord(event_properties.EventProperties(arg),sequence_id)
            elif type(arg) is event_properties.EventProperties:
                self.__log_event_to_ariarecord(arg, sequence_id)
            else:
                raise TypeError("no match")
            return sequence_id

    def flush(self):
        with self.__lock_flush:
            self.__is_flushed = True

    def tear_down(self):
        del self
    
    def __log_event_to_ariarecord(self, event_properties,sequence_id):
        from aria.log_manager import LogManager
        batched_record = BatchingRecord(self.tenant_token)
        
        batched_record.sequence_id = sequence_id
        batched_record.record = bond_types.Record()
        batched_record.record.record_id = AriaUtilities.generate_guid()
        batched_record.record.type = "custom"
        batched_record.record.event_type = event_properties.name
        batched_record.record.record_type_int = event_properties.message_type
        batched_record.record.timestamp = event_properties.time_stamp_in_epoch_ms
        batched_record.record.extension = AriaExtension.get_bond("", 
                                                                 batched_record.record.event_type, 
                                                                 self.__init_id, self.__sequence_id, 
                                                                 batched_record.record.timestamp, 
                                                                 event_properties.get_properties())
        pii_prop = event_properties.get_pii_properties()
        
        if (len(list(pii_prop.items())) > 0):
            batched_record.record.pii_extensions = AriaPiiExtension.get_bond(pii_prop)

        Batcher.add_record(self.tenant_token, batched_record)
        if StatsConstants.stats_tenant_token != self.tenant_token:
            LogManager.stats_manager.events_received(self.tenant_token, 1)
