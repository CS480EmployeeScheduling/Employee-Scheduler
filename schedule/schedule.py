from logilab.constraint import *
# A total of 4 shifts must be filled
variables = ('s1','s2','s3','s4')

values = [(time,worker) 
          for time in ('morning','midday','evening') 
          for worker in ('w1','w2','w3','w4')]

domains = {}
for v in variables:
    domains[v]=fd.FiniteDomain(values)
constraints = []

# Shifts 1 and 2 are morning
constraints.append(fd.make_expression(('s1',),"%s[0] == 'morning'"%'s1'))
constraints.append(fd.make_expression(('s2',),"%s[0] == 'morning'"%'s2'))

# Shifts 3 and 4 are evening
constraints.append(fd.make_expression(('s3',),"%s[0] == 'midday'"%'s3'))
constraints.append(fd.make_expression(('s4',),"%s[0] == 'midday'"%'s4'))

# Worker 1 can only work in the midday shift
for shift in ('s1','s2'):
    constraints.append(fd.make_expression((shift,),"%s[1] != 'w1'"%shift))

# Worker 2 cannot work in the morning
for shift in ('s1','s2'):
    constraints.append(fd.make_expression((shift,),"%s[1] != 'w2'"%shift))

# Worker 7 cannot work in the evening
#for shift in ('s6','s6','s8'):
#    constraints.append(fd.make_expression((shift,),"%s[1] != 'w7'"%shift))

# No one can work more than once today
for i in range(len(variables)):
    for j in range(i,len(variables)):
        if j > i:
            print '%s[1] != %s[1]'%(variables[i],variables[j])
            constraints.append(fd.make_expression((variables[i],variables[j]),'%s[1] != %s[1]'%(variables[i],variables[j])))


#constraints.append(fd.AllDistinct(variables))

r = Repository(variables,domains,constraints)
solutions = Solver().solve(r,1)
print solutions
print len(solutions)
