#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
"""N queens problem
The problem is solved with a EnumeratorDistributor splitting
the smallest domain in at most N subdomains."""

# (c) 2000-2001 LOGILAB S.A. (Paris, FRANCE).
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


from __future__ import generators

from logilab.constraint import *
from logilab.constraint.distributors import *

def rooks(size=8,verbose=0):
    variables = []
    domains = {}
    constraints = []
    for i in range(size):
        name = 'R%02d'%i
        variables.append(name)
        domains[name] = fd.FiniteDomain( range(size) )

    for r1 in range(size):
        for r2 in range(size):
            q1 = 'R%02d' % r1
            q2 = 'R%02d' % r2
            if r1 < r2:
                D = {'q1':q1,'q2':q2, 'r1' : r1, 'r2' : r2 }
                c = fd.make_expression((q1,q2), '%(q1)s != %(q2)s' % D )
                constraints.append(c)
                
    r = Repository(variables,domains,constraints)
    for sol in Solver(EnumeratorDistributor()).solve_all(r,verbose):
        yield sol



def draw_solution(s):
    size = len(s)
    board = ''
    queens = s.items()
    queens.sort()
    board += '_'*(size*2+1)+'\n'
    for i in range(size):
        qj = queens[i][1]
        for j in range(size):
            if j != qj:
                board+='|'+'�-'[(i+j)%2]
            else:
                board+='|R'
        board+='|\n'
    board += '�'*(size*2+1)
    print board


def main(args = None):
    import sys,getopt
    if args is None:
        args = sys.argv[1:]
    opts,args = getopt.getopt(args,'dvf')
    display = 0
    verbose = 0
    first = 0
    if args:
        size = int(args[0])
    else:
        size = 8
    for o,v in opts:
        if o == '-d':
            display = 1
        elif o == '-v':
            verbose += 1
        elif o == "-f":
            first = 1
    count = 0
    for sol in rooks(size,verbose):
        count += 1
        if display:
            print 'solution #%d'%count
            draw_solution(sol)
            print '*'*80
        if first:
            break
    if not display:
        print 'Use -d option to display solutions'
    print count,'solutions found.'

if __name__ == '__main__':
##     import hotshot
##     p = hotshot.Profile('/tmp/queens.prof')
##     p.runcall(main)
##     p.close()
    main()
