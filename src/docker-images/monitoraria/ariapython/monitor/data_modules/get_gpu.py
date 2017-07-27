import subprocess

class get_gpu(object):
    #gpu utilization
    @staticmethod
    def collect_data():
        agg_info = subprocess.Popen(['nvidia-smi --query-gpu'], stdout = subprocess.PIPE, shell = True).communicate()[0]
        return agg_info.split()[157]

    @staticmethod
    def name():
        return "GPU"
