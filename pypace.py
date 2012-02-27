from __future__ import division

class Distance(object):
    def __init__(self):
        self._meters = None
        # Conversion constants
        self._meters_in = {
            'mi': 1609.344, 
            'km': 1000, 
            'marathon': 42194.988 }
        
    @property
    def m(self):
        '''Distance in meters.'''
        return self._meters
        
    @m.setter
    def m(self, value):
        self._meters = value
        
    @property
    def mi(self):
        '''Distance in miles.'''
        return self._meters/self._meters_in['mi']
        
    @mi.setter
    def mi(self, value):
        self._meters = value*self._meters_in['mi']
        
    @property
    def km(self):
        '''Distance in km.'''
        return self._meters/self._meters_in['km']
        
    @km.setter
    def km(self, value):
        self._meters = value*self._meters_in['km']
        
    @property
    def marathon(self):
        '''Distance in marathons.'''
        return self._meters/self._meters_in['marathon']
        
    @marathon.setter
    def marathon(self, value):
        self._meters = value*self._meters_in['marathon']

class Time(object):
    def __init__(self):
        self._secs = None
        # Conversion constants
        self._secs_in = {
            'min': 60, 
            'hr': 3600 }
        
    @property
    def s(self):
        '''Time in seconds.'''
        return self._secs
        
    @s.setter
    def s(self, value):
        self._secs = value
        
    @property
    def min(self):
        '''Time in minutes.'''
        return self._secs/self._secs_in['min']
        
    @min.setter
    def min(self, value):
        self._secs = value*self._secs_in['min']
        
    @property
    def hr(self):
        '''Time in hours.'''
        return self._secs/self._secs_in['hr']
               
    @hr.setter
    def hr(self, value):
        self._secs = value*self._secs_in['hr']
        
    @property
    def str(self):
        secs = self._secs
        hours = int(secs/self._secs_in['hr'])
        secs = secs - hours*self._secs_in['hr']
        mins = int(secs/self._secs_in['min'])
        secs = int(secs - mins*self._secs_in['min'])
        result = ""
        if hours > 0:
            result = result + str(hours) + ":"
        result = result + '{0:02d}:{1:02d}'.format(mins,secs)
        return result
        
       

def secs_for_distance(distance, meters_per_sec):
    '''Seconds required to cover distance given speed.'''
    return distance/meters_per_sec
    
def miles_to_meters(miles):
    return miles*1609.344

def marathon_to_meters(marathons):
    return marathons*42194.988

def hours_to_seconds(hours):
    return hours*3600
    
def mph_to_mps(mph):
    '''Miles/hour to meters/sec'''
    return mph*miles_to_meters(1)/hours_to_seconds(1)

def one_mile_pace(mph):
    '''Time per mile.'''
    return secs_for_distance(miles_to_meters(1), mph_to_mps(mph))
    
def secs_for_5k(mph):
    return secs_for_distance(5000, mph_to_mps(mph))

def secs_for_10k(mph):
    return secs_for_distance(10000, mph_to_mps(mph))

def secs_for_half_marathon(mph):
    return secs_for_distance(marathon_to_meters(1/2), mph_to_mps(mph))

def secs_for_marathon(mph):
    return secs_for_distance(marathon_to_meters(1), mph_to_mps(mph))

def secs_to_string(secs):
    hours = int(secs/3600)
    secs = secs - hours*3600
    mins = int(secs/60)
    secs = int(secs - mins*60)
    result = ""
    if hours > 0:
        result = result + str(hours) + ":"
    result = result + '{0:02d}:{1:02d}'.format(mins,secs)
    return result

def print_table_row(mph):
    '''Print mph and pace for 1 mile, 5k, 10k, half, and full marathon.'''
    pace1m = secs_to_string(one_mile_pace(mph))
    pace5k = secs_to_string(secs_for_5k(mph))
    pace10k = secs_to_string(secs_for_10k(mph))
    pacehalf = secs_to_string(secs_for_half_marathon(mph))
    pacefull = secs_to_string(secs_for_marathon(mph))
    print '{0:.1f} & {1} & {2} & {3} & {4} & {5} \\\\'.format(mph, pace1m, pace5k, pace10k, pacehalf, pacefull)
    
def print_table():
    mph_table = [5 + i/5 for i in range(29)]
    for mph in mph_table:
        print_table_row(mph)
    
    
def print_latex_header():
    print '''
\\documentclass[11pt]{article}
\\usepackage{amsmath}
\\usepackage{fullpage}
\\usepackage{booktabs}
\\begin{document}
\\begin{Large}
\\thispagestyle{empty}
\\sffamily
\\begin{center}
\\begin{tabular}{rrrrrr}
\\toprule
\\multicolumn{1}{c}{mph} & \\multicolumn{1}{c}{1mi} & \\multicolumn{1}{c}{5k} & \\multicolumn{1}{c}{10k} & \\multicolumn{1}{c}{half} & \\multicolumn{1}{c}{full} \\\\ \\midrule'''

def print_latex_footer():
    print '''\\bottomrule
\\end{tabular}
\\end{center}
\\end{Large}
\\end{document}'''
    
if __name__ == "__main__":
    import sys
    print_latex_header()
    print_table()
    print_latex_footer()
