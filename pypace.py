from __future__ import division

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
    mph_table = [5 + i/5 for i in range(31)]
    for mph in mph_table:
        print_table_row(mph)
    
    
def print_latex_header():
    print '''
\\documentclass[12pt]{article}
\\usepackage{amsmath}
\\usepackage{fullpage}
\\begin{document}
\\begin{large}
\\thispagestyle{empty}
\\begin{tabular}{rrrrrr}
mph & 1mi & 5k & 10k & half & full \\\\'''

def print_latex_footer():
    print '''\\end{tabular}
\\end{large}
\\end{document}'''
    
if __name__ == "__main__":
    import sys
    print_latex_header()
    print_table()
    print_latex_footer()
