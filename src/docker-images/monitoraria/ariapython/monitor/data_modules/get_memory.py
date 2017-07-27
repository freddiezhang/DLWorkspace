import requests

class get_memory(object):

    @staticmethod
    def collect_data():
        container_url = 'http://localhost:4194/api/v1.3/containers/'
        machine_url = 'http://localhost:4194/api/v1.3/machine'
        container_response = requests.get(container_url).json()
        machine_response = requests.get(machine_url).json()

        # is this disk or RAM? assume RAM as 200GB disk seems small
        max_memory = machine_response['memory_capacity']
        used_memory = container_response['stats'][7]['memory']['usage']
        #return as a percent
        return float(used_memory) / float(max_memory) * 100

    @staticmethod
    def name():
        return "Memory"
