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
from logilab.constraint import fd
from logilab.constraint import propagation
from logilab.constraint import distributors


class AbstractConstraintTC(unittest.TestCase):
    """override the following methods:
     * setUp to initialize variables
     * narrowingAssertions to check that narrowing was ok
     """
    def setUp(self):
        self.relevant_variables = []
        self.irrelevant_variable = 'tagada'
        self.constraint = None #AbstractConstraint(self.relevant_variables)
        self.domains = {}
        self.entailed_domains = {}
        #raise NotImplementedError

    def testRelevance(self):
        """tests that relevant variables are relevant"""
        for v in self.relevant_variables:
            self.assert_(self.constraint.isVariableRelevant(v))
        self.failIf(self.constraint.isVariableRelevant(self.irrelevant_variable))
        

    def testNarrowing(self):
        """tests that narrowing is performed correctly"""
        entailed = self.constraint.narrow(self.domains)
        self.narrowingAssertions()
        
    def testEntailment(self):
        """tests that narrowing is performed correctly"""
        entailed = self.constraint.narrow(self.entailed_domains)
        self.assert_(entailed)

class AllDistinctTC(AbstractConstraintTC):
    def setUp(self):
        self.relevant_variables = ['x','y','z']
        self.irrelevant_variable = 'tagada'
        self.constraint = fd.AllDistinct(self.relevant_variables)
        self.domains = {'x':fd.FiniteDomain((1,2)),
                        'y':fd.FiniteDomain((1,3)),
                        'z':fd.FiniteDomain((1,4)),}
        
        self.entailed_domains = {'x':fd.FiniteDomain((1,)),
                                 'y':fd.FiniteDomain((1,2)),
                                 'z':fd.FiniteDomain((1,2,3)),}

    def narrowingAssertions(self):
        vx = self.domains['x'].getValues()
        vy = self.domains['y'].getValues()
        vz = self.domains['z'].getValues()
        self.assert_( 1 in vx and 2 in vx)
        self.assert_( 1 in vy and 3 in vy)
        self.assert_( 1 in vz and 4 in vz)

    def testNarrowing2(self):
        domains = {'x':fd.FiniteDomain((1,2)),
                   'y':fd.FiniteDomain((1,)),
                   'z':fd.FiniteDomain((1,4)),}
        entailed = self.constraint.narrow(domains)
        vx = domains['x'].getValues()
        vy = domains['y'].getValues()
        vz = domains['z'].getValues()
        self.assert_(entailed)
        self.assert_(2 in vx)
        self.assert_(1 in vy)
        self.assert_(4 in vz)

    def testNarrowing3(self):
        domains = {'x':fd.FiniteDomain((1,)),
                   'y':fd.FiniteDomain((2,)),
                   'z':fd.FiniteDomain((1,2,3,4)),}
        entailed = self.constraint.narrow(domains)
        vx = domains['x'].getValues()
        vy = domains['y'].getValues()
        vz = domains['z'].getValues()
        self.assert_(not entailed)
        self.assert_(1 in vx, str(vx))
        self.assert_(2 in vy, str(vy))
        self.assert_(4 in vz and 3 in vz, str(vz))

    def testNarrowing4(self):
        domains = {'x':fd.FiniteDomain((1,)),
                   'y':fd.FiniteDomain((2,)),
                   'z':fd.FiniteDomain((1,3,4)),
                   't':fd.FiniteDomain((2,5,4)),
                   'u':fd.FiniteDomain((1,2,4)),
                   }
        constraint = fd.AllDistinct(domains.keys())
        entailed = constraint.narrow(domains)
        vx = domains['x'].getValues()
        vy = domains['y'].getValues()
        vz = domains['z'].getValues()
        vt = domains['t'].getValues()
        vu = domains['u'].getValues()
        self.failUnless(entailed)
        self.assertEquals([1],  vx)
        self.assertEquals([2], vy)
        self.assertEquals([3], vz)
        self.assertEquals([5], vt)
        self.assertEquals([4], vu)

    def testFailure1(self):
        domains = {'x':fd.FiniteDomain((1,2)),
                   'y':fd.FiniteDomain((2,1)),
                   'z':fd.FiniteDomain((1,2)),}
        exception = 0
        try:
            entailed = self.constraint.narrow(domains)
        except propagation.ConsistencyFailure:
            exception = 1
        assert exception

    def testFailure2(self):
        domains = {'x':fd.FiniteDomain((1,)),
                   'y':fd.FiniteDomain((2,)),
                   'z':fd.FiniteDomain((1,2)),}
        exception = 0
        try:
            entailed = self.constraint.narrow(domains)
        except propagation.ConsistencyFailure:
            exception = 1
        assert exception

    def testFailure3(self):
        domains = {'x':fd.FiniteDomain((1,)),
                   'y':fd.FiniteDomain((1,)),
                   'z':fd.FiniteDomain((2,3)),}
        exception = 0
        try:
            entailed = self.constraint.narrow(domains)
        except propagation.ConsistencyFailure:
            exception = 1
        assert exception


    
class UnaryMathConstrTC(AbstractConstraintTC):
    def setUp(self):
        self.relevant_variables = ['x']
        self.irrelevant_variable = 'tagada'
        self.constraint = fd.make_expression(self.relevant_variables,
                                             'x==2')
        self.domains = {'x':fd.FiniteDomain(range(4))}
        self.entailed_domains = {'x':fd.FiniteDomain([2])}
    def narrowingAssertions(self):
        v = list(self.domains['x'].getValues())
        v.sort()
        assert v == [2],str(v)

class BinaryMathConstrTC(AbstractConstraintTC):
    def setUp(self):
        self.relevant_variables = ['x','y']
        self.irrelevant_variable = 'tagada'
        self.constraint = fd.make_expression(self.relevant_variables,
                                             'x+y==2')
        self.domains = {'x':fd.FiniteDomain(range(4)),
                        'y':fd.FiniteDomain(range(2))}
        self.entailed_domains = {'x':fd.FiniteDomain([2]),
                                 'y':fd.FiniteDomain([0])}
    def narrowingAssertions(self):
        v = list(self.domains['x'].getValues())
        v.sort()
        assert v == [1,2],str(v)
        v = list(self.domains['y'].getValues())
        v.sort()
        assert v == [0,1],str(v)

class TernaryMathConstrTC(AbstractConstraintTC):
    def setUp(self):
        self.relevant_variables = ['x','y','z']
        self.irrelevant_variable = 'tagada'
        self.constraint = fd.make_expression(self.relevant_variables,
                                             'x+y==2 and z>1')
        self.domains = {'x':fd.FiniteDomain(range(4)),
                        'y':fd.FiniteDomain(range(3)),
                        'z':fd.FiniteDomain(range(4))}
        self.entailed_domains = {'x':fd.FiniteDomain([2]),
                                 'y':fd.FiniteDomain([0]),
                                 'z':fd.FiniteDomain([2,3]),}
        

    def narrowingAssertions(self):
        v = list(self.domains['x'].getValues())
        v.sort()
        assert v == [0,1,2],str(v)
        v = list(self.domains['y'].getValues())
        v.sort()
        assert v == [0,1,2],str(v)
        v = list(self.domains['z'].getValues())
        v.sort()
        assert v == [2,3],str(v)

class AbstractBasicConstraintTC(unittest.TestCase):
    """override the following methods:
     * setUp to initialize variables
     * narrowingAssertions to check that narrowing was ok
     """
    def setUp(self):
        self.constraint = None #AbstractConstraint(self.relevant_variables)
        self.domains = {}
        self.entailed_domains = {}
        #raise NotImplementedError

    def testRelevance(self):
        """tests that relevant variables are relevant"""
        assert self.constraint.isVariableRelevant('x')
        assert not self.constraint.isVariableRelevant('tagada')

    def testGetVariable(self):
        """test that getVariable returns the right variable"""
        assert self.constraint.getVariable() == 'x'
        
    def testNarrowing(self):
        """tests that narrowing is performed correctly"""
        entailed = self.constraint.narrow(self.domains)
        self.narrowingAssertions()
        
    def testEntailment(self):
        """tests that narrowing is performed correctly"""
        entailed = self.constraint.narrow(self.domains)
        assert entailed


class EqualsConstrTC(AbstractBasicConstraintTC):
    def setUp(self):
        self.constraint = fd.Equals('x',1)
        self.domains = {'x':fd.FiniteDomain(range(3))}

    def narrowingAssertions(self):
        v = list(self.domains['x'].getValues())
        v.sort()
        assert v == [1],str(v)

class NotEqualsConstrTC(AbstractBasicConstraintTC):
    def setUp(self):
        self.constraint = fd.NotEquals('x',1)
        self.domains = {'x':fd.FiniteDomain(range(3))}

    def narrowingAssertions(self):
        v = list(self.domains['x'].getValues())
        v.sort()
        assert v == [0,2],str(v)

class LesserThanConstrTC(AbstractBasicConstraintTC):
    def setUp(self):
        self.constraint = fd.LesserThan('x',1)
        self.domains = {'x':fd.FiniteDomain(range(3))}

    def narrowingAssertions(self):
        v = list(self.domains['x'].getValues())
        v.sort()
        assert v == [0],str(v)

class LesserOrEqualConstrTC(AbstractBasicConstraintTC):
    def setUp(self):
        self.constraint = fd.LesserOrEqual('x',1)
        self.domains = {'x':fd.FiniteDomain(range(3))}

    def narrowingAssertions(self):
        v = list(self.domains['x'].getValues())
        v.sort()
        assert v == [0,1],str(v)

class GreaterThanConstrTC(AbstractBasicConstraintTC):
    def setUp(self):
        self.constraint = fd.GreaterThan('x',1)
        self.domains = {'x':fd.FiniteDomain(range(3))}

    def narrowingAssertions(self):
        v = list(self.domains['x'].getValues())
        v.sort()
        assert v == [2],str(v)

class GreaterOrEqualConstrTC(AbstractBasicConstraintTC):
    def setUp(self):
        self.constraint = fd.GreaterOrEqual('x',1)
        self.domains = {'x':fd.FiniteDomain(range(3))}

    def narrowingAssertions(self):
        v = list(self.domains['x'].getValues())
        v.sort()
        assert v == [1,2],str(v)



def get_all_cases(module):
    import types
    all_cases = []
    for name in dir(module):
        obj = getattr(module, name)
        if type(obj) in (types.ClassType, types.TypeType) and \
               issubclass(obj, unittest.TestCase) and \
               not name.startswith('Abstract'):
            all_cases.append(obj)
    all_cases.sort()
    return all_cases

def suite(cases = None):
    import test_constraints
    cases = cases or get_all_cases(test_constraints)
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test'
    loader.sortTestMethodsUsing = None # disable sorting
    suites = [loader.loadTestsFromTestCase(tc) for tc in cases]
    return unittest.TestSuite(suites)
    

if __name__ == '__main__':
    unittest.main(defaultTest="suite")
