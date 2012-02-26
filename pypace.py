def create_all_pairs(n,m):
    '''Given n, return a list of all pairs [i,j] where
    2 <= i <= n and 2 <= j <= n.'''
    a = range(2,n+1)  # 0..n
    b = range(2,m+1)  # 0..m
    return [[i,j] for i in a for j in b]
    
def incorrect_pairs():
    incorrect = [
        [3,8],
        [4,12],
        [5,12],
        [6,8],
        [8,7],
        [8,9]]
    return incorrect
        
    
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
