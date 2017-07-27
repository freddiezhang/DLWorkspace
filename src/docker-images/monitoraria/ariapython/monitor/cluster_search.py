
class ClusterSearch(object):

    #keep this list sorted
    machines_in_cluster = []

    @staticmethod
    def find(machine_name):
        machine_name_lower = machine_name.lower()

        index = binary_search(machine_name, 0, len(machines_in_cluster) - 1)
        if index < 0 or index >= len(machines_in_cluster):
            return None
        return index
        #unfortunately, dict returns unsorted list
        '''
        machine_names = machines_in_cluster.keys()
        for name in machine_names:
            if name == machine_name_lower
        '''

    def view_all():
        return machines_in_cluster

    def connect():
        return

    def add_machine(machine_name):
        ClusterSearch.insert_machine_into_list(machine_name, 0, len(machines_in_cluster) - 1)
        return

    @staticmethod
    def insert_machine_into_list(machine_name, lower, upper):
        if upper < 0:
            machines_in_cluster.insert(0, machine_name)
            return
        if lower >= len(machines_in_cluster):
            machines_in_cluster.append(machine_name)
            return
        middle = lower / 2 + upper / 2
        if machines_in_cluster[middle] == machine_name:
            #machine already in list
            return
        elif machines_in_cluster[middle] < machine_name:
            if machines_in_cluster[middle + 1] > machine_name:
                machines_in_cluster.insert(middle, machine_name)
                return
            else:
                ClusterSearch.add_machine(machine_name, middle + 1, upper)
                return
        else:
            ClusterSearch.add_machine(machine_name, lower, middle - 1)
            return
        return

    # for some reason i dont think this is going to work
    @staticmethod
    def binary_search(name, lower, upper):
        if upper < lower:
            return -1
        middle = lower / 2 + upper / 2
        if machines_in_cluster[middle] == name:
            return index
        elif machines_in_cluster[middle] > name:
            return ClusterSearch.binary_search(name, lower, middle - 1)
        else:
            return ClusterSearch.binary_search(name, middle + 1, upper)