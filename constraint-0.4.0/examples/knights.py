#!/usr/bin/env python2.3
# -*- coding: ISO-8859-1 -*-
"""Knight tour problem:
Place n*n values on a checker so
that consecutive values are a knight's
move away from each other"""


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
from logilab.constraint.distributors import *

def knight_tour(size=6,verbose=0):
    variables = []
    domains = {}
    constraints = []
    black_checker=[]
    # the black tiles
    white_checker=[]
    #the white tiles: one less if n is odd
    for row in range(size):
        for column in range(size):
            if (row+column)%2==0:
                black_checker.append((row,column))
            else:
                white_checker.append((row, column))

    # One variable for each step in the tour
    for i in range(size*size):
        name = 'x%02d'%i
        variables.append(name)
        # The knight's move jumps from black to white
        # and vice versa, so we make all the even steps black
        # and all the odd ones white.
        if i%2==0:
            domains[name] = fd.FiniteDomain(black_checker)
        else:
            domains[name] = fd.FiniteDomain(white_checker)
        if i > 0:
            j = i -1
            k1 = 'x%02d'%j
            k2 = 'x%02d'%i
            # the knight's move constraint
            c = fd.make_expression((k1,k2),
                       'abs(%(v1)s[0]-%(v2)s[0]) + abs(%(v1)s[1]-%(v2)s[1]) == 3'%\
                       {'v1':k1,'v2':k2})
            constraints.append(c)
            c = fd.make_expression((k1,k2),
                       'abs(abs(%(v1)s[0]-%(v2)s[0]) - abs(%(v1)s[1]-%(v2)s[1])) == 1'%\
                       {'v1':k1,'v2':k2})
            constraints.append(c)
    constraints.append(fd.AllDistinct(variables))
    half = size/2
    r = Repository(variables,domains,constraints)
    sol = Solver(EnumeratorDistributor()).solve_one(r,verbose)	
    return sol 

def draw_solution(sol, size):
    # change the keys into elements, elements into keys
    # to display the results.
    # I'm sure there's a better way to do this, but I'm 
    # new to python
    board = ''
    board += '_'*(size*3+1)+'\n'
    squares = {}
    for t in sol.items():
        squares[(t[1][0]*size)+t[1][1]]=t[0]   
    for i in range(size):
        for j in range(size):
        # find the variable whose value is (i,j)
            square = squares[i*size+j]
            # numbering should start from 1 ,not 0
            intsquare = int(square[1:4]) + 1
            board+='|%02s'%intsquare
        board+='|\n'
    board += '¯'*(size*3+1)+'\n'
    print board


if __name__ == '__main__':
    import sys,getopt
    opts,args = getopt.getopt(sys.argv[1:],'dv')
    display = 0
    verbose = 0
    if args:
        size = int(args[0])
    else:
        size = 6
    for o,v in opts:
        if o == '-d':
            display = 1
        elif o == '-v':
            verbose += 2
    count = 0
    sol = knight_tour(size,verbose)
    if display:
        print 'Solution found:'
        draw_solution(sol,size)
