import subprocess

class DataTracker:
    @staticmethod
    def tracklogs(directory):
        # logstat = {}
        logtotal = 0
        # somehow have to get admin privileges
        logfiles = subprocess.Popen(["ls -nl " + directory], stdout = subprocess.PIPE, shell = True)
        logstr = logfiles.communicate()[0]
        ealog = logstr.splitlines()
        for a in range(len(ealog)):
            if a == 0:
                continue
            # newkey = ""
            file = ealog[a]
            newval = 0
            filestat = file.split()
            # newkey = filestat[8]
            if filestat[0][0] == 100:
                newdir = directory + "/" + str(filestat[8])[1:]
                newval = DataTracker.tracklogs(newdir) + 4096
                '''
                dirstat = tracklogs(newdir)
                for key in dirstat:
                    newval += dirstat[key]
                '''
            else:
                try:
                    newval = int(filestat[4])
                except:
                    newval = 0
                    # put this in a better log
                    print("Directory was empty")
            logtotal += newval
        return logtotal
        '''
            logstat[newkey] = newval
        return logstat
        '''
    # returns an aggregate filesize
    # commented code returns a dict of filenames and sizes

    @staticmethod
    def get_disk_usage():
        return (1 - float(DataTracker.get_available_disk()) / float(DataTracker.get_total_disk())) * 100
    # returns a percent

    @staticmethod
    def get_available_disk():
        diskls = subprocess.Popen(['df'], stdout = subprocess.PIPE)
        diskstr = diskls.communicate()[0]
        ealine = diskstr.split()
        a = 10
        available = 0
        while(a < len(ealine)):
            available += int(ealine[a])
            a += 6
        return available
    # returns number of available 1K blocks


    @staticmethod
    def get_total_disk():
        diskls = subprocess.Popen(['df'], stdout = subprocess.PIPE)
        diskstr = diskls.communicate()[0]
        ealine = diskstr.split()
        a = 8
        total = 0
        while (a < len(ealine)):
            total += int(ealine[a])
            a += 6
        return total
    
    @staticmethod
    def get_total_cpu():
        # I count both idle and iowait as idle
        cpustat = subprocess.Popen(["top | grep -m 2 \"Cpu(s)\""], stdout = subprocess.PIPE, shell = True)
        cpustr = cpustat.communicate()[0]
        cpuarr = cpustr.split()
        idleTime = float(cpuarr[24]) + float(cpuarr[26])
        return 100 - idleTime
     # returns a percent
