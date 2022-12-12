"""
For given speed, compute the race pace for different distances.
"""

from __future__ import division

from physical_quantities import Distance, Speed

def print_table_row(speed, distances):
    '''Print mph and pace for 1 mile, 5k, 10k, half, and full marathon.'''
    paces = [speed.pace(x).str for x in distances]
    print('{0:.1f} & {1} & {2} & {3} & {4} & {5} \\\\'.format(speed['mi/hr'], *paces))

def print_table():
    """
    Print a table of pace as a function of different speeds.
    """
    distances_str = ['1 mile', '5 km', '10 km', '0.5 marathon', '1 marathon']
    distances = [Distance(x) for x in distances_str]
    speed = Speed()
    mph_table = [5 + i/5 for i in range(29)]
    for mph in mph_table:
        speed['mi/hr'] = mph
        print_table_row(speed, distances)


def print_latex_header():
    """
    Print LaTeX header for the race pace table.
    """
    print('''
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
\\multicolumn{1}{c}{mph} & \\multicolumn{1}{c}{1mi} & \\multicolumn{1}{c}{5k} & \\multicolumn{1}{c}{10k} & \\multicolumn{1}{c}{half} & \\multicolumn{1}{c}{full} \\\\ \\midrule''')

def print_latex_footer():
    """
    Print LaTeX footer for the race pace table.
    """
    print('''\\bottomrule
\\end{tabular}
\\end{center}
\\end{Large}
\\end{document}''')

if __name__ == "__main__":
    print_latex_header()
    print_table()
    print_latex_footer()
