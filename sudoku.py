import sys
import copy
import random

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

# Globals constants
ROW = 0
COL = 1
BOX = 2

class Sudoku(object):
    """
    DATA STRUCTURES USED IN THIS SOLVER

    state: 2D array that represents the current state of the puzzle
    domain: 2D array of lists, each list representing the domain of each
    variable. If the variable is assigned, then the domain value will be 0
    instead of a list.
    """

    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists

    def solve(self):
        domains = self.init_domains(self.puzzle)

        # check what the initial domains look like
        self.check_initial_domain(domains)
        state = copy.deepcopy(self.puzzle)

        ans = self.run_back_tracking(state, domains)

        # check final ans
        for row in ans:
            print row

        return ans

    def run_back_tracking(self, state, domains):
        initial_domain = domains
        if self.is_goal_state(state):
            return state

        # HEURISTIC HERE
        var = self.select_unassigned_variable(state)
        var_row = var[ROW]
        var_col = var[COL]
        domain = domains[var_row][var_col]

        # HEURISTIC HERE
        sorted_domain = self.order_domain_values(state, domain)

        for value in sorted_domain:
            if self.is_legal_assignment(value, var, state):
                state[var_row][var_col] = value

                # inferences return new list of domains
                # HEURISTIC HERE
                new_domains = self.inference(state, domains, var)

                if new_domains != None:
                    result = self.run_back_tracking(state, new_domains)

                    if result != None:
                        return result

            state[var_row][var_col] = 0
            domains = initial_domain

        return None

    def select_unassigned_variable(self, state):
        """
        For now just select first unassigned variable
        """
        for row in range(9):
            for col in range(9):
                if state[row][col] == 0:
                    box = self.get_box(row, col)
                    return (row, col, box)

    def order_domain_values(self, state, domain):
        """
        For now just randomly sort the domain
        """
        random.shuffle(domain)
        return domain

    def inference(self, state, domains, var):
        """
        For now just remove the domain of the current var and return the new
        domains. NOTE: DEEPCOPY THE DOMAIN!!
        """
        new_domains = self.init_domains(state)
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
        for other_num in state[var[ROW]]:
            if other_num == value:
                return False

        # check col constraints
        for index in range(9):
            if state[index][var[COL]] == value:
                return False

        # check box constraints
        box = var[BOX]
        box_row = box // 3
        box_col = box % 3

        for row in range(box_row*3, box_row*3+3):
            for col in range(box_col*3, box_col*3+3):
                if value == state[row][col]:
                    return False

        return True

    def init_domains(self, state):
        """
        Returns the domains of a particular state
        """
        # initialize as a 2d array of lists, representing domain of 1-9
        domains = [[[i for i in range(1,10)] for j in range(9)] for k in range(9)]

        # for each empty cell, check all 24 constraining neighbours, reduce
        # domain accordingly
        for row in range(9):
            for col in range(9):
                var = (row, col, self.get_box(row,col))
                val = state[row][col]
                if val != 0:
                    domains[row][col] = 0 # assign domain value 0 if variable is assigned
                    continue

                domain = domains[row][col]
                domain = self.check_row(var, domain, state)
                domain = self.check_col(var, domain, state)
                domain = self.check_box(var, domain, state)
                domains[row][col] = domain
        
        return domains

    def check_row(self, var, domain, state):
        """
        Returns the reduced domain after checking row constraints
        """
        new_domain = copy.copy(domain)
        row = var[ROW]
        for val in state[row]:
            if val == 0:
                continue
            try:
                new_domain.remove(val)
            except ValueError:
                pass
        return new_domain

    def check_col(self, var, domain, state):
        """
        Returns the reduced domain after checking col constraints
        """
        new_domain = copy.copy(domain)
        col = var[COL]
        for row in range(9):
            val = state[row][col]
            if val == 0:
                continue
            try:
                new_domain.remove(val)
            except ValueError:
                pass
        return new_domain

    def check_box(self, var, domain, state):
        """
        Returns the reduced domain after checking box constraints
        """
        new_domain = copy.copy(domain)
        box = var[BOX]
        box_row = box // 3
        box_col = box % 3

        for row in range(box_row*3, box_row*3+3):
            for col in range(box_col*3, box_col*3+3):
                val = state[row][col]
                if val == 0:
                    continue
                try:
                    new_domain.remove(val)
                except ValueError:
                    pass
        return new_domain

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
