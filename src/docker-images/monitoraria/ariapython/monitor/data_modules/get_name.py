import subprocess

class get_name(object):
    
    @staticmethod
    def collect_data():
        return subprocess.Popen(['hostname'], stdout = subprocess.PIPE).communicate()[0]

    @staticmethod
    def name():
        return "Name"
