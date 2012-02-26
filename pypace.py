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

def pace(mph):
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
    secs = secs - mins*60
    result = ""
    if hours > 0:
        result = result + str(hours) + ":"
    result = result + '{0:02d}:{1:02d}'.format(mins,secs)
    return result


    
    
    
def print_problem(pair):
    '''Given a pair [i,j], print a problem.'''
    print pair[0], ' \\times ', pair[1], '&= \\qquad & '
    
def print_latex_header(num_problems,time_for_problems):
    print '''
\\documentclass[12pt]{article}
\\usepackage{amsmath}
\\begin{document}
\\begin{Huge}\n'''
    print num_problems, 'problems,', time_for_problems, 'minutes:\n'
    print '\\begin{align*}'

def print_latex_footer():
    print '''\\end{align*}
\\end{Huge}
\\end{document}'''
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print '\nUsage: python times_tables.py num_problems> time_for_problems > output.tex\n'
        exit(0)
    num_problems = int(sys.argv[1])
    time_for_problems = int(sys.argv[2])
    pairs = create_all_pairs(9,12)
    import random
    my_problems = random.sample(pairs,num_problems)
    print_latex_header(num_problems,time_for_problems)
    for i in range(len(my_problems)):
        if i % 3 == 0:
            print '\\\\ '
        print_problem(my_problems[i])
        
    print_latex_footer()
