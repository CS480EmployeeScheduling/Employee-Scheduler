################################################
# This program schedules an arbitrary number of
# employees for an arbitrary number of worker-shifts.
# It takes into account both the availability 
# preferences of the employees and the requirements
# of the employer.
#
# Command line usage:
#    python schedule_file_input.py some_shift_file some_worker_file [some_overlapping_shifts_file]
# 
# @author Scott Abbey
# @author Tyler Young
# @author David Schoonover
# @author Nick Spear
################################################

from logilab.constraint import *
from pprint import pprint # "Pretty Print" -- for nicely printed dicts
from time import strftime
import random
import sys

DEBUGGING = True

################################################
# Converts the shift list to a dictionary for easy searching
#
# @param shift_list A list of all worker-shifts, each specified as
#                   [day, shift, number]
# @return A dictionary whose keys are non-unique shifts (represented
#         as strings) and whose values are the number of workers to
#         schedule for that shift. E.g.,
#              { 'd1s2': 3, 'd2s3': 1 }
################################################
def shift_list_to_dictionary( shift_list ):
    shift_d = {}
    for shift in shift_list:
        day_and_shift = shift_to_string( shift[0:2] )
        if day_and_shift not in shift_d:
            shift_d[day_and_shift] = shift[2]
        else:
            shift_d[ day_and_shift ] = max( shift_d[day_and_shift], shift[2] )
    return shift_d

################################################
# This function takes a list of non-unique overlapping shift
# tuples (as returned by the load_overlapping_shifts() function)
# and translates all shifts to their unique counterparts. E.g.,
# if we had 3 workers at shift 2 of day 1, we would change all
# instances of "d1s2" to 3 separate constraints involving
# "d1s2n1", "d1s2n2", and "d1s2n3", respectively.
#
# @param nonunique_overlap A list of tuples, where each tuple
#                          specifies the non-unique string
#                          representation of 2 shifts that overlap.
# @param shift_list A list of all worker-shifts, each specified as
#                   [day, shift, number]
# @return A list containing a number of tuples; each tuple
#         specifies the unique string representation of
#         two person-shifts that overlap one another.
################################################
def extend_overlapping_shifts_to_be_unique( nonunique_overlap, shift_list ):
    unique_overlap_list = []

    # Convert the list to a dictionary for easy searching
    shift_d = shift_list_to_dictionary( shift_list )

    for pair in nonunique_overlap:
        if not ((pair[0] in shift_d) and (pair[1] in shift_d)):
            raise ValueError

        # For each unique shift associated with the first shift . . .
        for i in range( shift_d[ pair[0] ] + 1 ):
            # And each unique shift associated with the second . . .
            for j in range( shift_d[ pair[1] ] + 1):
                unique_overlap_list.append(
                    ( extend_shift_key( pair[0], i ),
                      extend_shift_key( pair[1], j ) ) )

    return unique_overlap_list

################################################
# This function takes a path to a file and returns
# a list of all the shifts that the file defines to be overlapping.
# 
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
# @return A list containing a number of tuples; each tuple
#         specifies the (non-unique) string representation of
#         two shifts that overlap one another.
################################################
def load_overlapping_shifts( file_path ):
    # Each entry in the overlap list is a tuple of two
    # overlapping shifts
    overlap_list = []
    for line in open(file_path,'r').readlines():
        if line[0] == "%": # denotes end of file to be read
            break
        elif line[0] == "#": # a comment, skip this line
            continue
        # If we get this far, we're just going to assume
        # a well-formatted file.
        (day_0, shift_0, day_1, shift_1) = line.split(',')
        
        overlap_list.append( ( shift_to_string( [int(day_0),
                                                 int(shift_0)] ),
                               shift_to_string( [int(day_1),
                                                 int(shift_1)] ) ) )
    return overlap_list

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

################################################
def load_worker_jobs( file_path ):
    worker_job_list = []
    worker_job_file = open(file_path,'r')
    worker_job_lines = worker_job_file.readlines()
    for line in worker_job_lines:
        if line[0] == "%": # denotes end of file to be read
            break
        elif line[0] == "#": # a comment, skip this line
            continue
        # If we get this far, we're just going to assume
        # a well-formatted file.
        (worker,job) = line.split(',')
        # Add this to the list
        worker_job_list.append([int(worker),int(job),]) 
    
    return worker_job_list
    
################################################

################################################
def load_shift_jobs( file_path ):
    shift_job_list = []
    shift_job_file = open(file_path,'r')
    shift_job_lines = shift_job_file.readlines()
    for line in shift_job_lines:
        if line[0] == "%": # denotes end of file to be read
            break
        elif line[0] == "#": # a comment, skip this line
            continue
        # If we get this far, we're just going to assume
        # a well-formatted file.
        (day,shift,job,number) = line.split(',')
        # Add this to the list
        shift_job_list.append([int(day),int(shift),int(job),int(number)]) 
    
    return shift_job_list


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
# @params shift A list [day,shift,shift_number] to be converted
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
# This function takes a list specifying a shift
# and its type of worker and make a string representation
# of that shift.
#
# @param shift_job_item The shift to be translated
# @param A number representing the worker number for that shift
################################################   
def shift_job_to_string ( shift_job_item, worker_number ):
    string_rep = 'd' + str(shift_job_item[0]) + 's' + str(shift_job_item[1]) + 'n' + str(worker_number) + 'j' + str(shift_job_item[2])
    return string_rep


################################################
# The keys in shift_tuple uniquely identify each
# shift, but sometimes we only care about day and
# shift, not which of the worker-shifts at that time.
# So to get the key for worker_prefs, we break off
# everything from 'n' to the end.
################################################
def shorten_shift_key(key):
    split_key = key.split('n')
    return split_key[0]

################################################
# Sometimes we need to go the opposite direction of
# the shorten_shift_key() function.
# @param key A short shift key, specifying day and
#            shift number. E.g., "d2s3"
# @param shift_number A unique number for the person fulfilling
#                     this shift. E.g., if 3 people are working
#                     d2s3, you might pass 0, 1, or 2 here.
################################################
def extend_shift_key(key, shift_number):
    return key + 'n' + str(shift_number)

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
# A function to take a list specifying a shift and
# its job.  Returns a tuple which contains information
# for the shift day, shift number, shift worker number, and 
# the job number needed for that specific entry.
#
# @param shift_job_list The shift list which specifies jobs
################################################
def make_shift_job_tuple( shift_job_list ):
    shift_jobs = ()
    for item in shift_job_list:
        num_workers = item[3]
        for x in xrange( 0,num_workers ):
            string_representation = shift_job_to_string (item, x)
            shift_jobs = shift_jobs + ( string_representation, )

    return shift_jobs


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
# This function creates constraints based on overlap of
# shifts.
#
# @params constraints A dictionary, possibly holding some
#                     constraints already
#
# @params overlap_list A list containing tuples of string
#                      representations of overlapping
#                      person-shifts
# @return A list of overlap constraints, formulated for the
#         logilab solver, to be appended to the problem's
#         constraint list
################################################
def make_overlapping_constraints( constraints, overlap_list ):
    for shift_pair in overlap_list:
        constraints.append( fd.make_expression(
            shift_pair, "%(shift_0)s[2] != %(shift_1)s[2]" %
            {'shift_0' : shift_pair[0], "shift_1": shift_pair[1]} ))

    return constraints
    
################################################
# This function creates constraints based on an employees
# job and the amount of jobs needed on each shift
#
# @params constraints A dictionary, possibly holding some
#                     constraints already
#
# @params overlap_list A list containing tuples of string
#                      representations of overlapping
#                      person-shifts
# @return A list of overlap constraints, formulated for the
#         logilab solver, to be appended to the problem's
#         constraint list
################################################
def make_overlapping_constraints( constraints, overlap_list ):
    for shift_pair in overlap_list:
        constraints.append( fd.make_expression(
            shift_pair, "%(shift_0)s[2] != %(shift_1)s[2]" %
            {'shift_0' : shift_pair[0], "shift_1": shift_pair[1]} ))

    return constraints

################################################
# This function adds constraints based on availability
# preferences from the workers. If the worker's preference
# level is below the given threshold, the constraint
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
# @params availability_threshold An integer from 0 to 100 specifying
#                                 the lowest availability level allowed
#                                 to be worked for a shift.
################################################
def make_availability_constraints( constraints, shift_tuple, worker_tuple, worker_prefs, availability_threshold ):
    for worker in worker_tuple:
        for shift in shift_tuple:
            short_key = shorten_shift_key(shift)
            key = worker + short_key
            if worker_prefs[key] < availability_threshold:
                constraints.append( fd.make_expression(
                    (shift,), "%(a_shift)s[2] != '%(worker)s'" %
                    {'a_shift' : shift, "worker": worker} ))

    return constraints
    
################################################
# Creates constraints for job types.  If a worker
# does not have the correct job type, that worker
# cannot work that posistion for that shift, so 
# a constraint is added.
#
# @param constraints A dictionary, possibly holding some
#                    constraints already
#
# @param worker_job_list A list containing an entry for
#                        a worker and his/her job number
#
# @param shift_job_tuple contains information for shift position
#                        that require specific job types.
################################################
def make_job_constraints( constraints, worker_job_list, shift_job_tuple ):
    for shift_job in shift_job_tuple:
        for worker_job in worker_job_list:
            if (int(shift_job[-1]) != worker_job[1]):
                shift_key = shift_job[:6]
                worker = 'w' + str(worker_job[0])
                constraints.append( fd.make_expression(
                    (shift_key,), "%(a_shift)s[2] != '%(a_worker)s'" %
                    {'a_shift' : shift_key, "a_worker": worker} ))
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
# This includes shift_file, worker_file, and optionally, overlap_file
# Yeah, this can be done in a more robust way...
shift_file = sys.argv[1]
worker_file = sys.argv[2]
availability_threshold = 100


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


# Check for overlapping shifts
overlapping_list = []
try:
    overlap_file = sys.argv[3]
    if overlap_file == "none":
        overlapping_list = None
    else:
        # Overlapping list is a list containing a number of tuples:
        # each tuple specifies the string rep. of 2 (unique) shifts that overlap
        overlapping_list = extend_overlapping_shifts_to_be_unique(
            load_overlapping_shifts( overlap_file ), shift_list )
except IndexError:
    overlapping_list = None
    
# Check for job specifications
worker_job_list = []
try:
    workers_job_file = sys.argv[4]
    # Overlapping list is a list containing a number of tuples:
    # each tuple specifies the string rep. of 2 (unique) shifts that overlap
    worker_job_list = load_worker_jobs( workers_job_file )
except IndexError:
    worker_job_list = None

# Require shift-job file if worker-job file is specified
if worker_job_list:
    shift_job_list = []
    shift_job_file = sys.argv[5]
    shift_job_list = load_shift_jobs( shift_job_file )
    shift_job_tuple = make_shift_job_tuple( shift_job_list )

# Do this loop until solutions are found,
# decrementing the availability_threshold 
# by 1 each time
solutions = []



# Create a dictionary that can be easily traversed
# to find the preference a worker has indicated
# for a given day and shift
worker_prefs = make_worker_prefs(worker_list)


static_constraints = []
if overlapping_list:
    static_constraints = make_overlapping_constraints( static_constraints, overlapping_list )
        
if worker_job_list:
    static_constraints = make_job_constraints( static_constraints, worker_job_list, shift_job_tuple)



while len(solutions) < 1:
    if DEBUGGING:
        print strftime('%H:%M:%S')+": Availability: "+str(availability_threshold)

    # Set up the domains for each variable.
    # This will restrict each variable to the
    # indicated day and shift, and allow any
    # worker
    domains = make_shift_domains(shift_list, worker_tuple)


    # Set up the constraints based on the given
    # availability threshold
    constraints = static_constraints[:]
    constraints = make_availability_constraints( constraints,
                                                shift_tuple,
                                                worker_tuple,
                                                worker_prefs,
                                                availability_threshold )
    

    # Decrement the availability_threshold
    availability_threshold -= 1

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

