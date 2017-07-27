import subprocess
import requests

class get_cpu(object):

    # timestamp2 > timestamp1, both are strings
    @staticmethod
    def timediff(timestamp1, timestamp2):
        # remove date, hours, minutes, and timezone
        time1 = timestamp1.split("T")[1].split("-")[0].split(":")[2]
        time2 = timestamp2.split("T")[1].split("-")[0].split(":")[2]

        diff = float(time2) - float(time1)
        # sometimes minutes are crossed
        if diff < 0:
            diff += 60
        return diff

    @staticmethod
    def collect_data():
        
        #use cadvisor
        container_url = 'http://localhost:4194/api/v1.3/containers/'
        machine_url = 'http://localhost:4194/api/v1.3/machine'
        container_response = requests.get(container_url).json()
        machine_response = requests.get(machine_url).json()

        timestamp1 = str(container_response['stats'][6]['timestamp'])
        timestamp2 = str(container_response['stats'][7]['timestamp'])

        interval = get_cpu.timediff(timestamp1, timestamp2)

        max_computations = machine_response['num_cores'] * 1000000000 * interval
        num_computations = container_response['stats'][7]['cpu']['usage']['total'] - \
                           container_response['stats'][6]['cpu']['usage']['total']

        # return as a percent
        return float(num_computations / max_computations) * 100
        '''
        cpustat = subprocess.Popen(["top | grep -m 2 \"Cpu(s)\""], stdout = subprocess.PIPE, shell = True)
        cpustr = cpustat.communicate()[0]
        cpuarr = cpustr.split()
        idleTime = float(cpuarr[24]) + float(cpuarr[26])
        return 100 - idleTime
        '''
    @staticmethod
    def name():
        return "CPU"



