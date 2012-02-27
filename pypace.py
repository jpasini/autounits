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

class Speed(object):
    def __init__(self):
        self._mps = None # store internally in meters/sec
        # Conversions
        d = Distance()
        t = Time()
        d.mi = 1
        t.hr = 1
        self._mph_to_mps = d.m/t.s
        
    @property
    def mps(self):
        '''Speed in meters/second.'''
        return self._mps
        
    @mps.setter
    def mps(self, value):
        self._mps = value
        
    @property
    def mph(self):
        '''Speed in miles per hour.'''
        return self._mps/self._mph_to_mps
        
    @mph.setter
    def mph(self, value):
        self._mps = value*self._mph_to_mps
        
    def pace(self, distance):
        '''Return time to cover given distance.'''
        t = Time()
        t.s = distance.m/self.mps
        return t
        
def print_table_row(mph):
    '''Print mph and pace for 1 mile, 5k, 10k, half, and full marathon.'''
    s = Speed()
    s.mph = mph
    d = Distance()
    d.mi = 1
    pace1m = s.pace(d).str
    d.km = 5
    pace5k = s.pace(d).str
    d.km = 10
    pace10k = s.pace(d).str
    d.marathon = 0.5
    pacehalf = s.pace(d).str
    d.marathon = 1
    pacefull = s.pace(d).str
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
