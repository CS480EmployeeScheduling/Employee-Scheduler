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


distributors = {
    "enum" : EnumeratorDistributor,
    "dicho" : DichotomyDistributor,
    "naive" : NaiveDistributor,
    }

def queens(size=8,verbose=0,distrib="enum"):
    variables = []
    domains = {}
    constraints = []
    for i in range(size):
        name = 'Q%02d'%i
        variables.append(name)
        domains[name] = fd.FiniteDomain([(i,j) for j in range(size)])

    for q1 in variables:
        for q2 in variables:
            if q1 < q2:
                c = fd.make_expression((q1,q2),
                                       '%(q1)s[0] < %(q2)s[0] and '
                                       '%(q1)s[1] != %(q2)s[1] and '
                                       'abs(%(q1)s[0]-%(q2)s[0]) != '
                                       'abs(%(q1)s[1]-%(q2)s[1])'%\
                                       {'q1':q1,'q2':q2})
                constraints.append(c)
    r = Repository(variables,domains,constraints)
    Distrib = distributors[distrib]
    for sol in Solver(Distrib()).solve_all(r,verbose):
        yield sol



def draw_solution(s):
    size = len(s)
    queens = {}
    board = ''
    for q,p in s.items():
        queens[p]=q
    board += '_'*(size*2+1)+'\n'
    for i in range(size):
        #
        for j in range(size):
            q = queens.get((i,j))
            if q is None:
                board+='|'+'·-'[(i+j)%2]
            else:
                board+='|Q'
        board+='|\n'
    board += '¯'*(size*2+1)
    print board


def main(args = None):
    import sys,getopt
    if args is None:
        args = sys.argv[1:]
    opts,args = getopt.getopt(args,'dvfD:')
    display = 0
    verbose = 0
    first = 0
    distrib = "enum"
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
        elif o == "-D":
            if v in distributors:
                distrib = v
            else:
                raise RuntimeError("Distributor must be one of %s" % ", ".join(distributors.keys()) )
        
    count = 0
    for sol in queens(size,verbose,distrib):
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
