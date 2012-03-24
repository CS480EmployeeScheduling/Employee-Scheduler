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

from logilab.constraint.propagation import *
from logilab.constraint import fd


def queens(size=8,verbose=0):
    possible_positions = [(i,j) for i in range(size) for j in range(size)]
    variables = []
    domains = {}
    constraints = []
    for i in range(size):
        name = 'Q%d'%i
        variables.append(name)
        domains[name] = fd.FiniteDomain(possible_positions)
    for q1 in variables:
        for q2 in variables:
            if q1 < q2:
                constraints.append(fd.make_expression((q1,q2),
                                                      '%(q1)s[0] < %(q2)s[0] and '
                                                      '%(q1)s[1] != %(q2)s[1] and '
                                                      'abs(%(q1)s[0]-%(q2)s[0]) != '
                                                      'abs(%(q1)s[1]-%(q2)s[1])'%\
                                                      {'q1':q1,'q2':q2}))
    r = Repository(variables,domains,constraints)
    s = Solver().solve(r,verbose)
    print 'Number of solutions:',len(s)

if __name__ == '__main__':
    import profile
    profile.run('queens()','csp.prof')
    import pstats

    p = pstats.Stats('csp.prof')
    p.sort_stats('time','calls').print_stats(.25)
    p.sort_stats('cum','calls').print_stats(.25)
    p.strip_dirs().sort_stats('cum','calls').print_callers(.25)
    p.strip_dirs().sort_stats('cum','calls').print_callees()
