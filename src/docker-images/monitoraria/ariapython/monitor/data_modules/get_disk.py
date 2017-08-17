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
        print(str(disk_map))

        for drive in disk_map:
            drive_stat = disk_map[drive]
            name = drive_stat['name']
            capacity = drive_stat['size']
            major = drive_stat['major']
            minor = drive_stat['minor']
            disks[(major, minor)] = [name, 0, capacity]
        
        print(" ")
        #all disk usage, unfortunately inconsistent so I can't pull the most recent data
        a_disk_usage = container_response['stats'][6]['diskio']['io_service_bytes']
        print(str(a_disk_usage))
        #trimmed disk usage
        for disk in a_disk_usage:
            major = disk['major']
            minor = disk['minor']
            # pretty sloppy fix, I don't know which major/minor numbers are important
            if (major, minor) in disks:
                print(str(major) + " " + str(minor))
                disks[(major, minor)][1] = disk['stats']['Total']
        
        return disks

    @staticmethod
    def name():
        return 'Disk'
