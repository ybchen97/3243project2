import os
import sys
import random
import time
import copy
import csv
from collections import deque
from csv import writer
from csv import reader
import turtle
from random import randint, shuffle
from time import sleep

# Code taken from Sudoku.py
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

    # Variable heuristics
    FIRST_UNASSIGNED_VAR = 0
    MOST_CONSTRAINED_VAR = 1

    # Value heuristics
    RANDOM_SHUFFLE = 0
    LEAST_CONSTRAINING_VAL = 1

    # Inference heuristics
    FORWARD_CHECKING = 0
    AC3 = 1

    def __init__(self, puzzle, inference_type):
        # you may add more attributes if you need
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.variable_heuristic = self.MOST_CONSTRAINED_VAR
        self.value_heuristic = self.LEAST_CONSTRAINING_VAL
        self.inference_heuristic = inference_type
        self.totalSteps = 0
        self.totalSizeDomains = 0
        self.timeTaken = 0

    def solve(self):
        start = time.time()
        domains = self.get_initial_domains(self.puzzle)

        # self.check_domains(self.puzzle, domains)
        state = copy.deepcopy(self.puzzle)
        ans = self.run_back_tracking(state, domains)

        if ans is None:
            return "Did not solve :("
        end = time.time()
        self.timeTaken = end - start
        return ans

    def run_back_tracking(self, state, domains):

        self.totalSteps += 1
        # self.check_domains(state, domains)
        if self.is_goal_state(state):
            return state

        # VARIABLE HEURISTIC HERE
        var = self.select_unassigned_variable(state, domains)
        var_row, var_col = var
        # print("Variable to assign next: {}".format(var))

        # VALUE HEURISTIC HERE
        sorted_domain = self.order_domain_values(state, domains, var)
        # print("Values to try: {}".format(sorted_domain))

        for value in sorted_domain:
            # print("Value: {}".format(value))
            if self.is_legal_assignment(value, var, state):
                state[var_row][var_col] = value

                # INFERENCE HEURISTIC HERE
                new_domains = self.inference(state, domains, var)
                self.totalSizeDomains += self.domain_size(new_domains)
                #print("domains are ",new_domains)
                #print("\n\n")

                if new_domains is not None:
                    result = self.run_back_tracking(state, new_domains)

                    if result is not None:
                        return result

            state[var_row][var_col] = 0

        return None
    
    def domain_size(self, domains):
        count = 0
        if (domains == None):
            return count
        for row in domains:
            for variable in row:
                for values in variable:
                    count += 1
        return count
    

    def select_unassigned_variable(self, state, domains):
        """
        FIRST_UNASSIGNED_VAR returns the first unassigned variable
        MOST_CONSTRAINED_VAR returns the most constrained variable
        """
        if self.variable_heuristic == self.FIRST_UNASSIGNED_VAR:
            return self.first_unassigned(state)
        elif self.variable_heuristic == self.MOST_CONSTRAINED_VAR:
            return self.most_constrained_variable(state, domains)

    def first_unassigned(self, state):
        """
        Returns first unassigned variable
        """
        for row in range(9):
            for col in range(9):
                if state[row][col] == 0:
                    return (row, col)

    def most_constrained_variable(self, state, domains):
        """
        Returns unassigned variable with smallest domain
        """
        result = (0, 0)
        min_domain_length = 10
        for row in range(9):
            for col in range(9):
                domain = domains[row][col]
                if state[row][col] == 0 and len(domain) < min_domain_length:
                    result = (row, col)
                    min_domain_length = len(domain)
        return result

    def order_domain_values(self, state, domains, var):
        """
        For now just randomly sort the domain
        """
        if self.value_heuristic == self.RANDOM_SHUFFLE:
            new_domain = domains[var[self.ROW]][var[self.COL]]
            random.shuffle(new_domain)
            return new_domain
        elif self.value_heuristic == self.LEAST_CONSTRAINING_VAL:
            return self.least_constraining_value(state, domains, var)

    def count_valid_values(self, neighbour_domain, value):
        count = 0
        for val in neighbour_domain:
            if val != value:
                count += 1
        return count

    def least_constraining_value(self, state, domains, var):
        """
        Returns domain sorted by least conflicts
        """
        row, col = var
        domain = domains[row][col]
        sorted_domain = []
        neighbours = self.get_unassigned_neighbours(var, state)
        for value in domain:
            conflicts = 0
            for neighbour in neighbours:
                row, col = neighbour
                neighbour_domain = domains[row][col]
                # TODO: Something interesting to note, it becomes slower if 'not' is not included
                # Current implementation is actually most constraining value...
                if value not in neighbour_domain:
                    conflicts += 1
            sorted_domain.append((value, conflicts))

        sorted_domain = sorted(sorted_domain, key=lambda tup: tup[1])
        return [tup[0] for tup in sorted_domain]

    def get_unassigned_neighbours(self, var, state, get_all_neighbours=False):
        """
        Returns a list of neighbours or all unassigned neighbours of var
        """
        neighbours = []
        row, col = var

        if get_all_neighbours:
            # Neighbours in row and col
            for i in range(9):
                if i != col:
                    neighbours.append((row, i))
                if i != row:
                    neighbours.append((i, col))

            # Neighbours in box
            box_row = (row // 3) * 3
            box_col = (col // 3) * 3

            for i in range(box_row, box_row+3):
                for j in range(box_col, box_col+3):
                    # Not same row AND not same col to prevent double counting from above
                    if i != row and j != col:
                        neighbours.append((i, j))

        else:
            # Neighbours in row and col
            for i in range(9):
                if state[row][i] == 0 and i != col:
                    neighbours.append((row, i))
                if state[i][col] == 0 and i != row:
                    neighbours.append((i, col))

            # Neighbours in box
            box_row = (row // 3) * 3
            box_col = (col // 3) * 3

            for i in range(box_row, box_row+3):
                for j in range(box_col, box_col+3):
                    # Not same row AND not same col to prevent double counting from above
                    if state[i][j] == 0 and (i != row and j != col):
                        neighbours.append((i, j))

        return neighbours

    def get_unassigned_variables(self, state):
        unassigned_variables = []
        for row in range(9):
            for col in range(9):
                if state[row][col] == 0:
                    unassigned_variables.append((row, col))
        return unassigned_variables

    def inference(self, state, domains, var):
        """
        For now just remove the domain of the current var and return the new
        domains. NOTE: DEEPCOPY THE DOMAIN!!
        """
        if self.inference_heuristic == self.FORWARD_CHECKING:
            # TODO: issue here due to bug with init_domains
            return self.init_domains(state)
        elif self.inference_heuristic == self.AC3:
            row, col = var
            new_domains = copy.deepcopy(domains)
            new_domains[row][col] = [state[row][col]]
            new_domains = self.ac3(state, new_domains)
            return new_domains

    def ac3(self, state, domains):
        # initialize queue of arcs
        queue = deque()
        unassigned_var = self.get_unassigned_variables(state)
        for x in unassigned_var:
            neighbours = self.get_unassigned_neighbours(x, state, get_all_neighbours=True)
            for y in neighbours:
                queue.append((x, y))

        while len(queue) > 0:
            x, y = queue.popleft()
            # print("x: {} y: {}".format(x, y))
            if self.revise(domains, x, y):
                # self.check_domains(state, domains)
                if len(domains[x[self.ROW]][x[self.COL]]) == 0:
                    # print("({},{})'s domain is gone".format(x[self.ROW], x[self.COL]))
                    return None
                neighbours = self.get_unassigned_neighbours(x, state, get_all_neighbours=True)
                neighbours.remove(y)
                for neighbour in neighbours:
                    queue.append((neighbour, x))
        return domains

    def revise(self, domains, x, y):
        revised = False
        x_domain = domains[x[self.ROW]][x[self.COL]]
        # print("Var {}'s domain: {}".format(x, x_domain))
        for x_val in x_domain:
            y_domain = domains[y[self.ROW]][y[self.COL]]
            has_diff_val = False
            for y_val in y_domain:
                if x_val != y_val:
                    has_diff_val = True
                    break
            if not has_diff_val:
                x_domain.remove(x_val)
                revised = True
        return revised

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
        row, col = var
        # check row constraints
        for i in range(9):
            if state[row][i] == value:
                return False

        # check col constraints
        for i in range(9):
            if state[i][col] == value:
                return False

        # check box constraints
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3

        for row in range(box_row, box_row+3):
            for col in range(box_col, box_col+3):
                if value == state[row][col]:
                    return False

        return True

    def get_initial_domains(self, state):
        initial_domains = [[[1,2,3,4,5,6,7,8,9] for i in range(9)] for j in range(9)]
        for row in range(9):
            for col in range(9):
                if state[row][col] != 0:
                    initial_domains[row][col] = [state[row][col]]
        return initial_domains

    # TODO: There is some problem with this function, USE WITH CAUTION.
    # Timing is increased by 7 seconds if this function is used
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
                var = (row, col)
                val = state[row][col]
                if val != 0:
                    # domains[row][col] = 0  # assign domain value 0 if variable is assigned
                    domains[row][col] = [val]  # assign domain to be assigned value if variable is assigned
                    continue

                domain = domains[row][col]
                domain = self.check_row(var, domain, state)
                domain = self.check_col(var, domain, state)
                domain = self.check_box(var, domain, state)
                if len(domain) == 0:
                    return None
                domains[row][col] = domain

        return domains

    def check_row(self, var, domain, state):
        """
        Returns the reduced domain after checking row constraints
        """
        new_domain = copy.deepcopy(domain)
        row = var[self.ROW]
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
        new_domain = copy.deepcopy(domain)
        col = var[self.COL]
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
        new_domain = copy.deepcopy(domain)
        row, col = var
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3

        for row in range(box_row, box_row+3):
            for col in range(box_col, box_col+3):
                val = state[row][col]
                if val == 0:
                    continue
                try:
                    new_domain.remove(val)
                except ValueError:
                    pass
        return new_domain

    def check_domains(self, state, domains):
        print("State:\n")
        for i in range(9):
            print(state[i])
        
        print("\nDomains:\n")
        for i in range(9):
            row = ""
            for j in range(9):
                row += "{:20}".format(str(domains[i][j]))
            print(row)







        





if __name__ == "__main__":

    # Puzzles taken from https://qqwing.com/generate.html

    with open('SudokuResults.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        heading_list = []
    
        # Adding headings for the columns

        heading_list.append(str("Simple_FC_BacktrackingSteps"))
        heading_list.append(str("Simple_AC3_BacktrackingSteps"))
        heading_list.append(str("Simple_FC_AverageDomainSize"))
        heading_list.append(str("Simple_AC3_AverageDomainSize"))
        heading_list.append(str("Simple_FC_Time"))
        heading_list.append(str("Simple_AC3_Time"))

        heading_list.append(str("Easy_FC_BacktrackingSteps"))
        heading_list.append(str("Easy_AC3_BacktrackingSteps"))
        heading_list.append(str("Easy_FC_AverageDomainSize"))
        heading_list.append(str("Easy_AC3_AverageDomainSize"))
        heading_list.append(str("Easy_FC_Time"))
        heading_list.append(str("Easy_AC3_Time"))

        heading_list.append(str("Intermediate_FC_BacktrackingSteps"))
        heading_list.append(str("Intermediate_AC3_BacktrackingSteps"))
        heading_list.append(str("Intermediate_FC_AverageDomainSize"))
        heading_list.append(str("Intermediate_AC3_AverageDomainSize"))
        heading_list.append(str("Intermediate_FC_Time"))
        heading_list.append(str("Intermediate_AC3_Time"))

        heading_list.append(str("Hard_FC_BacktrackingSteps"))
        heading_list.append(str("Hard_AC3_BacktrackingSteps"))
        heading_list.append(str("Hard_FC_AverageDomainSize"))
        heading_list.append(str("Hard_AC3_AverageDomainSize"))
        heading_list.append(str("Hard_FC_Time"))
        heading_list.append(str("Hard_AC3_Time"))

        print(heading_list)
        writer.writerow(heading_list)
        
        total_result = []
        
        # Parses in Simple puzzles and adds results into their respective lists
        with open("experiment_Simple_puzzles.txt", "r") as a_file:
            puzzle = [[0 for i in range(9)] for j in range(9)]
            AC3_Simple_Steps_list = []
            FC_Simple_Steps_list = []
            AC3_Simple_AvDomain_list = []
            FC_Simple_AvDomain_list = []
            AC3_Simple_Time_list = []
            FC_Simple_Time_list = []
            for line in a_file:
                stripped_line = line.strip()
                i, j = 0, 0
                for number in line:
                    if '0' <= number <= '9':
                        puzzle[i][j] = int(number)
                        j += 1
                        if j == 9:
                            i += 1
                            j = 0

                sudoku_FC = Sudoku(puzzle, 0)
                sudoku_AC3 = Sudoku(puzzle, 1)
                ans_FC = sudoku_FC.solve()
                ans_AC3 = sudoku_AC3.solve()
                
                FC_Simple_Steps_list.append(sudoku_FC.totalSteps)
                AC3_Simple_Steps_list.append(sudoku_AC3.totalSteps)
                FC_Simple_AvDomain_list.append(sudoku_FC.totalSizeDomains / sudoku_FC.totalSteps)
                AC3_Simple_AvDomain_list.append(sudoku_AC3.totalSizeDomains / sudoku_AC3.totalSteps)
                FC_Simple_Time_list.append(sudoku_FC.timeTaken)
                AC3_Simple_Time_list.append(sudoku_AC3.timeTaken)
                    

        # Parses in Easy puzzles and adds results into their respective lists
        with open("experiment_Easy_puzzles.txt", "r") as a_file:
            puzzle = [[0 for i in range(9)] for j in range(9)]
            AC3_Easy_Steps_list = []
            FC_Easy_Steps_list = []
            AC3_Easy_AvDomain_list = []
            FC_Easy_AvDomain_list = []
            AC3_Easy_Time_list = []
            FC_Easy_Time_list = []
            for line in a_file:
                stripped_line = line.strip()
                i, j = 0, 0
                for number in line:
                    if '0' <= number <= '9':
                        puzzle[i][j] = int(number)
                        j += 1
                        if j == 9:
                            i += 1
                            j = 0

                sudoku_FC = Sudoku(puzzle, 0)
                sudoku_AC3 = Sudoku(puzzle, 1)
                ans_FC = sudoku_FC.solve()
                ans_AC3 = sudoku_AC3.solve()
                
                FC_Easy_Steps_list.append(sudoku_FC.totalSteps)
                AC3_Easy_Steps_list.append(sudoku_AC3.totalSteps)
                FC_Easy_AvDomain_list.append(sudoku_FC.totalSizeDomains / sudoku_FC.totalSteps)
                AC3_Easy_AvDomain_list.append(sudoku_AC3.totalSizeDomains / sudoku_AC3.totalSteps)
                FC_Easy_Time_list.append(sudoku_FC.timeTaken)
                AC3_Easy_Time_list.append(sudoku_AC3.timeTaken)


        # Parses in Intermediate puzzles and adds results into their respective lists
        with open("experiment_Intermediate_puzzles.txt", "r") as a_file:
            puzzle = [[0 for i in range(9)] for j in range(9)]
            AC3_Intermediate_Steps_list = []
            FC_Intermediate_Steps_list = []
            AC3_Intermediate_AvDomain_list = []
            FC_Intermediate_AvDomain_list = []
            AC3_Intermediate_Time_list = []
            FC_Intermediate_Time_list = []
            for line in a_file:
                stripped_line = line.strip()
                i, j = 0, 0
                for number in line:
                    if '0' <= number <= '9':
                        puzzle[i][j] = int(number)
                        j += 1
                        if j == 9:
                            i += 1
                            j = 0

                sudoku_FC = Sudoku(puzzle, 0)
                sudoku_AC3 = Sudoku(puzzle, 1)
                ans_FC = sudoku_FC.solve()
                ans_AC3 = sudoku_AC3.solve()
                
                FC_Intermediate_Steps_list.append(sudoku_FC.totalSteps)
                AC3_Intermediate_Steps_list.append(sudoku_AC3.totalSteps)
                FC_Intermediate_AvDomain_list.append(sudoku_FC.totalSizeDomains / sudoku_FC.totalSteps)
                AC3_Intermediate_AvDomain_list.append(sudoku_AC3.totalSizeDomains / sudoku_AC3.totalSteps)
                FC_Intermediate_Time_list.append(sudoku_FC.timeTaken)
                AC3_Intermediate_Time_list.append(sudoku_AC3.timeTaken)

        # Parses in Hard puzzles and adds results into their respective lists
        with open("experiment_Hard_puzzles.txt", "r") as a_file:
            puzzle = [[0 for i in range(9)] for j in range(9)]
            AC3_Hard_Steps_list = []
            FC_Hard_Steps_list = []
            AC3_Hard_AvDomain_list = []
            FC_Hard_AvDomain_list = []
            AC3_Hard_Time_list = []
            FC_Hard_Time_list = []
            for line in a_file:
                stripped_line = line.strip()
                i, j = 0, 0
                for number in line:
                    if '0' <= number <= '9':
                        puzzle[i][j] = int(number)
                        j += 1
                        if j == 9:
                            i += 1
                            j = 0

                sudoku_FC = Sudoku(puzzle, 0)
                sudoku_AC3 = Sudoku(puzzle, 1)
                ans_FC = sudoku_FC.solve()
                ans_AC3 = sudoku_AC3.solve()
                
                FC_Hard_Steps_list.append(sudoku_FC.totalSteps)
                AC3_Hard_Steps_list.append(sudoku_AC3.totalSteps)
                FC_Hard_AvDomain_list.append(sudoku_FC.totalSizeDomains / sudoku_FC.totalSteps)
                AC3_Hard_AvDomain_list.append(sudoku_AC3.totalSizeDomains / sudoku_AC3.totalSteps)   
                FC_Hard_Time_list.append(sudoku_FC.timeTaken)
                AC3_Hard_Time_list.append(sudoku_AC3.timeTaken)   



        # Add lists of results related to Simple puzzles
        total_result.append(FC_Simple_Steps_list)
        total_result.append(AC3_Simple_Steps_list)
        total_result.append(FC_Simple_AvDomain_list)
        total_result.append(AC3_Simple_AvDomain_list)
        total_result.append(FC_Simple_Time_list)
        total_result.append(AC3_Simple_Time_list)

        # Add lists of results related to Easy puzzles
        total_result.append(FC_Easy_Steps_list)
        total_result.append(AC3_Easy_Steps_list)
        total_result.append(FC_Easy_AvDomain_list)
        total_result.append(AC3_Easy_AvDomain_list)
        total_result.append(FC_Easy_Time_list)
        total_result.append(AC3_Easy_Time_list)

        # Add lists of results related to Intermediate puzzles
        total_result.append(FC_Intermediate_Steps_list)
        total_result.append(AC3_Intermediate_Steps_list)
        total_result.append(FC_Intermediate_AvDomain_list)
        total_result.append(AC3_Intermediate_AvDomain_list)
        total_result.append(FC_Intermediate_Time_list)
        total_result.append(AC3_Intermediate_Time_list)

        # Add lists of results related to Hard puzzles
        total_result.append(FC_Hard_Steps_list)
        total_result.append(AC3_Hard_Steps_list)
        total_result.append(FC_Hard_AvDomain_list)
        total_result.append(AC3_Hard_AvDomain_list)
        total_result.append(FC_Hard_Time_list)
        total_result.append(AC3_Hard_Time_list)

        # Rearrange them by row rather than column
        total_result_csv = zip(*total_result)

        # Write the rows into the CSV file
        writer.writerows(total_result_csv)