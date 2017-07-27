from __future__ import absolute_import
from threading import RLock
from . import log_config
from . import logger
from . import configuration
from .batcher import Batcher
from . import sender
from .compact_binary_protocol import CompactBinaryProtocolWriter
from .bond import AriaBond
import threading 
from multiprocessing import Pool
from .subscribe import Subscribe
from .stats_manager import StatsManager
import sys
from six.moves import range

class LogManager(object):
    #from AriaCore import AriaEventsTransmitter
    __loggers = {}       # list of loggers unique for the combination source, tenantToken
    tenant_token = ""
    #event_transmitter = AriaEventsTransmitter()
    logger_lock = RLock()
    is_initialize = False
    events_in_memory = 0
    events_in_memory_lock = RLock()
    configuration = None
    log_manager_initializes = False
    aria_sender_threads = []
    pool_process = None
    aria_bond = None
    subscribers = None
    stats_manager = None
    is_flushed = False
    flushed_called = False    
    
    @staticmethod
    def __StartThreads():
        ''' This method stats Batcher threads and sender threads '''
        log_config.AriaLog.aria_log.info("Starting all threads")
        Batcher.define_threads()
        Batcher.start_sender_lazy_thread()
        Batcher.start_batcher_thread()
        Batcher.start_sender_thread()
        
        for index in range(LogManager.configuration.TCP_CONNECTIONS):
            aria_sender = sender.AriaSender(index)
            aria_sender.start_thread()
            LogManager.aria_sender_threads.append(aria_sender)
    
    @staticmethod
    def records_in_memory():
        return LogManager.events_in_memory
      
    @staticmethod
    def increment_events_in_memory(count = 1):
        with LogManager.events_in_memory_lock:
            LogManager.events_in_memory += count
    
    @staticmethod
    def decrement_events_in_memory(count = 1):
        with LogManager.events_in_memory_lock:
            LogManager.events_in_memory -= count
            if LogManager.events_in_memory < 0:
                log_config.AriaLog.aria_log.warning("Number of events in memory is negative. Something is wrong.")
        
    @staticmethod
    def initialize(tenantToken, log_manager_conf = None):
        log_config.AriaLog.aria_log.info("LogManager Init was called!")
        if log_manager_conf == None:
            log_manager_conf = configuration.LogManagerConfiguration()
        # from AriaCore import init_log,aria_log
        if LogManager.is_initialize == True:
            return
        
        from .stats_manager import StatsConstants, StatsManager
        if LogManager.is_initialize == False:
            try:
                with LogManager.logger_lock:
                    # Initialize the log_manager
                    LogManager.configuration = log_manager_conf
                    log_config.init_log(log_manager_conf.log_configuration)
                    
                    # Init the subscribers
                    LogManager.subscribers = Subscribe()
                    
                    # Init the aria bond for better performance
                    CompactBinaryProtocolWriter.InitGenerated()
                    
                    # copy the tenant_token
                    LogManager.tenant_token = tenantToken
                    
                    # Get the logger
                    logger =  LogManager.__create_or_get_logger("", LogManager.tenant_token)
                    
                    # Populate the sdk for the stats
                    StatsConstants().PopulateSDKVersion()
                    
                    # Start the threads for sending events and batcher
                    LogManager.__StartThreads()
                    
                    # Define the stats manager for Log Manager
                    LogManager.stats_manager = StatsManager()
                    
                    # Initialize a static instance of Aria BOnd
                    AriaBond.init_static()
                    
                    # Create a poll process for the LogManager to be used for serializing the events
                    LogManager.pool_process = Pool(LogManager.configuration.PROCESS_NUMBER)
                    
                    # Create an instance of Aria Bond for the log_manager
                    LogManager.aria_bond = AriaBond()
                    
                    #Specify that the initialze was completed
                    LogManager.is_initialize = True
                    
                    log_config.AriaLog.aria_log.info("Intialize completed successfuly ")
                    return logger
            except:
                log_config.AriaLog.aria_log.error("Error while initialize the LogManager:" + str(sys.exc_info()[0]))
                LogManager.is_initialize = False
                pass
    
    @staticmethod
    def add_subscriber(subscriber):
        log_config.AriaLog.aria_log.info("subscriber added")
        if LogManager.is_initialize == False:
            log_config.AriaLog.aria_log.debug("subscriber added failed")
            return False
        LogManager.subscribers.register(subscriber)
    
    @staticmethod
    def remove_subscriber(subscriber):
        log_config.AriaLog.aria_log.info("remove_subscriber")
        if LogManager.is_initialize == False:
            return False
        try:
            LogManager.subscribers.unregister(subscriber)
            return True        
        except:
            log_config.AriaLog.aria_log.warning("remove_subscriber failed" + str(sys.exc_info()[0]))
            return False
    @staticmethod
    def remove_all_subscriber(subscriber):
        log_config.AriaLog.aria_log.info("remove_all_subscriber")
        if LogManager.is_initialize == False:
            return None
        try:
            LogManager.subscribers.unregister_all()
        except:
            log_config.AriaLog.aria_log.warning("remove_all_subscribers failed"  + str(sys.exc_info()[0]))
            return False
    
    @staticmethod    
    def get_logger(source="", tenantToken=""):
        log_config.AriaLog.aria_log.info("get_logger")
        if LogManager.is_initialize == False:
            return None
        try:
            with LogManager.logger_lock:
                return LogManager.__create_or_get_logger(source, tenantToken)
        except:
            log_config.AriaLog.aria_log.warning("get_logger failed "  + str(sys.exc_info()[0]))
            return None
            
    @staticmethod
    def flush(timeout = 10):
        if not LogManager.is_initialize:
            return

        from time import sleep
        from .stats_manager import StatsConstants
        log_config.AriaLog.aria_log.info("flush was called")
        LogManager.stats_manager.flush_and_tead_down()
        flushed_called = True
        #try:
        with LogManager.logger_lock:
            
            # Stop each logger to receive events
            for i in LogManager.__loggers:
                if LogManager.__loggers[i].tenant_token != StatsConstants.stats_tenant_token:
                    LogManager.__loggers[i].flush()
            
            # Stop the batcher theards and process the remaining events
            Batcher.flush()
            timeout_packages = timeout
            while LogManager.events_in_memory > 0  and timeout_packages > 0:
                log_config.AriaLog.aria_log.debug(str(LogManager.events_in_memory) + " events in memory yet")
                sleep(1)
                timeout_packages -= 1
            
            # Send stats:
            LogManager.stats_manager.flush()
            Batcher.send_all_remaining_events()
            
            if timeout == 0:
                timeout = 1
            timeout_stats = timeout
            while LogManager.events_in_memory > 0  and timeout_stats > 0:
                log_config.AriaLog.aria_log.debug(str(LogManager.events_in_memory) + " events in memory yet")
                sleep(1)
                timeout_stats -= 1
            
            for i in LogManager.__loggers:
                if LogManager.__loggers[i].tenant_token == StatsConstants.stats_tenant_token:
                    LogManager.__loggers[i].flush()
            
            for aria_sender in LogManager.aria_sender_threads:
                try:
                    aria_sender.stop_thread()
                except:
                    pass
            
            if LogManager.configuration.PROCESS_NUMBER !=0:
                LogManager.pool_process.close()
            LogManager.is_flushed = True
            
            # Revert all the variables to start
            LogManager.__loggers = {}
            LogManager.tenant_token = ""
            LogManager.logger_lock = RLock()
            LogManager.is_initialize = False
            LogManager.events_in_memory = 0
            LogManager.events_in_memory_lock = RLock()
            LogManager.configuration = None
            LogManager.log_manager_initializes = False
            LogManager.aria_sender_threads = []
            LogManager.pool_process = None
            LogManager.aria_bond = None
            LogManager.subscribers = None
            LogManager.stats_manager = None
            LogManager.is_flushed = False
            log_config.AriaLog.aria_log.info("Flushed finished")
        return True
    
    @staticmethod
    def empty_the_system():
        log_config.AriaLog.aria_log.info("empty_the_system was called")
        Batcher.stop_and_clean_up()
    
    @staticmethod
    def tear_down(self):
        del LogManager.__loggers
        
    def flush_and_tear_down(self):
        LogManager.flush()
        LogManager.tear_down(self)
    
    @staticmethod
    def __create_or_get_logger(source, tenantToken):
        log_config.AriaLog.aria_log.info("Return a logger for tenant:" + tenantToken)
        try:
            if (source, tenantToken) in LogManager.__loggers:
                logger_local = LogManager.__loggers[(source, tenantToken)]
            else:
                log_config.AriaLog.aria_log.info("Create a logger")
                logger_local = logger.Logger(source, tenantToken)
                LogManager.__loggers[(source, tenantToken)] = logger_local
            return logger_local
        except:
            log_config.AriaLog.aria_log.warning("Create a logger " + str(sys.exc_info()[0]))
            return None