from logilab.constraint import *
from pprint import pprint # "Pretty Print" -- for nicely printed dicts
import random

################################################
# This function takes a bunch of variables and returns a
# numerical "score" indicating how much we dislike this
# assignment. Particularly, it considers how many workers'
# preferences have been violated and to what degree.
#
# NOTE: In order for soft constraints to be taken into
#       account, you must indicate that a worker *can*
#       work a shift in the main problem setup. We take
#       care of the preference part here.
# NOTE Also: Nozick's Utility Monster applies.
#
# @param **kwargs A variable-length parameter where each
#                 keyword (being a shift ID) is associated
#                 with values (the shift's assignments)
################################################
def cost_function( **kwargs ):
    score = 0

    # Debugging:
    #for key in kwargs:
    #    print "another keyword arg: %s: %s" % (key, kwargs[key])
    
    # An example set of soft constraints.
    #   Gives worker, shift, level of preference (1 being
    #   "I really, really don't want to do this, but if the
    #   world is crashing down, I can", and 99 being "I'm
    #   totally happy working this shift, but I don't need to")
    sc = { 'w0s1': 10, # Worker 0 really doesn't want shift 1
           'w0s2': 90, # Worker 0 is okay with shift 2
           'w1s5': 50,
           'w1s6': 20,
           'w5s8': 50,
           'w7s10': 30,
           'w8s14': 5,
           'w9s12': 80,
           'w10s9': 50,
           'w10s15': 60,
           'w10s16': 60,
           'w13s4': 10,
           'w15s8': 70,
           'w15s9': 70 }

    worker_and_shift_l = []
    for key in kwargs:
        worker_and_shift_l.append( str( kwargs[key][1] ) + str( key ) )

    for constraint in sc:
        if constraint in worker_and_shift_l:
            score += sc[ constraint ]
    
    # For each soft constraint we have,
    # add 1 if that soft constraint is violated
    return score




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
for shift in shifts:
    domains[shift]=fd.FiniteDomain(values)
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
random.seed(21)
for worker_num in range(2,16):
    worker_str = 'w'+str(worker_num)
    for shift in shifts:
        # With probability 0.22, we'll say we can work this shift
        if random.randint(1, 100) < 78:
            constraints.append( fd.make_expression(
            (shift,), "%(a_shift)s[1] != '%(worker)s'" %
            {'a_shift': shift, "worker": worker_str} ))
        # Note: if you're a bit baffled by the string formatting above,
        #       cf. this (somewhat old, but still relevant) doc:
        # http://docs.python.org/release/2.5.2/lib/typesseq-strings.html


# No one can work more than once today
# (Does this actually do what it says? - TAY)
for i in range(len(shifts)):
    for j in range(i,len(shifts)):
        if j > i:
            #print '%s[1] != %s[1]'%(shifts[i],shifts[j])
            constraints.append( fd.make_expression(
                (shifts[i],shifts[j]),'%s[1] != %s[1]' %
                (shifts[i],shifts[j]) ) )


#constraints.append(fd.AllDistinct(shifts))

# Repository objects are used to hold the variables, domains
# and constraints describing the problem. A Solver object solves
# the problem described by a Repository.
r = Repository(shifts,domains,constraints)

# Solver( ) takes parameter Distributor if we want to try to optimize that way
#   (cf. Solver source in constraint-0.4.0/propogation.py)
# Parameters for solve_best are Repository, cost_function, (bool)verbose
#    (source found in constraint-0.4.0/propogation.py)
solutions = []
for s in Solver().solve_best(r, cost_function, 1):
    solutions.append(s)
    # This will append better solutions as it finds them; last one is best!

print "Found", len(solutions), "solutions."
print "\n\nHere's the best solution we found:"
pprint(solutions[len(solutions)-1])
