import sys
import copy
import random

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

"""Keeps track of unassigned variables.
Kept as a separate class from Sudoku. 
It does not need to be reinitialised with Sudoku."""
class Tracker(object):
    def __init__(self, state):
        most_constrained_vars = []#store unassigned_vars with samllest domains.
        self.row_tracker = []; #stores coordinates of unassigned variables according to row.
        self.col_tracker = []; #stores coordinates of unassigned variables according to row.
        self.box_tracker = []; #stores coordinates of unassigned variables according to 3x3 square.
        for index in range(9):
            self.row_tracker.append([])
            self.col_tracker.append([])
            self.box_tracker.append([])
        for row in range(9):
            for col in range(9):
                if state[row][col] == 0:
                    self.row_tracker[row].append((row, col))
                    self.col_tracker[col].append((row, col)) 
                    self.box_tracker[(row // 3) * 3 + col // 3].append((row, col))
    
    #called in select_unassigned_variable()
    def get_most_constrained_vars(self):
        return self.most_constrained_vars
    
    #called in init_domain()
    def set_most_constrained_vars(self, vars):
        self.most_constrained_vars = vars;

    #returns a set of all unassigned variables in the same row/ column/ box as the input coordinates.
    def get_neighbours(self, row_num, col_num):
        var_set = set()
        square_num = (row_num // 3) * 3 + col_num // 3
        for coordinates in self.row_tracker[row_num]:
            var_set.add(coordinates)
        for coordinates in self.col_tracker[col_num]:
            var_set.add(coordinates)    
        for coordinates in self.box_tracker[square_num]:
            var_set.add(coordinates)
        return var_set

    #called when assigning a blanck space a value.
    def remove(self, row_num, col_num):
        self.row_tracker[row_num].remove((row_num, col_num))
        self.col_tracker[col_num].remove((row_num, col_num))
        self.box_tracker[(row_num // 3) * 3 + col_num // 3].remove((row_num, col_num))
    
    def add(self, row_num, col_num):
        self.row_tracker[row_num].append((row_num, col_num))
        self.col_tracker[col_num].append((row_num, col_num))
        self.box_tracker[(row_num // 3) * 3 + col_num // 3].append((row_num, col_num))
    
    #returns set of coordinates for all unassigned variables.
    def get_unassigned_vars(self):
        var_set = set();
        for index in range(9):
            for coordinates in self.row_tracker[index]:
                var_set.add(coordinates)
        return var_set

        
class Sudoku(object):
    """
    DATA STRUCTURES USED IN THIS SOLVER

    state: 2D array that represents the current state of the puzzle
    domain: 2D array of lists, each list representing the domain of each
    variable. If the variable is assigned, then the domain value will be 0
    instead of a list.
    """

    # Constants
    ROW = 0
    COL = 1
    BOX = 2

    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        
    def solve(self):
        # initialise tracker
        tracker = Tracker(self.puzzle)
        domains = self.init_domains(self.puzzle, tracker)
        # check what the initial domains look like
        self.check_initial_domain(domains)
        state = copy.deepcopy(self.puzzle)

        ans = self.run_back_tracking(state, domains, tracker)

        # check final ans
        for row in ans:
            print row

        return ans

    def run_back_tracking(self, state, domains, tracker):
        initial_domain = domains
        if self.is_goal_state(state):
            return state

        # HEURISTIC HERE
        var = self.select_unassigned_variable(state, domains, tracker, 1)
        var_row = var[self.ROW]
        var_col = var[self.COL]
        tracker.remove(var_row, var_col) #update tracker here 

        # HEURISTIC HERE
        sorted_domain = self.order_domain_values(domains, var, tracker, 1)
        iter = 0 #test if iteration of sorted_domain is sequential. To be removed.
        for value in sorted_domain:
            print("var selected: (" + str(var_row) + "," + str(var_col) + ")")
            print("domain: " + str(domains[var_row][var_col]))
            print("sorted domain: " + str(sorted_domain))
            print("iter: " + str(iter))
            iter += 1
            print("value assigned: " + str(value))
            print("tracker: " + str(tracker.get_unassigned_vars()))
            if self.is_legal_assignment(value, var, state):
                state[var_row][var_col] = value
                for i in range(9):
                    print(state[i])
                print()
                # inferences return new list of domains
                # HEURISTIC HERE
                new_domains = self.inference(state, domains, var, tracker)

                if new_domains != None:
                    result = self.run_back_tracking(state, new_domains, tracker)

                    if result != None:
                        return result
            state[var_row][var_col] = 0
            domains = initial_domain
        #print("assignment to (" + str(var_row) + "," + str(var_col) + ") failed")
        tracker.add(var_row, var_col) #revert changes to tracker
        return None

    def select_unassigned_variable(self, state, domains, tracker, index):
        """
        index == 0 -> select first unassigned variable.
        index == 1 -> most constrained variable with most constraining as tie-breaker.
        index == 2 -> most constraining with most constrained as tie-breaker.
        """ 
        if (index == 0):
            for row in range(9):
                for col in range(9):
                    if state[row][col] == 0:
                        box = self.get_box(row, col)
                        return (row, col, box)
        elif (index == 1):
            most_constrained_vars = tracker.get_most_constrained_vars()
            most_constrained_var = most_constrained_vars[0]
            if len(most_constrained_vars) > 1:
                for var in most_constrained_vars[1:]:
                    var_row = var[self.ROW]
                    var_col = var[self.COL]
                    #print("tie")
                    #print("comparing " + str(most_constrained_var) + " to " + str(var))
                    #print(tracker.get_neighbours(row_num, col_num))
                    if len(tracker.get_neighbours(var_row, var_col)) > len(tracker.get_neighbours(most_constrained_var[self.ROW], most_constrained_var[self.COL])):
                        most_constrained_var = var;
                    #print(var selected: " + str(most_constrained_var))
            row_num = most_constrained_var[self.ROW] 
            col_num = most_constrained_var[self.COL]
            return (row_num, col_num, self.get_box(row_num, col_num))
        elif (index == 2):
            unassigned_var_list = list(set(tracker.get_unassigned_vars()))
            if (len(unassigned_var_list) > 0):
                max_num_constrains = -1 #number of variables constrained by most-constraining-variable.
                most_constraining_var = (-1, -1)
                for unassigned_variable in unassigned_var_list:
                    row_num = unassigned_variable[0]
                    col_num = unassigned_variable[1]
                    num_constrains = len(tracker.get_neighbours(row_num, col_num))
                    if (num_constrains > max_num_constrains):
                        most_constraining_var = (row_num, col_num);
                        max_num_constrains = num_constrains
                    elif (num_constrains == max_num_constrains):
                        if len(domains[row_num][col_num]) > len(domains[most_constraining_var[0]][most_constraining_var[1]]):
                            most_constraining_var = (row_num, col_num); 
                return (row_num, col_num, self.get_box(row_num, col_num))
            
    def order_domain_values(self, domains, var, tracker, index):
        """
        index == 0 => randomly sort the domain
        index == 1 => least constraining value
        """
        var_row = var[self.ROW]
        var_col = var[self.COL]
        #print(tracker.get_neighbours(var_row, var_col))
        domain = domains[var_row][var_col]
        if index == 0:
            random.shuffle(domain)
            return domain
        if index == 1:            
            value_occurence_counter = [0] * 9 #list that keeps track of number of times each value occurs accross the domains of unassigned variables in var_row/ var_col/ var_box.
            #print(value_occurence_counter)
            neighbours = tracker.get_neighbours(var_row, var_col)
            for neighbour in neighbours:
                neighbour_row = neighbour[self.ROW]
                neighbour_col = neighbour[self.COL]
                neighbour_domain = domains[neighbour_row][neighbour_col]
                for value in neighbour_domain:
                    value_occurence_counter[value - 1] += 1
            sorted_values = [] #list of tuples to be sorted in ascending order accoring to occurence.
            for value in domain:
                sorted_values.append((value, value_occurence_counter[value - 1]))
            sorted_values.sort(key = lambda tup: tup[1])
            #print("sorted_values: " + str(sorted_values))
            domain = [tup[0] for tup in sorted_values]
            return domain
            

    def inference(self, state, domains, var, tracker):
        """
        For now just remove the domain of the current var and return the new
        domains. NOTE: DEEPCOPY THE DOMAIN!!
        """
        new_domains = self.init_domains(state, tracker)
        return new_domains

    def is_goal_state(self, state):
        """
        Simple check to see if all variables are assigned. If a variable has
        value 0, then there are still unassigned variables.
        """
        for row in state:
            min_value = min(row)
            if min_value == 0:
                return False
        return True

    def is_legal_assignment(self, value, var, state):
        # check row constraints
        for other_num in state[var[self.ROW]]:
            if other_num == value:
                #print("illegal assignment")
                return False

        # check col constraints
        for index in range(9):
            if state[index][var[self.COL]] == value:
                #print("illegal assignment")
                return False

        # check box constraints
        box = var[self.BOX]
        box_row = box // 3
        box_col = box % 3

        for row in range(box_row*3, box_row*3+3):
            for col in range(box_col*3, box_col*3+3):
                if value == state[row][col]:
                    #print("illegal assignment")
                    return False
        #print("legal assignment")
        return True

    def init_domains(self, state, tracker):
        """
        Returns the domains of a particular state
        """
        # initialize as a 2d array of lists, representing domain of 1-9
        domains = [[[i for i in range(1,10)] for j in range(9)] for k in range(9)]

        # for each empty cell, check all 24 constraining neighbours, reduce
        # domain accordingly
        min_domain_size = 10
        most_constrained_vars = []
        # idenitfy most constrained variable with smallest domain
        for row in range(9):
            for col in range(9):
                var = (row, col, self.get_box(row,col))
                val = state[row][col]
                if val != 0:
                    domains[row][col] = 0 # assign domain value 0 if variable is assigned
                    continue

                domain = domains[row][col]
                domain, domain_size = self.check_row(var, domain, state, 9)
                domain, domain_size = self.check_col(var, domain, state, domain_size)
                domain, domain_size = self.check_box(var, domain, state, domain_size)
                domains[row][col] = domain
                if domain_size == min_domain_size:
                    most_constrained_vars.append((row, col))
                elif domain_size < min_domain_size:
                    most_constrained_vars = [(row, col)]
                    min_domain_size = domain_size
        tracker.set_most_constrained_vars(most_constrained_vars)
        print("most_constrained_vars: " + str(most_constrained_vars))
        return domains

    def check_row(self, var, domain, state, domain_size):
        """
        Returns the reduced domain after checking row constraints
        """
        new_domain = copy.copy(domain)
        row = var[self.ROW]
        for val in state[row]:
            if val == 0:
                continue
            try:
                new_domain.remove(val)
                domain_size -= 1
            except ValueError:
                pass
        return new_domain, domain_size

    def check_col(self, var, domain, state, domain_size):
        """
        Returns the reduced domain after checking col constraints
        """
        new_domain = copy.copy(domain)
        col = var[self.COL]
        for row in range(9):
            val = state[row][col]
            if val == 0:
                continue
            try:
                new_domain.remove(val)
                domain_size -= 1
            except ValueError:
                pass
        return new_domain, domain_size

    def check_box(self, var, domain, state, domain_size):
        """
        Returns the reduced domain after checking box constraints
        """
        new_domain = copy.copy(domain)
        box = var[self.BOX]
        box_row = box // 3
        box_col = box % 3

        for row in range(box_row*3, box_row*3+3):
            for col in range(box_col*3, box_col*3+3):
                val = state[row][col]
                if val == 0:
                    continue
                try:
                    new_domain.remove(val)
                    domain_size -= 1
                except ValueError:
                    pass
        return new_domain, domain_size

    def get_box(self, row, col):
        """
        Get box number from row and col indices. Box number range from 0-8
        """
        box_row = row // 3
        box_col = col // 3
        box = box_row * 3 + box_col
        return box

    def check_initial_domain(self, domains):
        print("Starting state:\n")
        for i in range(9):
            print(self.puzzle[i])
        
        print("\nStarting domains:\n")
        for i in range(9):
            row = ""
            for j in range(9):
                row += "{:20}".format(str(domains[i][j]))
            print(row)

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()
    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
