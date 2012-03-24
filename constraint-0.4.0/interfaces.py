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
"""Definition of interfaces"""

class ConstraintInterface:
    """The interface that all constraints should implement"""
    def isVariableRelevant(self, variable):
        """Returns true if changes in the domaine of the variable
        should trigger an evaluation of the constraint"""
        raise NotImplementedError

    def affectedVariables(self):
        """ Return a list of all variables affected by this constraint """
        raise NotImplementedError
        
    def estimateCost(self, domains):
        """ Return an estimate of the cost of the narrowing of the constraint"""
        raise NotImplementedError
        
    def narrow(self, domains):
        """ensures that the domains are consistent with the constraint
        Calls domain.removeValue to remove values from a domain
        raises ConsistencyFailure if the narrowing fails
        Returns 1 if the constraint is entailed, and 0 otherwise"""
        raise NotImplementedError


class DomainInterface:
    """The interface that all domains should implement"""

    def resetFlags(self):
        """resets the hasChanged flag"""
        raise NotImplementedError
    
    def hasChanged(self):
        """returns true if values have been removed from the domain
        since the last call to resetFlags"""
        raise NotImplementedError
    
    def removeValue(self, value):
        """Removes a value from the domain"""
        raise NotImplementedError

    def size(self):
        """returns the number of values in the domain"""
        raise NotImplementedError
        
    def getValues(self):
        """returns a tuple containing all the values in the domain
        These values should not be modified!"""
        raise NotImplementedError

class DistributorInterface:
    """The interface that all distributors should implement"""
    def distribute(self, domains, verbose=0):
        """domains is a dictionnary of variable -> Domain objects
        This method returns a list of dictionnaries similar to the domain argument
        This list should be a partition of the initial domains"""
        raise NotImplementedError

## class VariableInterface:
##     """The interface that all variables should implement"""
##     def getDomain(self):
##         """returns the domain of the variable"""
##         raise NotImplementedError
##     def setDomain(self, domain):
##         """sets a new domain to the variable"""
##         raise NotImplementedError

##     # Magic methods for various operations
##     def __add__(self, other):
##         raise NotImplementedError

##     def __sub__(self, other):
##         raise NotImplementedError
    
##     def __mul__(self, other):
##         raise NotImplementedError
    
##     def __div__(self, other):
##         raise NotImplementedError
        
##     def __radd__(self, other):
##         raise NotImplementedError

##     def __rsub__(self, other):
##         raise NotImplementedError
    
##     def __rmul__(self, other):
##         raise NotImplementedError
    
##     def __rdiv__(self, other):
##         raise NotImplementedError
        
##     def __abs__(self):
##         raise NotImplementedError

##     def __neg__(self):
##         raise NotImplementedError

##     def __pos__(self):
##         raise NotImplementedError

##     def __lt__(self, other):
##         raise NotImplementedError

##     def __le__(self, other):
##         raise NotImplementedError

##     def __gt__(self, other):
##         raise NotImplementedError

##     def __ge__(self, other):
##         raise NotImplementedError

##     def __eq__(self, other):
##         raise NotImplementedError

##     def __ne__(self, other):
##         raise NotImplementedError

##     def __len__(self):
##         raise NotImplementedError

##     def __getitem__(self, size):
##         raise NotImplementedError
