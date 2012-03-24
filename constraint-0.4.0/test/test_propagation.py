"""Unit testing for constraint propagation module"""

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

import unittest
import os
from logilab.constraint.propagation import *
from logilab.constraint import fd
from logilab.constraint.distributors import DefaultDistributor

class Repository_TC(unittest.TestCase):
    def setUp(self):
        self.domains = {}
        self.variables = list('abcdef')
        for v in self.variables:
            self.domains[v] = fd.FiniteDomain(range(6))

        self.repo = Repository(self.variables, self.domains)

    def testVCGDraw(self):
        for v1 in self.variables:
            for v2 in self.variables:
                if v1 < v2:
                    self.repo.addConstraint(fd.make_expression((v1, v2),
                                                           '%s < %s'%(v1, v2)))
        try:
            try:
                self.repo.vcg_draw('toto.vcg')
            except IOError, exc:
                self.fail('This test cannot run in the testing environment'
                          'because I cannot write the file.\n'
                          'The error message was: \n%s' % exc)
        finally:
            os.unlink('toto.vcg')

        
        
    def testGetDomains(self):
        doms = self.repo.getDomains()
        self.assertEqual(doms, self.domains)

    def testDistribute(self):
        d = []
        for distributed in self.repo.distribute(DefaultDistributor()):
            d.append(distributed)
        self.assertEqual(len(d),2)

    def testConsistencyNoConstraint(self):
        self.repo.consistency()
        for v, dom in self.repo.getDomains().items():
            self.assertEqual(dom.size(),6)

    def testConsistency(self):
        for v1 in self.variables:
            for v2 in self.variables:
                if v1 < v2:
                    self.repo.addConstraint(fd.make_expression((v1, v2),
                                                           '%s < %s'%(v1, v2)))

        self.repo.consistency()
        for v, dom in self.repo.getDomains().items():
            self.assertEqual(dom.size(),1)

    def testInconsistency(self):
        self.repo.addConstraint(fd.make_expression(('a', 'b'),
                                                   'a < b'))
        self.repo.addConstraint(fd.make_expression(('a', 'b'),
                                                   'a > b'))

        try:
            self.repo.consistency()
            self.fail('No ConsistencyFailure raised')
        except ConsistencyFailure:
            pass


class Sover_TC(unittest.TestCase):
    def setUp(self):
        self.solver = Solver()
        self.domains = {}
        self.variables = list('abcdef')
        for v in self.variables:
            self.domains[v] = fd.FiniteDomain(range(6))

        self.repo = Repository(self.variables, self.domains)
        for v1 in self.variables:
            for v2 in self.variables:
                if v1 < v2:
                    self.repo.addConstraint(fd.make_expression((v1, v2),
                                                               '%s < %s'%(v1, v2)))


    def testSolveOne(self):
        solution = self.solver.solve_one(self.repo)
        self.assertEqual(solution,{'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5})

    def testSolve(self):
        solutions = self.solver.solve(self.repo)
        self.assertEqual(solutions,
                         [{'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5}])

    def testSolveAll(self):
        solutions = []
        for s in self.solver.solve_all(self.repo):
            solutions.append(s)
        self.assertEqual(solutions,
                         [{'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5}])

    def testNolutionSolve(self):
        self.repo.addConstraint(fd.make_expression(('a', 'b'),
                                                   'b < a'))

        solutions = self.solver.solve(self.repo)
        self.assertEqual(solutions,
                         [])


class SolverBest_TC(unittest.TestCase):
    def setUp(self):
        self.solver = Solver()
        self.domains = {}
        self.variables = list('abc')
        for v in self.variables:
            self.domains[v] = fd.FiniteDomain(range(6))

        self.repo = Repository(self.variables, self.domains)
        for v1 in self.variables:
            for v2 in self.variables:
                if v1 < v2:
                    self.repo.addConstraint(fd.make_expression((v1, v2),
                                                               '%s < %s'%(v1, v2)))

    def costFunc(self, a,b,c):
        return -(a*a+b*b+c*c)
    
    def testSolveBest(self):
        solutions = []
        for s in self.solver.solve_best(self.repo, self.costFunc):
            solutions.append(s)

        costs = [self.costFunc(**sol[0]) for sol in solutions]
        sorted_costs = costs[:]
        sorted_costs.sort()
        sorted_costs.reverse()
        self.assertEquals(costs, sorted_costs)
        self.assertEquals(costs, [s[1] for s in solutions])

                         

if __name__ == '__main__':
    unittest.main()
