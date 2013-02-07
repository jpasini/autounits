from __future__ import division

from physical_quantities import Distance, Time, Speed

def print_table_row(mph):
    '''Print mph and pace for 1 mile, 5k, 10k, half, and full marathon.'''
    s = Speed("%s mi/hr" % mph)
    distances = ['1mi','5km','10km','0.5marathon','1marathon']
    d = [Distance(x) for x in distances]
    paces = [s.pace(x).str for x in d]
    print '{0:.1f} & {1} & {2} & {3} & {4} & {5} \\\\'.format(mph, *paces)
    
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
    print_latex_header()
    print_table()
    print_latex_footer()
