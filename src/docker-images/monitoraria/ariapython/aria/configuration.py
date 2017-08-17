from __future__ import absolute_import
from .log_config import LogConfiguration
import multiprocessing

class ConfiguationLimits(object):
    MAX_TCP_CONNECTION_ALLOWED = 6
    MIN_TCP_CONNECTION_ALLOWED = 1

class LogManagerConfiguration(object):
    was_init = False
    def __init__(self, tcp_connections = 3
                     , max_events_to_batch = 200
                     , max_events_in_memory = 40000
                     , log_configuration = None
                     , drop_event_if_max_is_reached = True
                     , batching_threads_count = 3
                     , all_threads_daemon = False):
        """!@brief Creates a new LogManagerConfiguration object.

            This LogManagerConfiguration is being used to configurate LogManager

            @param tcp_connections Number of TCP connections we create, there will be a thread per TCP connection
            @param max_events_in_memory Maximum number of events in memory at any point.
            @param max_events_to_batch Maximum number of events that are batched together.
            @param log_configuration LogConfiguration for Debugging purposes
            @param drop_event_if_max_is_reached If this is True, old events are dropped to make space for the the new event. If it's false, the latest event is dropped.
            @param batching_threads_count Number of batching threads.
            @param all_threads_daemon Set up all the threads that are created as Daemon or not.
        """

        if log_configuration == None:
            log_configuration = LogConfiguration()

        # Prechecks:
        if tcp_connections > ConfiguationLimits.MAX_TCP_CONNECTION_ALLOWED or tcp_connections < ConfiguationLimits.MIN_TCP_CONNECTION_ALLOWED:
            raise Exception("TCP Connection can't be higher than " + str(ConfiguationLimits.MAX_TCP_CONNECTION_ALLOWED) +
                            " or lower than " + str(ConfiguationLimits.MIN_TCP_CONNECTION_ALLOWED))
        
        LogManagerConfiguration.was_init = True
        self.DROP_EVENT_IF_MAX_IS_REACHED = drop_event_if_max_is_reached
        self.log_configuration = log_configuration
        self.MAX_EVENTS_IN_MEMORY = max_events_in_memory
        self.BATCHER_TIMER = 0.050                          # ms
        self.SENDER_TIMER = 0.050                           # ms
        self.SENDER_LAZY_TIMER = 10                         # Seconds
        self.LAZY_BATCHER_TIMER = 10                        # Seconds
        self.MAX_EVENTS_TO_BATCH = max_events_to_batch
        self.TCP_CONNECTIONS = tcp_connections
        self.ARIA_SENDER_TIMER = 0.050
        self.SUPPORT_GZIP = True
        self.MAX_SIZE_ALLOWED = 3 * 1024 * 1024 - 5 * 1024   # 5KB Safe margin
        self.QUEUE_DROPPED_EVENTS = int(min(max_events_to_batch/10, 200))
        self.MAX_RETRY_COUNT = 4
        self.STATS_CADENCE = 3 * 60                                     # 5 minutes between stats
        self.PROCESS_NUMBER = batching_threads_count                      # If this is set up to 0 then BATCHING_THREADS will be used to set up the threads
        self.ALL_THREADS_DEAMON = all_threads_daemon