"""Validation testing for constraint propagation module"""

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

from logilab.common.testlib import TestCase

from logilab.constraint import *
from logilab.constraint.distributors import EnumeratorDistributor

import os, sys
from cStringIO import StringIO

class Queens8_TC(TestCase):
    size = 8
    nb_sols = 92
    verbose=0
    def setUp(self):
        variables = []
        domains = {}
        constraints = []
        for i in range(self.size):
            name = 'Q%d'%i
            variables.append(name)
            domains[name] = fd.FiniteDomain([(i,j) for j in range(self.size)])

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
        self.repo = Repository(variables,domains,constraints)
        sys.stdout = StringIO()
    
    def tearDown(self):
        sys.stdout = sys.__stdout__

    def testQueensWithEnumerator(self):
        self.skip("to long")
        solver = Solver(EnumeratorDistributor())
        solutions = solver.solve(self.repo, verbose=self.verbose)
        self.assertEqual(len(solutions), self.nb_sols)

    def testQueensWithDefaultDistributor(self):
        self.skip("to long")
        solver = Solver()
        solutions = solver.solve(self.repo, verbose=self.verbose)
        self.assertEqual(len(solutions), self.nb_sols)


    
class Queens4_TC(Queens8_TC):
    size=4
    nb_sols=2

class Queens5_TC(Queens8_TC):
    size=5
    nb_sols=10

class Queens6_TC(Queens8_TC):
    size=6
    nb_sols=4

class Queens7_TC(Queens8_TC):
    size=7
    nb_sols=40

class Queens6Verbose_TC(Queens6_TC):
    verbose = 3


# remove if we are running with pylint, 'cos this gets too long without psyco
if os.environ.get('PYLINT_IMPORT') != '1':
    class Queens9_TC(Queens8_TC):
        size=9
        nb_sols=352

    class Queens10_TC(Queens8_TC):
        size=10
        nb_sols=724

