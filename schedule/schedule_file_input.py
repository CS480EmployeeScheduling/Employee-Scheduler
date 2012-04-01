from logilab.constraint import *
from pprint import pprint # "Pretty Print" -- for nicely printed dicts
from time import strftime
import random
import sys



################################################
# This function takes a path to a file and returns
# a list of all the worker-shifts defined in the file.
# The format of the file is:
# Any line starting with a # is a comment and not read
# Any line starting with % indicates the end of data to be read
# Any other line has the format: [day],[shift],[needed]
# where day and shift identify the time the shift takes
# place and needed is how many workers are required for that
# shift.
#
# @param file_path the path to the file containing
#                  shift definitions
################################################

def load_shifts( file_path ):
    shift_list = [] # Each entry is a list stating the day and shift of that day
    shift_file = open(file_path,'r')
    shift_lines = shift_file.readlines()
    for line in shift_lines:
        if line[0] == "%": # denotes end of file to be read
            break
        elif line[0] == "#": # a comment, skip this line
            continue
        # If we get this far, we're just going to assume
        # a well-formatted file.
        (day,shift,needed) = line.split(',')
        # Add 1 worker-shift for each that is needed
        for i in range(int(needed)):
            shift_list.append([int(day),int(shift),i])

    return shift_list


################################################
# This function takes a path to a file and returns
# a list whose elements are lists representing
# each line of the file. The file defines the
# workers in the system and their preference for
# each shift.
# The format of the file is:
# Any line starting with a # is a comment and not read
# Any line starting with % indicates the end of data to be read
# Any other line has the format: [worker],[day],[shift],[availability]
# Where worker, day, and shift are integers representing
# those items and availability is an integer from 0
# (totally not available) to 100 (absolutely available)
################################################
def load_workers( file_path ):
    # Each entry in worker_list is a list stating
    # the worker, which day and shift, and his
    # preference for working that shift
    worker_list = []
    worker_file = open(file_path,'r')
    worker_lines = worker_file.readlines()
    for line in worker_lines:
        if line[0] == "%": # denotes end of file to be read
            break
        elif line[0] == "#": # a comment, skip this line
            continue
        # If we get this far, we're just going to assume
        # a well-formatted file.
        (worker,day,shift,availability) = line.split(',')
        # Add this to the list
        worker_list.append([int(worker),int(day),int(shift),int(availability)]) 
    
    return worker_list


################################################
# This function takes a shift in the list format and
# returns a string representation for that format.
# This is for the shift without a unique identifier.
#
# @params shift A list [day,shift] to be converted
################################################
def shift_to_string( shift ):
    string_representation = 'd'+str(shift[0])+'s'+str(shift[1])
    return string_representation


################################################
# This function takes a shift in the list format and
# returns a string representation for that format.
# This is for the shift with its unique identifier.
#
# @params shift A list [day,shift] to be converted
################################################
def unique_shift_to_string( shift ):
    string_representation = 'd'+str(shift[0])+'s'+str(shift[1])+'n'+str(shift[2])
    return string_representation


################################################
# This function takes a worker's number and
# returns a string representation for that worker.
#
# @params worker_number A number representing a worker
################################################
def worker_to_string( worker_number ):
    string_representation = 'w'+str(worker_number)
    return string_representation


################################################
# The keys in shift_tuple uniquely identify each
# shift, but sometimes we only care about day and
# shift, not which of the worker-shifts at that time.
# So to get the ky for worker_prefs, we break off
# Everything from 'n' to the end.
################################################
def shorten_shift_key(key):
    split_key = key.split('n')
    return split_key[0]



################################################
# This function takes input in the form of a list
# of [day,shift] lists. It returns their representation
# as a tuple for the variables of the repository
# 
# @param shift_list A list of shifts to be turned into tuples
################################################
def make_shift_tuple( shift_list ):
    shifts = ()
    for shift in shift_list:
        string_representation = unique_shift_to_string(shift)
        # Tuples are immutable, so we have to build this up
        # by concatenating to a new tuple (comma declares this a tuple)
        shifts = shifts + ( string_representation, )

    return shifts


################################################
# This function takes input in the form of a list
# of worker preferences for each shift.
# It returns a tuple with a string representation
# of each individual worker in the system
# 
# @param worker_list The worker list
################################################
def make_worker_tuple( worker_list ):
    worker_numbers = []
    for item in worker_list:
        worker_numbers.append(item[0])
    
    # set(worker_numbers) removes duplicates
    # from the list of worker numbers
    number_of_workers = len(set(worker_numbers))

    workers = ()
    for worker_num in range(number_of_workers):
        string_representation = worker_to_string(worker_num)
        workers = workers + ( string_representation, )

    return workers


################################################
# This function creates the domains for each shift variable.
# It limits the domain to the day and shift that the
# shift represents, and allows any worker to work that shift.
#
# @params shift_list A list of all the shifts, [day,shift] format
# @params workers_tuple A tuple containing the strings representing
#                       each worker
################################################
def make_shift_domains( shift_list, workers_tuple ):
    domains = {}
    for shift in shift_list:
        # Get the possible values for this shift
        values = [('d'+str(shift[0]),'s'+str(shift[1]),worker)
                for worker in workers_tuple ]

        shift_string = unique_shift_to_string(shift)
        domains[shift_string] = fd.FiniteDomain(values)


    return domains


################################################
# This function creates a dictionary containing
# the preference level for each individual 
# worker-shift entity.
# 
# @params worker_list The worker list representation,
#                     which is a list of lists in the
#                     format: [worker],[day],[shift],[availability]
################################################
def make_worker_prefs( worker_list ):
    worker_prefs = {}
    for item in worker_list:
        shift = shift_to_string([item[1],item[2]])
        worker = worker_to_string(item[0])
        key = worker+shift
        worker_prefs[key] = item[3]

    return worker_prefs


################################################
# This function adds constraints based on availability
# preferences from the workers. If the worker's preference
# level is below the given threshhold, the constraint
# is added to the list.
#
# @params constraints A dictionary, possibly holding some
#                     constraints already
#
# @params shift_tuple A tuple with the names of each shift
#
# @params worker_tuple A tuple with the names of each worker
#
# @params worker_prefs A dictionary with the preference level
#                      of each worker for each shift
#
# @params availability_threshhold An integer from 0 to 100 specifying
#                                 the lowest availability level allowed
#                                 to be worked for a shift.
################################################
def make_availability_constraints( constraints, shift_tuple, worker_tuple, worker_prefs, availability_threshhold ):
    for worker in worker_tuple:
        for shift in shift_tuple:
            short_key = shorten_shift_key(shift)
            key = worker + short_key
            if worker_prefs[key] < availability_threshhold:
                constraints.append( fd.make_expression(
                    (shift,), "%(a_shift)s[2] != '%(worker)s'" %
                    {'a_shift' : shift, "worker": worker} ))

    return constraints


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
# @param worker_prefs The preference level of each
#                     worker for each shift
# @param **kwargs A variable-length parameter where each
#                 keyword (being a shift ID) is associated
#                 with values (the shift's assignments)
################################################
def cost_function( **kwargs ):
    global worker_prefs
    score = 0

    # Debugging:
    #for key in kwargs:
        #print "another keyword arg: %s: %s" % (key, kwargs[key])
    
    worker_and_shift_l = []
    for key in kwargs:
        short_key = shorten_shift_key(key)
        worker_and_shift_l.append( str( kwargs[key][2] ) + str( short_key ) )

    for constraint in worker_prefs:
        if constraint in worker_and_shift_l:
            score += worker_prefs[ constraint ]
    
    # For each soft constraint we have,
    # add 1 if that soft constraint is violated
    return score


########################
# Main program below   #
########################

# Get the arguments passed
# For now, just: shift_file worker_file
# Yeah, this can be done in a more robust way...
shift_file = sys.argv[1]
worker_file = sys.argv[2]
availability_threshhold = 100


# Process the files into simple lists of lists
# that we can use in various places
shift_list = load_shifts(shift_file)
worker_list = load_workers(worker_file)

# Make a shifts tuple that will represent the
# names of the variables in the constraint
# satisfaction problem
shift_tuple = make_shift_tuple(shift_list)

# Make a tuple holding a string representation
# of each worker defined.
worker_tuple = make_worker_tuple(worker_list)


# Do this loop until solutions are found,
# decrementing the availability_threshhold 
# by 1 each time
solutions = []
while len(solutions) < 1:
    print strftime('%H:%M:%S')+": Availability: "+str(availability_threshhold)

    # Set up the domains for each variable.
    # This will restrict each variable to the
    # indicated day and shift, and allow any
    # worker.
    domains = make_shift_domains(shift_list, worker_tuple)

    # Create a dictionary that can be easily traversed
    # to find the preference a worker has indicated
    # for a given day and shift
    worker_prefs = make_worker_prefs(worker_list)

    # Set up the constraints based on the given
    # availability threshhold
    constraints = []
    constraints = make_availability_constraints( constraints,
                                                shift_tuple,
                                                worker_tuple,
                                                worker_prefs,
                                                availability_threshhold )

    # Decrement the availability_threshhold
    # Okay, this probably shouldn't be done here
    # but whatever
    availability_threshhold -= 1

    # We don't want to schedule the same worker at the same
    # shift more than once
    constraints.append(fd.AllDistinct(shift_tuple))

    # Repository objects are used to hold the variables, domains
    # and constraints describing the problem. A Solver object solves
    # the problem described by a Repository.
    r = Repository(shift_tuple,domains,constraints)

    # Solver( ) takes parameter Distributor if we want to try to optimize that way
    #   (cf. Solver source in constraint-0.4.0/propogation.py)
    # Parameters for solve_best are Repository, cost_function, (bool)verbose
    #    (source found in constraint-0.4.0/propogation.py)
    #for s in Solver().solve_best(r, cost_function, 0):
    #    solutions.append(s)
    # This will append better solutions as it finds them; last one is best!
    # Just look for one solution, for testing when we 
    # don't care how good the result is.
    # 1 for verbose, 0 for silent
    solutions.append(Solver().solve_one(r,0))
    if solutions[0] == None:
        solutions = []



print "Found", len(solutions), "solutions."
print "\n\nHere's the best solution we found:"
pprint(solutions[-1])
