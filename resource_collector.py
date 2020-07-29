#!/usr/bin/python

import re
import sys
import time
from subprocess import check_output

# TODO: change to read this interval from a config file
TIME_INTERVAL = 5.0

class ResourceCollector(object):

    def __init__(self, percentage=True, sleeptime = 1):
        self.percentage = percentage
        self.cpustat = '/proc/stat'
        self.sep = ' '
        self.sleeptime = sleeptime
        self.test_duration = 5

    # Parse and extract units from value.
    def __parse_units(self, v):
        if 'B' in v:
            return int(v.replace('B', ''))
        elif 'k' in v:
            return int(v.replace('k', '')) * 1000
        elif 'M' in v:
            return int(v.replace('M', '')) * 1000000
        else:
            return int(v)

    # Get CPU information from /proc/stat file.
    # Algorithm used is based on:
    # https://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux/
    def __get_cpu_time(self):
        cpu_info = {}
        with open(self.cpustat, 'r') as f_stat:
            lines = [line.split(self.sep) for content in f_stat.readlines() for line in content.split('\n') if line.startswith('cpu')]
            # compute for every cpu
            for cpu_line in lines:
                # remove empty elements
                if '' in cpu_line:
                    cpu_line.remove('')
                cpu_line = [cpu_line[0]]+[float(i) for i in cpu_line[1:]]
                cpu_id, user, nice, system, idle, iowait, irq, softrig, steal, guest, guest_nice = cpu_line
                Idle = idle + iowait
                NonIdle = user + nice + system + irq + softrig + steal
                Total = Idle + NonIdle
                cpu_info.update({cpu_id:{'total': Total, 'idle': Idle}})
            return cpu_info

    #Compute average CPU usage based on /proc/stat file
    def get_cpu_usage(self):
        total = 0
        for _ in range(self.test_duration):
            start = self.__get_cpu_time()
            time.sleep(self.sleeptime)
            stop = self.__get_cpu_time()
            cpu_load = {}
            for cpu in start:
                Total = stop[cpu]['total']
                PrevTotal = start[cpu]['total']
                Idle = stop[cpu]['idle']
                PrevIdle = start[cpu]['idle']
                CPU_Percentage=((Total - PrevTotal) - (Idle - PrevIdle))/(Total - PrevTotal)*100
                cpu_load.update({cpu: CPU_Percentage})
            current_avg = sum(cpu_load.values())/len(cpu_load.keys())
            total += current_avg
        return total/self.test_duration

    #Compute bandwidth usage based on dstat tool
    def get_bandwidth_usage(self):
        rx_total, tx_total = (0, 0)
        # execute dstat for 'test_duration' seconds
        bwidth = check_output(['dstat', '-n', '--nocolor' ,'1', str(self.test_duration)]).split('\n')[2:-1]
        # parse dstat output
        for _ in bwidth:
            rx, tx = [self.__parse_units(v) for v in ' '.join(re.sub('\x1b.*?m', '', _).split()).split(' ')]
            rx_total += rx # total received (Bytes)
            tx_total += tx # total sent (Bytes)
        # get recv and sent bandwidth average
        rx_avg = rx_total/self.test_duration
        tx_avg = tx_total/self.test_duration
        return rx_avg, tx_avg

if __name__ == '__main__':
    rc = ResourceCollector()
    # collect system resource usage every 'TIME_INTERVAL' seconds
    start = time.time()
    while True:
        # collect CPU usage
        with open('/opt/vines/resources/cpu_usage', 'a+') as f_cpu:
            entry = str(rc.get_cpu_usage()) + '\n'
            f_cpu.write(entry)
        # collect bandwidth usage with dstat
        with open('/opt/vines/resources/bandwidth_usage', 'a+') as f_bw:
            entry = ' '.join([str(_) for _ in rc.get_bandwidth_usage()]) + '\n'
            f_bw.write(entry)
        time.sleep(TIME_INTERVAL - ((time.time() - start) % TIME_INTERVAL))