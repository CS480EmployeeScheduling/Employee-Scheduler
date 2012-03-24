# (c) 2006 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307
# USA.


from logilab.constraint import *


# games found on http://www.websudoku.com/
# I'm not sure how they rate the difficulty of their problems. 
easy = ["  5   27 ",
        " 4   79  ",
        "1 6 8  35",
        "4 32 16 9",
        "   5 8   ",
        "8 76 95 3",
        "73  2 1 6",
        "  41   2 ",
        " 12   8  "]

medium = [" 9 85    ",
          "  3 1 5  ",
          " 283   1 ",
          "   2  4 7",
          " 3     5 ",
          "4 7  5   ",
          " 4   362 ",
          "  2 7 1  ",
          "    26 3 "]

hard = [" 19 73  4",
        "   98 72 ",
        "        5",
        "      4 6",
        "93     72",
        "4 6      ",
        "8        ",
        " 92 36   ",
        "5  42 31 "]

evil = ["  1  9   ",
        " 5 4     ",
        "2   1 365",
        "     327 ",
        "9       8",
        " 821     ",
        "473 5   1",
        "     6 4 ",
        "   3  8  "]

def sudoku(problem, verbose=0):
    assert len(problem) == 9 # more sizes later
    variables = ['v%02d_%02d'%(i,j) for i in range(9) for j in range(9)]
    domains = {}
    constraints = []
    values = list('123456789')
    for v in variables:
        domains[v] = fd.FiniteDomain(values)

    # line and column constraints
    for i in range(9):
        constraints.append(fd.AllDistinct(['v%02d_%02d'%(i,j) for j in range(9)]))
        constraints.append(fd.AllDistinct(['v%02d_%02d'%(j,i) for j in range(9)]))

    # square constraints:
    for i in (0, 3, 6):
        for j in (0, 3, 6):
            constraints.append(fd.AllDistinct(['v%02d_%02d'%(i+ii,j+jj)
                                               for ii in (0, 1, 2)
                                               for jj in (0, 1, 2)]))

    # fixed values:
    for i, line in enumerate(problem):
        for j, value in enumerate(line):
            if value != ' ':
                constraints.append(fd.Equals('v%02d_%02d'%(i,j), value))
        
    r = Repository(variables, domains, constraints)
    s = Solver().solve_one(r, verbose)
    return s

def display_solution(d):
    for i in range(9):
        for j in range(9):
            print d['v%02d_%02d'%(i,j)],
        print
            
if __name__ == '__main__':
    import sys, getopt
    opts, args = getopt.getopt(sys.argv[1:], 'dv')
    verbose = 0
    display = 0
    for o,v in opts:
        if o == '-v':
            verbose += 1
        if o == '-d':
            display = 1
    sol = sudoku(evil, verbose)
    if display:
        display_solution(sol)
    else:
        print sol
