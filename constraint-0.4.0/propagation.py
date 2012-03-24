# (c) 2002 LOGILAB S.A. (Paris, FRANCE).
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
"""The code of the constraint propagation algorithms"""

from __future__ import generators
from operator import mul as MUL
from time import strftime
from logilab.constraint.interfaces import DomainInterface, ConstraintInterface
from logilab.constraint.psyco_wrapper import Psyobj
from logilab.common.compat import enumerate

def _default_printer(*msgs):
    for msg in msgs[:-1]:
        print msg,
    print msgs[-1]
class ConsistencyFailure(Exception):
    """The repository is not in a consistent state"""
    pass

class Repository(Psyobj):
    """Stores variables, domains and constraints
    Propagates domain changes to constraints
    Manages the constraint evaluation queue"""
    
    def __init__(self, variables, domains, constraints = None, printer=_default_printer):
        # encode unicode
        self._printer = printer
        
        for i, var in enumerate(variables):
            if type(var) == type(u''):
                variables[i] = var.encode()
                
        self._variables = variables   # list of variable names
        self._domains = domains    # maps variable name to domain object
        self._constraints = [] # list of constraint objects
#        self._queue = []       # queue of constraints waiting to be processed
        self._variableListeners = {}
        for var in self._variables:
            self._variableListeners[var] = []
            assert self._domains.has_key(var)
        for constr in constraints or ():
            self.addConstraint(constr)


    def display(self):
        self._printer( "VARIABLES")
        self._printer( "---------")
        for v in sorted(self._variables):
            self._printer( "%s = %s" % (v, self._domains[v]))
        self._printer( "CONSTRAINTS")
        self._printer( "-----------")
        for c in self._constraints:
            self._printer( c)

    def display_vars(self):
        self._printer( "%d constraints with:" % len(self._constraints))
        for v in sorted(self._variables):
            self._printer( "%15s = %s" % (v, self._domains[v]))
            
        
    def __repr__(self):
        return '<Repository nb_constraints=%d domains=%s>' % \
                               (len(self._constraints), self._domains)

    def vcg_draw(self, filename, title='Constraints graph'):
        """ draw a constraints graph readable by vcg
        """
        from logilab.common.vcgutils import VCGPrinter, EDGE_ATTRS
        stream = open(filename, 'w')
        printer = VCGPrinter(stream)        
        printer.open_graph(title=title, textcolor='black'
#                                layoutalgorithm='dfs',
#                               manhattan_edges='yes'
#                               port_sharing='no'
#                                late_edge_labels='yes'
                                )
        
        for var in self._variables:
            printer.node(var, shape='ellipse')

        type_colors = {}
        color_index = 2
        i = 0
        for constraint in self._constraints:
            key = constraint.type
            if not type_colors.has_key(key):
                type_colors[key] = color_index
                color_index += 1
            affected_vars = constraint.affectedVariables()
            if len(affected_vars) <= 1:
                continue
            if len(affected_vars) == 2:
                var1 = affected_vars[0]
                var2 = affected_vars[1]
                printer.edge(var1, var2, arrowstyle='none',
                             color=EDGE_ATTRS['color'][type_colors[key]])
                continue
            n_id = 'N_aire%i' % i
            i += 1
            printer.node(n_id, shape='triangle')
            for var1 in affected_vars:
                printer.edge(var1, n_id, arrowstyle='none',
                             color=EDGE_ATTRS['color'][type_colors[key]])
        # self._printer( legend)
        for node_type, color in type_colors.items():
            printer.node(node_type, shape='box',
                         color=EDGE_ATTRS['color'][color])
        printer.close_graph()
        stream.close()
        
    def addConstraint(self, constraint):
        if isinstance(constraint, BasicConstraint):
            # Basic constraints are processed just once
            # because they are straight away entailed
            var = constraint.getVariable()
            constraint.narrow({var: self._domains[var]})
        else:
            self._constraints.append(constraint)
            for var in constraint.affectedVariables():
                self._variableListeners[var].append(constraint)
        
    def _removeConstraint(self, constraint):
        self._constraints.remove(constraint)
        for var in constraint.affectedVariables():
            try:
                self._variableListeners[var].remove(constraint)
            except ValueError:
                raise ValueError('Error removing constraint from listener',
                                 var,
                                 self._variableListeners[var],
                                 constraint)

    def getDomains(self):
        return self._domains

    def distribute(self, distributor, verbose=0):
        """Create new repository using the distributor and self """
        for domains in distributor.distribute(self._domains, verbose):
            yield Repository(self._variables, domains, self._constraints) 

# alf 20041216 -- I tried the following to avoid the cost of the
# creation of new Repository objects. It resulted in functional, but
# slightly slower code. If you want to try to improve it, I keep the
# commented out version in the source, but the version above stays
# active as it is both simpler and faster.
##         backup_constraints = self._constraints[:]
##         for domains in distributor.distribute(self._domains, verbose):
##             self._domains = domains
##             self._constraints = []
##             self._queue = []
##             for var in self._variables:
##                 self._variableListeners[var] = []
##             for constraint in backup_constraints:
##                 self.addConstraint(constraint)
##             yield self
    
    def consistency(self, verbose=0, custom_printer=None):
        """Prunes the domains of the variables
        This method calls constraint.narrow() and queues constraints
        that are affected by recent changes in the domains.
        Returns True if a solution was found"""
        if custom_printer is None:
            printer = self._printer
        else:
            printer = custom_printer
        if verbose:
            printer( strftime('%H:%M:%S'), '** Consistency **')

        _queue = [ (constr.estimateCost(self._domains),
                           constr) for constr in self._constraints ]
        _queue.sort()
        _affected_constraints = {}
        while True:
            if not _queue:
                # refill the queue if some constraints have been affected
                _queue = [(constr.estimateCost(self._domains),
                           constr) for constr in _affected_constraints]
                if not _queue:
                    break
                _queue.sort()
                _affected_constraints.clear()
            if verbose > 2:
                printer( strftime('%H:%M:%S'), 'Queue', _queue)
            cost, constraint = _queue.pop(0)
            if verbose > 1:
                printer( strftime('%H:%M:%S'),
                'Trying to entail constraint', constraint, '[cost:%d]' % cost)
            entailed = constraint.narrow(self._domains)
            for var in constraint.affectedVariables():
                # affected constraints are listeners of
                # affected variables of this constraint
                dom = self._domains[var]
                if not dom.hasChanged():
                    continue
                if verbose > 1 :
                    printer( strftime('%H:%M:%S'),
                        ' -> New domain for variable', var, 'is', dom)
                for constr in self._variableListeners[var]:
                    if constr is not constraint:
                        _affected_constraints[constr] = True
                dom.resetFlags()
            if entailed:
                if verbose:
                    printer( strftime('%H:%M:%S'),
                        "--> Entailed constraint", constraint)
                self._removeConstraint(constraint)
                if constraint in _affected_constraints:
                    del _affected_constraints[constraint]
                
        for domain in self._domains.itervalues():
            if domain.size() != 1:
                return 0
        return 1

class Solver(Psyobj):
    """Top-level object used to manage the search"""

    def __init__(self, distributor=None, printer=_default_printer):
        """if no distributer given, will use the default one"""
        self.printer = printer
        if distributor is None:
            from logilab.constraint.distributors import DefaultDistributor
            distributor = DefaultDistributor()
        self.verbose = True
        self._distributor = distributor
        self.max_depth = 0

    def solve_one(self, repository, verbose=0):
        """Generates only one solution"""
        self.verbose = verbose
        self.max_depth = 0
        self.distrib_cnt = 0
        try:
            # XXX  FIXME: this is a workaround a bug in psyco-1.4
##             return  self._solve(repository).next()
            return  self._solve(repository, 0).next()
        except StopIteration:
            return
        
    def solve_best(self, repository, cost_func, verbose=0):
        """Generates solution with an improving cost"""
        self.verbose = verbose
        self.max_depth = 0
        self.distrib_cnt = 0
        best_cost = None
            # XXX  FIXME: this is a workaround a bug in psyco-1.4
##        for solution in self._solve(repository):
        for solution in self._solve(repository, 0):
            cost = cost_func(**solution)
            if best_cost is None or cost <= best_cost:
                best_cost = cost
                yield solution, cost            
        
    def solve_all(self, repository, verbose=0):
        """Generates all solutions"""
        self.verbose = verbose
        self.max_depth = 0
        self.distrib_cnt = 0
        for solution in self._solve(repository):
            yield solution

    def solve(self, repository, verbose=0):
        """return list of all solutions"""
        self.max_depth = 0
        self.distrib_cnt = 0
        solutions = []
        for solution in self.solve_all(repository, verbose):
            solutions.append(solution)
        return solutions
        
    def _solve(self, repository, recursion_level=0):
        """main generator"""
        _solve = self._solve
        verbose = self.verbose
        if recursion_level > self.max_depth:
            self.max_depth = recursion_level
        if verbose >= 2:
            self.printer( strftime('%H:%M:%S'),)
            self.printer( '*** [%d] Solve called with repository' % recursion_level,)
            repository.display_vars()
        try:
            foundSolution = repository.consistency(verbose, custom_printer=self.printer)
        except ConsistencyFailure, exc:
            if verbose:
                self.printer( strftime('%H:%M:%S'), exc)
        else:
            if foundSolution:
                solution = {}
                for variable, domain in repository.getDomains().items():
                    solution[variable] = domain.getValues()[0]
                if verbose:
                    self.printer( strftime('%H:%M:%S'), '### Found Solution', solution)
                    self.printer( '-'*80)
                yield solution
            else:
                self.distrib_cnt += 1
                for repo in repository.distribute(self._distributor,
                                                  verbose>=2):
                    for solution in _solve(repo, recursion_level+1):
                        if solution is not None:
                            yield solution
                            
        if recursion_level == 0 and self.verbose:
            self.printer( strftime('%H:%M:%S'),'Finished search')
            self.printer( strftime('%H:%M:%S'), 'Maximum recursion depth = ',
                self.max_depth)
            self.printer( 'Nb distributions = ', self.distrib_cnt)

        




class BasicConstraint(Psyobj):
    """A BasicConstraint, which is never queued by the Repository
    A BasicConstraint affects only one variable, and will be entailed
    on the first call to narrow()"""

    __implements__ = ConstraintInterface
    
    def __init__(self, variable, reference, operator):
        """variables is a list of variables on which
        the constraint is applied"""
        self._variable = variable
        self._reference = reference
        self._operator = operator

    def __repr__(self):
        return '<%s %s %s>'% (self.__class__, self._variable, self._reference)

    def isVariableRelevant(self, variable):
        return variable == self._variable

    def estimateCost(self, domains):
        return 0 # get in the first place in the queue
    
    def affectedVariables(self):
        return [self._variable]
    
    def getVariable(self):
        return self._variable
        
    def narrow(self, domains):
        domain = domains[self._variable]
        operator = self._operator
        ref = self._reference
        try:
            for val in domain.getValues() :
                if not operator(val, ref) :
                    domain.removeValue(val)
        except ConsistencyFailure:
            raise ConsistencyFailure('inconsistency while applying %s' % \
                                     repr(self))
        return 1


class AbstractDomain(Psyobj):
    """Implements the functionnality related to the changed flag.
    Can be used as a starting point for concrete domains"""

    __implements__ = DomainInterface
    def __init__(self):
        self.__changed = 0

    def resetFlags(self):
        self.__changed = 0
    
    def hasChanged(self):
        return self.__changed

    def _valueRemoved(self):
        """The implementation of removeValue should call this method"""
        self.__changed = 1
        if self.size() == 0:
            raise ConsistencyFailure()
    
class AbstractConstraint(Psyobj):
    __implements__ = ConstraintInterface
    
    def __init__(self, variables):
        """variables is a list of variables which appear in the formula"""
        self._variables = variables

    def affectedVariables(self):
        """ Return a list of all variables affected by this constraint """
        return self._variables

    def isVariableRelevant(self, variable):
        return variable in self._variables

    def estimateCost(self, domains):
        """Return an estimate of the cost of the narrowing of the constraint"""
        return reduce(MUL, [domains[var].size() for var in self._variables])

    
