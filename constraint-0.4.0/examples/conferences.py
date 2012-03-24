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


# import Repository, ListDomain and MathematicConstraint
from logilab.constraint import *
variables = ('c01','c02','c03','c04','c05','c06','c07','c08','c09','c10')
values = [(room,slot) 
          for room in ('room A','room B','room C') 
          for slot in ('day 1 AM','day 1 PM','day 2 AM','day 2 PM')]
domains = {}
for v in variables:
    domains[v]=fd.FiniteDomain(values)
constraints = []

# Internet access is in room C only
for conf in ('c03','c04','c05','c06'):
    constraints.append(fd.make_expression((conf,),
                                          "%s[0] == 'room C'"%conf))

# Speakers only available on day 1
for conf in ('c01','c05','c10'):
    constraints.append(fd.make_expression((conf,),
                                          "%s[1].startswith('day 1')"%conf))
# Speakers only available on day 2
for conf in ('c02','c03','c04','c09'):
    constraints.append(fd.make_expression((conf,),
                                          "%s[1].startswith('day 2')"%conf))

# try to satisfy people willing to attend several conferences
groups = (('c01','c02','c03','c10'),
          ('c02','c06','c08','c09'),
          ('c03','c05','c06','c07'),
          ('c01','c03','c07','c08'))
for g in groups:
    for conf1 in g:
        for conf2 in g:
            if conf2 > conf1:
                print '%s[1] != %s[1]'%(conf1,conf2)
                constraints.append(fd.make_expression((conf1,conf2),
                                                      '%s[1] != %s[1]'%\
                                                      (conf1,conf2)))


constraints.append(fd.AllDistinct(variables))

r = Repository(variables,domains,constraints)
solutions = Solver().solve(r)
print solutions
print len(solutions)
