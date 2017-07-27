import requests

class get_network(object):

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
        container_url = 'http://localhost:4194/api/v1.3/containers/'
        machine_url = 'http://localhost:4194/api/v1.3/machine'
        container_response = requests.get(container_url).json()
        machine_response = requests.get(machine_url).json()

        curr_interface_usage = container_response['stats'][7]['network']['interfaces']
        past_interface_usage = container_response['stats'][6]['network']['interfaces']

        bytes_moved = 0
        for index in range (0, len(curr_interface_usage)):
            bytes_moved += curr_interface_usage[index]['rx_bytes'] + curr_interface_usage[index]['tx_bytes']
            bytes_moved -= past_interface_usage[index]['rx_bytes'] + past_interface_usage[index]['tx_bytes']

        interfaces = machine_response['network_devices']
        #cumulative network speed, in megabits/s
        c_net_speed = 0
        for index in range (0, len(interfaces)):
            c_net_speed += interfaces[index]['speed']

        timestamp1 = str(container_response['stats'][6]['timestamp'])
        timestamp2 = str(container_response['stats'][7]['timestamp'])

        interval = get_network.timediff(timestamp1, timestamp2)
        c_net_speed = c_net_speed * 125000 * interval

        # returns network usage in bytes/second for now
        return bytes_moved / c_net_speed

    @staticmethod
    def name():
        return 'Network'
