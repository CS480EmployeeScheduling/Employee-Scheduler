"""Unit testing for constraint propagation module"""

# (c) 2005 LOGILAB S.A. (Paris, FRANCE).
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
from logilab.constraint.fi import *
from logilab.constraint import Repository, Solver

class FiniteIntervalTC(unittest.TestCase):

    def setUp(self):
        self.dom1 = FiniteIntervalDomain(0, 10, 2, 4, 1)
        self.dom2 = FiniteIntervalDomain(2, 5, 3)
        self.dom3 = FiniteIntervalDomain(2, 6, 2, 3, .5)

    def testConstructorExceptions(self):
        try:
            d = FiniteIntervalDomain(5,1,3)
            self.fail("Should have an assertion error here")
        except AssertionError:
            pass
        try:
            d = FiniteIntervalDomain(1,5,3,1)
            self.fail("Should have an assertion error here")
        except AssertionError:
            pass
        try:
            d = FiniteIntervalDomain(1,3,-2)
            self.fail("Should have an assertion error here")
        except AssertionError:
            pass
        try:
            d = FiniteIntervalDomain(1,3,5)
            self.fail("Should have an assertion error here")
        except AssertionError:
            pass

    def test_ConstructorDefaults(self):
        d = FiniteIntervalDomain(1,3,2)
        self.assertEquals(d._max_length, 2)
        self.assertEquals(d._resolution, 1)

    def test_ConstructorAjustMaxLength(self):
        d = FiniteIntervalDomain(0, 5, 2, 8)
        self.assertEquals(d._max_length, 5)

    def test_getValues(self):
        self.assertEquals(len(self.dom1.getValues()), self.dom1.size())
        self.assertEquals(len(self.dom2.getValues()), self.dom2.size())
        self.assertEquals(len(self.dom3.getValues()), self.dom3.size())

    def test_Size(self):
        self.assertEquals(self.dom1.size(), 9 + 8 + 7)
        self.assertEquals(self.dom2.size(), 1)
        self.assertEquals(self.dom3.size(), 12)

    def test_overlap(self):
        self.failUnless(self.dom1.overlap(self.dom2))
        self.failUnless(self.dom1.overlap(FiniteIntervalDomain(-5,  5, 1)))
        self.failUnless(self.dom1.overlap(FiniteIntervalDomain( 5, 15, 1)))
        self.failUnless(self.dom1.overlap(FiniteIntervalDomain(-5, 15, 1)))
        self.failIf(self.dom1.overlap(FiniteIntervalDomain(-15, 0, 1)))
        self.failIf(self.dom1.overlap(FiniteIntervalDomain(10, 25, 1)))

    def test_SetLow(self):
        self.dom1.setLowestMin(2)
        self.assertEquals(self.dom1.lowestMin, 2)
        self.assertRaises(ConsistencyFailure, self.dom1.setLowestMin, 10)
        
    def test_SetHigh(self):
        self.dom1.setHighestMax(9)
        self.assertEquals(self.dom1.highestMax, 9)
        self.assertRaises(ConsistencyFailure, self.dom1.setHighestMax, -10)

    def test_SetMinLength(self):
        self.dom1.setMinLength(3)
        self.assertEquals(self.dom1._min_length, 3)
        self.dom1.setMinLength(4)
        self.assertEquals(self.dom1._min_length, 4)
        self.assertRaises(ConsistencyFailure, self.dom2.setMinLength, 5)

    def test_SetMaxLength(self):
        self.dom1.setMaxLength(3)
        self.assertEquals(self.dom1._max_length, 3)
        self.dom1.setMaxLength(2)
        self.assertEquals(self.dom1._max_length, 2)
        self.assertRaises(ConsistencyFailure, self.dom2.setMaxLength, 1)

    def test_FailureIfSizeEqualsZero(self):
        self.assertRaises(ConsistencyFailure, self.dom2.setHighestMax, 4)

    def test_LatestStart(self):
        self.assertEquals(self.dom1.highestMin, 8)
        self.assertEquals(self.dom2.highestMin, 2)
        self.assertEquals(self.dom3.highestMin, 4)
        
    def test_EarliestEnd(self):
        self.assertEquals(self.dom1.lowestMax, 2)
        self.assertEquals(self.dom2.lowestMax, 5)
        self.assertEquals(self.dom3.lowestMax, 4)

# FIXME check all possible cases are handled
class ConstraintOverlapTC(unittest.TestCase):
    def setUp(self):
        self.d1 = FiniteIntervalDomain(0, 5, 2)
        self.d2 = FiniteIntervalDomain(0, 5, 3)
        self.d3 = FiniteIntervalDomain(1, 5, 3)
        self.d4 = FiniteIntervalDomain(0, 4, 2)
        self.d5 = FiniteIntervalDomain(1, 4, 2)
        self.d6 = FiniteIntervalDomain(4, 7, 2)
        self.d7 = FiniteIntervalDomain(0, 5, 4)
        self.d8 = FiniteIntervalDomain(3, 8, 4)
        self.d9 = FiniteIntervalDomain(3, 8, 1)
        self.d10 = FiniteIntervalDomain(0, 6, 2)
        self.d11 = FiniteIntervalDomain(1, 5, 2)
        self.d12 = FiniteIntervalDomain(0, 6, 3)
        self.d13 = FiniteIntervalDomain(1, 6, 3)
        self.d14 = FiniteIntervalDomain(0, 6, 3)
        self.d15 = FiniteIntervalDomain(0, 2, 2)
        self.d16 = FiniteIntervalDomain(0, 2, 2)
        self.domains = {'v1': self.d1,
                        'v2': self.d2,
                        'v3': self.d3,
                        'v4': self.d4,
                        'v5': self.d5,
                        'v6': self.d6,
                        'v7': self.d7,
                        'v8': self.d8,
                        'v9': self.d9,
                        'v10': self.d10,
                        'v11': self.d11,
                        'v12': self.d12,
                        'v13': self.d13,
                        'v14': self.d14,
                        'v15': self.d15,
                        'v16': self.d16,
                        }

    # consistency failure
    
    def test_NoOverlap_ConsistencyFailure(self):
        c = NoOverlap('v2', 'v3')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)
        c = NoOverlap('v3', 'v2')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)

    def test_NoOverlap_ConsistencyFailure1(self):
        c = NoOverlap('v5', 'v2')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)
        c = NoOverlap('v2', 'v5')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)

    def test_NoOverlap_ConsistencyFailure2(self):
        c = NoOverlap('v15', 'v16')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)
        c = NoOverlap('v16', 'v15')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)

    # entailed
    
    def test_NoOverlap_Entailed(self):
        c = NoOverlap('v6', 'v4')
        self.assertEquals(c.narrow(self.domains), 1)
        c = NoOverlap('v4', 'v6')
        self.assertEquals(c.narrow(self.domains), 1)

    def test_NoOverlap_Entailed1(self):
        c = NoOverlap('v1', 'v3')
        self.assertEquals(c.narrow(self.domains), 1)
        c = NoOverlap('v3', 'v1')
        self.assertEquals(c.narrow(self.domains), 1)
        
    def test_NoOverlap_Entailed2(self):
        c = NoOverlap('v7', 'v8')
        self.assertEquals(c.narrow(self.domains), 1)
        self.assertEquals(self.d7, FiniteIntervalDomain(0,4,4))
        self.assertEquals(self.d8, FiniteIntervalDomain(4,8,4))
        
    def test_NoOverlap_Entailed2bis(self):
        c = NoOverlap('v8', 'v7')
        self.assertEquals(c.narrow(self.domains), 1)
        self.assertEquals(self.d7, FiniteIntervalDomain(0,4,4))
        self.assertEquals(self.d8, FiniteIntervalDomain(4,8,4))

    def test_NoOverlap_Entailed3(self):
        c = NoOverlap('v7', 'v10')
        self.assertEquals(c.narrow(self.domains), 1)
        self.assertEquals(self.d7, FiniteIntervalDomain(0,4,4))
        self.assertEquals(self.d10, FiniteIntervalDomain(4,6,2))

    def test_NoOverlap_Entailed3bis(self):
        c = NoOverlap('v10', 'v7')
        self.assertEquals(c.narrow(self.domains), 1)
        self.assertEquals(self.d7, FiniteIntervalDomain(0,4,4))
        self.assertEquals(self.d10, FiniteIntervalDomain(4,6,2))

    def test_NoOverlap_Entailed4(self):
        c = NoOverlap('v12', 'v13')
        self.assertEquals(c.narrow(self.domains), 1)
        self.assertEquals(self.d12, FiniteIntervalDomain(0,3,3))
        self.assertEquals(self.d13, FiniteIntervalDomain(3,6,3))

    def test_NoOverlap_Entailed4bis(self):
        c = NoOverlap('v13', 'v12')
        self.assertEquals(c.narrow(self.domains), 1)
        self.assertEquals(self.d12, FiniteIntervalDomain(0,3,3))
        self.assertEquals(self.d13, FiniteIntervalDomain(3,6,3))

    # not entailed
    
    def test_NoOverlap_NotEntailed(self):
        c = NoOverlap('v4', 'v1')
        self.assertEquals(c.narrow(self.domains), 0)

    def test_NoOverlap_NotEntailed2(self):
        c = NoOverlap('v8', 'v9')
        self.assertEquals(c.narrow(self.domains), 0)
        c = NoOverlap('v9', 'v8')
        self.assertEquals(c.narrow(self.domains), 0)

    def test_NoOverlap_NotEntailed3(self):
        c = NoOverlap('v11', 'v12')
        self.assertEquals(c.narrow(self.domains), 0)
        c = NoOverlap('v12', 'v11')
        self.assertEquals(c.narrow(self.domains), 0)

    def test_NoOverlap_NotEntailed4(self):
        c = NoOverlap('v12', 'v14')
        self.assertEquals(c.narrow(self.domains), 0)
        c = NoOverlap('v14', 'v12')
        self.assertEquals(c.narrow(self.domains), 0)


    def test_equality(self):
        c1 = NoOverlap('v12', 'v14')
        c2 = NoOverlap('v14', 'v12')
        c3 = NoOverlap('v15', 'v12')
        self.assertEquals(c1, c2)
        self.assertNotEquals(c1, c3)
        self.assertNotEquals(c2, c3)
        self.assertEquals(c3, c3)

    def test_hash(self):
        c1 = NoOverlap('v12', 'v14')
        c2 = NoOverlap('v14', 'v12')
        c3 = NoOverlap('v15', 'v12')
        d = {c1 : 'hello', c2 : 'hello', c3 : 'hello'}
        self.assertEquals(len(d), 2)
        

class ConstraintTC(unittest.TestCase):
    def setUp(self):
        self.d1 = FiniteIntervalDomain(5, 10, 1, 1)
        self.d2 = FiniteIntervalDomain(2,  7, 1, 1)
        self.d3 = FiniteIntervalDomain(8, 10, 1, 1)
        self.d4 = FiniteIntervalDomain(3, 10, 5, 6)
        self.d5 = FiniteIntervalDomain(4, 10, 5)
        self.d6 = FiniteIntervalDomain(0, 3, 2)
        self.d7 = FiniteIntervalDomain(0, 5, 4)
        self.d8 = FiniteIntervalDomain(3, 8, 4)
        self.d9 = FiniteIntervalDomain(3, 8, 1)
        self.d10 = FiniteIntervalDomain(0, 6, 2)
        self.domains = {'v1': self.d1,
                        'v2': self.d2,
                        'v3': self.d3,
                        'v4': self.d4,
                        'v5': self.d5,
                        'v6': self.d6,
                        'v7': self.d7,
                        'v8': self.d8,
                        'v9': self.d9,
                        'v10': self.d10,
                        }
    ##
    ## StartsBeforeStart
    ##
    def test_StartsBeforeStart_NotEntailed(self):
        c = StartsBeforeStart('v2','v1')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)

    def test_StartsBeforeStart_ConsistencyFailure(self):
        c = StartsBeforeStart('v3','v2')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)

    def test_StartsBeforeStart_Entailed(self):
        c = StartsBeforeStart('v2','v3')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 1)
        
    ##
    ## StartsBeforeEnd
    ##
    def test_StartsBeforeEnd_NotEntailed(self):
        c = StartsBeforeEnd('v2','v1')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)
        
    def test_StartsBeforeEnd_ConsistencyFailure(self):
        c = StartsBeforeEnd('v3','v2')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)
        
    def test_StartsBeforeEnd_Entailed(self):
        c = StartsBeforeEnd('v4', 'v1')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 1)
        
    ##
    ## EndsBeforeStart
    ##
    def test_EndsBeforeStart_Entailed(self):
        c = EndsBeforeStart('v2','v3')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 1)
        
    def test_EndsBeforeStart_NotEntailed(self):
        c = EndsBeforeStart('v3','v1')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)
        
    def test_EndsBeforeStart_NotEntailed_withRemoval(self):
        c = EndsBeforeStart('v1','v3')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)
        self.assertEquals(self.d1.highestMax, self.d3.highestMin)
        
    def test_EndsBeforeStart_ConsistencyFailure(self):
        c = EndsBeforeStart('v3','v2')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)
        
    ##
    ## EndsBeforeEnd
    ##
    def test_EndsBeforeEnd_Entailed(self):
        c = EndsBeforeEnd('v2','v3')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 1)
        
    def test_EndsBeforeEnd_NotEntailed(self):
        c = EndsBeforeEnd('v2','v1')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)
        self.assertEquals(self.d2.highestMax, 7)

    def test_EndsBeforeEnd_NotEntailed_withRemoval(self):
        c = EndsBeforeEnd('v1','v2')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)
        self.assertEquals(self.d1.highestMax, self.d2.highestMax)

    def test_EndsBeforeEnd_ConsistencyFailure(self):
        c = EndsBeforeEnd('v3','v2')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)

    ##
    ## StartsAfterStart
    ##
    def test_StartsAfterStart_Entailed(self):
        c = StartsAfterStart('v3','v2')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 1)

    def test_StartsAfterStart_NotEntailed(self):
        c = StartsAfterStart('v1','v2')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)
        self.assertEquals(self.d1.lowestMin, 5)

    def test_StartsAfterStart_NotEntailed_withRemoval(self):
        c = StartsAfterStart('v2','v1')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)
        self.assertEquals(self.d2.lowestMin, self.d1.lowestMin)

    def test_StartsAfterStart_ConsistencyFailure(self):
        c = StartsAfterStart('v2','v3')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)
        
    ##
    ## StartsAfterEnd
    ##
    def test_StartsAfterEnd_Entailed(self):
        c = StartsAfterEnd('v3','v2')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 1)

    def test_StartsAfterEnd_NotEntailed_withRemoval(self):
        c = StartsAfterEnd('v1','v4')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)
        self.assertEquals(self.d1.lowestMin, self.d4.lowestMax)

    def test_StartsAfterEnd_ConsistencyFailure(self):
        c = StartsAfterEnd('v2','v3')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)
        
    ##
    ## EndsAfterStart
    ##
    def test_EndsAfterStart_Entailed(self):
        c = EndsAfterStart('v4','v2')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 1)
        
    def test_EndsAfterStart_NotEntailed(self):
        c = EndsAfterStart('v4','v3')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)

    def test_EndsAfterStart_ConsistencyFailure(self):
        c = EndsAfterStart('v2','v3')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)
        

    ##
    ## EndsAfterEnd
    ##
    def test_EndsAfterEnd_Entailed(self):
        c = EndsAfterEnd('v4','v2')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 1)

    def test_EndsAfterEnd_NotEntailed(self):
        c = EndsAfterEnd('v4','v3')
        ret = c.narrow(self.domains)
        self.assertEquals(ret, 0)
        
    def test_EndsAfterEnd_ConsistencyFailure(self):
        c = EndsAfterEnd('v2','v3')
        self.assertRaises(ConsistencyFailure, c.narrow, self.domains)

        
class DistributorTC(unittest.TestCase):
    def setUp(self):
        self.d = FiniteIntervalDistributor()

    def test_DistributeDifferentLengths(self):
        d1 = FiniteIntervalDomain(0, 5, 3, 5)
        d2 = FiniteIntervalDomain(0, 20, 1)
        domains = {'v1': d1,
                   'v2': d2,
                   }
        dom1, dom2 = self.d.distribute(domains)
        self.failUnless(dom1['v2'] == dom2['v2'])
        self.failUnless(dom1['v2'] == d2)
        self.failIf(dom1['v1'] == d1)
        self.failIf(dom2['v1'] == d1)
        self.assertEquals(dom1['v1']._max_length, d1._min_length)
        self.assertEquals(dom2["v1"]._min_length, d1._min_length+d1._resolution)
        self.assertEquals(d1.size(), dom1['v1'].size() + dom2['v1'].size())

    def test_DistributeSameLengths(self):
        d1 = FiniteIntervalDomain(lowestMin=0, highestMax=5,  min_length=4)
        d2 = FiniteIntervalDomain(lowestMin=0, highestMax=20, min_length=1)
        domains = {'v1': d1,
                   'v2': d2,
                   }
        dom1, dom2 = self.d.distribute(domains)
        self.failUnless(dom1['v2'] == dom2['v2'])
        self.failUnless(dom1['v2'] == d2)
        self.failIf(dom1['v1'] == d1)
        self.failIf(dom2['v1'] == d1)
        self.assertEquals(dom1['v1'].size(), 1)
        self.assertEquals(dom1["v1"].highestMax, d1._min_length + d1.lowestMin)
        self.assertEquals(dom2["v1"].lowestMin, d1._resolution + d1.lowestMin)
        self.assertEquals(d1.size(), dom1['v1'].size() + dom2['v1'].size())
        

class PlannerTC(unittest.TestCase):
    def setUp(self):
        self.d = FiniteIntervalDistributor()
        self.verbose = 1
        
    def solve_repo1(self, constraints):
        dom1 = FiniteIntervalDomain(0, 15, 5)
        dom2 = FiniteIntervalDomain(0, 15, 5)
        dom3 = FiniteIntervalDomain(0, 15, 5)
        repo = Repository( ['A','B','C'], { 'A': dom1,
                                            'B': dom2,
                                            'C': dom3 },
                           constraints )
        s = Solver( self.d )
        answers = list(s.solve_all(repo,verbose=self.verbose))
        self.assertEquals(len(answers), 2)
        import pprint
        pprint.pprint( list(answers) )

    def test_pb1(self):
        constraints = [ StartsAfterEnd('B','A'),
                        StartsAfterEnd('C','A'),
                        NoOverlap('B','C' ) ]
        self.solve_repo1( constraints )

    def test_pb2(self):
        constraints = [ EndsBeforeStart('A','B'),
                        EndsBeforeStart('A','C'),
                        NoOverlap('B','C' ) ]
        self.solve_repo1( constraints )


    def solve_repo2(self, constraints):
        dom1 = FiniteIntervalDomain(0, 20, 5)
        dom2 = FiniteIntervalDomain(0, 20, 5)
        dom3 = FiniteIntervalDomain(0, 20, 10)
        dom4 = FiniteIntervalDomain(0, 20, 5)
        repo = Repository( ['A','B','C', 'D'], { 'A': dom1,
                                                 'B': dom2,
                                                 'C': dom3,
                                                 'D': dom4 },
                           constraints )
        s = Solver( self.d )
        answers = list(s.solve_all(repo,verbose=1))
        import pprint
        pprint.pprint( list(answers) )

    def test_pb3(self):
        constraints = [ StartsAfterEnd('B','A'),
                        StartsAfterEnd('C','A'),
                        StartsAfterEnd('D','B'),
                        StartsAfterEnd('D','C'),
                        ]
        self.solve_repo2( constraints )

    def test_pb4(self):
        constraints = [ StartsAfterEnd('B','A'),
                        StartsAfterEnd('C','A'),
                        StartsAfterEnd('D','B'),
                        StartsAfterEnd('D','C'),
                        StartsAfterEnd('D','A'),
                        ]
        self.solve_repo2( constraints )


if __name__ == '__main__':
    unittest.main()
