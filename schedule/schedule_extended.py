from logilab.constraint import *
import random

# 3 shifts per day to fill, for 5 days, with a second worker required
# for one particular shift (a busy day, for instance).
# Total of 16 "person-shifts"
shifts = () # formerly called "variables"
for worker_shift in range(3*5 + 1):
    string_representation = 's'+str(worker_shift)
    # Tuples are immutable, so we have to build this up
    # by concatenating to a new tuple (comma declares this a tuple)
    shifts = shifts + ( string_representation, )

workers = ()
for worker_num in range(16):
    string_representation = 'w'+str(worker_num)
    workers = workers + ( string_representation, )

# Possible assignments (prior to any constraints) for a given 
# worker are morning, midday, or evening. When associated with
# a particular shift ID, this will give a day as well. (E.g.,
# we might decide that shifts 0--2 are all on Monday, 3--5 on
# Tuesday, etc. --- Doesn't matter to the solver!
values = [(time,worker) 
          for time in ('morning','midday','evening') 
          for worker in workers ]

# IMPORTANT: By default, the solver assumes all elements of
# the domain are valid. I.e., instead of specifying when a
# person *can* work, you must specify when they *cannot*.
# (Some exceptions apply, like if there's only one person
# qualified to work a shift.)
domains = {}
for v in variables:
    domains[v]=fd.FiniteDomain(values)
constraints = []

# 5 shifts (0--4) are in the morning
# NOTE: From looking at the documentation, it looks like it doesn't matter
#       whether these are modeled as constraints or diff. domains - TAY
for shift_num in range(5):
    string_rep = 's'+str(shift_num)
    constraints.append( fd.make_expression( (string_rep,),
                                            "%s[0] == 'morning'" % string_rep))
# 5 shifts (5--9) at midday
for shift_num in range(5, 10):
    string_rep = 's'+str(shift_num)
    constraints.append( fd.make_expression( (string_rep,),
                                            "%s[0] == 'midday'" % string_rep))
# 5 shifts (10--14) in the evening
for shift_num in range(10, 15):
    string_rep = 's'+str(shift_num)
    constraints.append( fd.make_expression( (string_rep,),
                                            "%s[0] == 'evening'" % string_rep))

# And an extra person working some day in the evening,
# because we're particularly busy that day
constraints.append( fd.make_expression( ('s15',), "%s[0] == 'evening'"%'s15'))



# Worker 1 can only work midday shifts (i.e., no mornings, no evenings)
for shift_num in range(5):
    string_rep = 's'+str(shift_num)
    constraints.append( fd.make_expression( (string_rep,),
                                            "%s[1] != 'w0'"%string_rep))
for shift_num in range(10, 15):
    string_rep = 's'+str(shift_num)
    constraints.append( fd.make_expression( (string_rep,),
                                            "%s[1] != 'w0'"%string_rep))

# Worker 2 can only work shift 15 or 16 (presumably, these are
# the same day and time---recall 16 is the extra shift)
for shift_num in range(15):
    string_rep = 's'+str(shift_num)
    constraints.append( fd.make_expression( (string_rep,),
                                            "%s[1] != 'w1'"%string_rep))

# Assign the rest of the workers' availabilities at random
random.seed(20)
for worker_num in range(2,16):
    worker_str = 'w'+str(worker_num)
    for shift in shifts:
        # With probability 0.1, we'll say we can work this shift
        if random.randint(1, 10) < 2:
            constraints.append( fd.make_expression(
            (shift,), "%(a_shift)s[1] != '%(worker)s'" %
            {'a_shift': shift, "worker": worker_str} ))
        # Note: if you're a bit baffled by the string formatting above,
        #       cf. this (somewhat old, but still relevant) doc:
        # http://docs.python.org/release/2.5.2/lib/typesseq-strings.html


# No one can work more than once today
for i in range(len(variables)):
    for j in range(i,len(variables)):
        if j > i:
            print '%s[1] != %s[1]'%(variables[i],variables[j])
            constraints.append( fd.make_expression(
                (variables[i],variables[j]),'%s[1] != %s[1]' %
                (variables[i],variables[j]) ) )


#constraints.append(fd.AllDistinct(variables))

r = Repository(variables,domains,constraints)
solutions = Solver().solve(r,1)
print solutions
print len(solutions)
