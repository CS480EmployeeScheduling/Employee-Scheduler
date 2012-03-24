"""
Solve a puzzle that got discussed on c.l.p. on october 2002

ABC*DE=FGHIJ with all letters different and in domain [0,9]
"""
from __future__ import generators

from logilab.constraint import *
from logilab.constraint.psyco_wrapper import psyobj
from logilab.constraint.propagation import BasicConstraint, ConsistencyFailure

class DistinctDigits(BasicConstraint,psyobj):
    def __init__(self,variable):
        BasicConstraint.__init__(self,variable,None,None)

    def narrow(self,domains):
        domain = domains[self._variable]
        for v in domain.getValues():
            s = str(v)
            for d in ('0','1','2','3','4','5','6','7','8','9'):
                if s.count(d) not in (0,1):
                    domain.removeValue(v)
                    break
        return 1

    def __repr__(self):
        
        return '<DistinctDigits on variable %s>'%self._variable


def menza() :
    """
    """

    VARS='ab'
    variables = list(VARS)
    domains = {}
    constraints = []

    domains['a'] = fd.FiniteDomain(range(0,1000))
    domains['b'] = fd.FiniteDomain(range(0,100))
    
    me = fd.make_expression

    for v in variables:
        constraints.append(DistinctDigits(v))
    dist = ['10000 < a*b ']
    for digit in range(10):
        dist.append('("%%.3d%%.2d%%.5d" %% (a,b,a*b)).count("%d")==1'%digit)
    constraints.append(me(('a','b'),' and '.join(dist)))
    r = Repository(variables, domains, constraints)
    return r

if __name__ == '__main__' :
    import sys,getopt
    opts,args = getopt.getopt(sys.argv[1:],'dv')
    verbose = 0
    display = 0
    create_problem=menza
    for o,v in opts:
        if o == '-v':
            verbose += 1
        elif o == '-d':
            display = 1

    
    r = create_problem()
    print 'problem created. let us solve it.'
    s = []
    for sol in Solver().solve_all(r,verbose):
        s.append(sol)
        if display:
            sol['c'] = sol['a']*sol['b']
            print "%(a)s x %(b)s = %(c)s" % sol
    if not display:
        print 'Found %d solutions'%len(s)
