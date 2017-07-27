import requests

class get_disk(object):
    @staticmethod
    def collect_data():
        container_url = 'http://localhost:4194/api/v1.3/containers/'
        machine_url = 'http://localhost:4194/api/v1.3/machine'

        machine_response = requests.get(machine_url).json()
        container_response = requests.get(container_url).json()
        disks = {}

        disk_map = machine_response['disk_map']

        #figure this out!!
        for drive in disk_map:
            drive_stat = disk_map[drive]
            name = drive_stat['name']
            capacity = drive_stat['size']
            major = drive_stat['major']
            minor = drive_stat['minor']
            disks[(major, minor)] = [name, 0, capacity]
        
        #all disk usage
        a_disk_usage = container_response['stats'][7]['diskio']['io_service_bytes']
        #trimmed disk usage
        for disk in a_disk_usage:
            if disk['stats']['Total'] != 0:
                major = disk['major']
                minor = disk['minor']
                disks[(major, minor)][1] = disk['stats']['Total']
        
        return disks

    @staticmethod
    def name():
        return 'Disk'
