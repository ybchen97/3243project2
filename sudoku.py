import sys
import copy
import random
from collections import deque


# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt


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

    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.variable_heuristic = self.MOST_CONSTRAINED_VAR
        self.value_heuristic = self.LEAST_CONSTRAINING_VAL
        self.inference_heuristic = self.FORWARD_CHECKING
        self.count = 0

    def solve(self):
        domains = self.get_initial_fc_domains(self.puzzle)

        # self.print_domains(self.puzzle, domains)
        state = copy.deepcopy(self.puzzle)

        ans = self.run_back_tracking(state, domains)
        print("Backtrack called {} times".format(self.count))

        if ans is None:
            return "Did not solve :("

        return ans

    def run_back_tracking(self, state, domains):
        self.count += 1
        # self.print_domains(state, domains)
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
                # values_removed contains the values that were removed from each variable's domains during inference
                # Original domains is retrieved by taking the union of this set and the modified domains
                values_removed = {(var_row, var_col): domains[var_row][var_col]}
                domains[var_row][var_col] = {value}

                # INFERENCE HEURISTIC HERE
                # self.inference directly modifies domains
                if self.inference(state, domains, var, value, values_removed) is not None:
                    result = self.run_back_tracking(state, domains)

                    if result is not None:
                        return result

                # Restore original domains
                self.restore_domains(domains, values_removed)

            state[var_row][var_col] = 0

        return None

    """
    UTILITY FUNCTIONS
    """
    def restore_domains(self, domains, values_removed):
        for key in values_removed:
            row = key[self.ROW]
            col = key[self.COL]
            # Union of sets to restore the original domain
            domains[row][col] |= values_removed[key]

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

            for i in range(box_row, box_row + 3):
                for j in range(box_col, box_col + 3):
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

            for i in range(box_row, box_row + 3):
                for j in range(box_col, box_col + 3):
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
        # check row and col constraints
        for i in range(9):
            # Note: variable is not yet assigned during this function call
            if state[row][i] == value or state[i][col] == value:
                return False

        # check box constraints
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3

        for row in range(box_row, box_row + 3):
            for col in range(box_col, box_col + 3):
                if value == state[row][col]:
                    return False

        return True

    def get_initial_domains(self, state):
        initial_domains = [[{1, 2, 3, 4, 5, 6, 7, 8, 9} for i in range(9)] for j in range(9)]
        for row in range(9):
            for col in range(9):
                if state[row][col] != 0:
                    initial_domains[row][col] = {state[row][col]}
        return initial_domains

    def get_initial_fc_domains(self, state):
        initial_domains = [[{1, 2, 3, 4, 5, 6, 7, 8, 9} for i in range(9)] for j in range(9)]
        for row in range(9):
            for col in range(9):
                var = (row, col)
                val = state[row][col]
                if val != 0:
                    initial_domains[row][col] = {val}
                    self.forward_checking(initial_domains, var, val, {})
        return initial_domains

    """
    Variable Heuristics
    """
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

    """
    Value Heuristics
    """
    def order_domain_values(self, state, domains, var):
        """
        For now just randomly sort the domain
        """
        if self.value_heuristic == self.RANDOM_SHUFFLE:
            new_domain = domains[var[self.ROW]][var[self.COL]]
            random.shuffle(list(new_domain))
            return new_domain
        elif self.value_heuristic == self.LEAST_CONSTRAINING_VAL:
            return self.least_constraining_value(state, domains, var)

    def least_constraining_value(self, state, domains, var):
        """
        Returns domain sorted by least conflicts
        """
        row, col = var
        domain = domains[row][col]
        sorted_domain = []
        # Whether we get all neighbours or only unassigned neighbours does not matter to forward checking
        neighbours = self.get_unassigned_neighbours(var, state, get_all_neighbours=True)
        for value in domain:
            conflicts = 0
            for neighbour in neighbours:
                row, col = neighbour
                neighbour_domain = domains[row][col]
                if value in neighbour_domain:
                    conflicts += 1
            sorted_domain.append((value, conflicts))

        sorted_domain = sorted(sorted_domain, key=lambda pair: pair[1])
        return [pair[0] for pair in sorted_domain]

    """
    Inference
    """
    def inference(self, state, domains, var, value, values_removed):
        """
        For now just remove the domain of the current var and return the new
        domains. NOTE: DEEPCOPY THE DOMAIN!!
        """
        if self.inference_heuristic == self.FORWARD_CHECKING:
            return self.forward_checking(domains, var, value, values_removed)
        elif self.inference_heuristic == self.AC3:
            row, col = var
            new_domains = self.ac3(state, domains, values_removed)
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
                # self.print_domains(state, domains)
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
        for x_val in set(x_domain):
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

    def forward_checking(self, domains, var, value, values_removed):
        """
        Returns the domains of a particular state
        """
        domains = self.check_row(var, domains, value, values_removed)
        if domains is None:
            return None
        domains = self.check_col(var, domains, value, values_removed)
        if domains is None:
            return None
        domains = self.check_box(var, domains, value, values_removed)
        if domains is None:
            return None

        return domains

    def check_row(self, var, domains, value, values_removed):
        """
        Returns the reduced domains after checking row constraints
        """
        row, col = var
        for i in range(9):
            domain = domains[row][i]
            if i != col and value in domain:
                domain.remove(value)
                if (row, i) not in values_removed:
                    values_removed[(row, i)] = {value}
                else:
                    values_removed[(row, i)].add(value)
                if len(domain) == 0:
                    return None
        return domains

    def check_col(self, var, domains, value, values_removed):
        """
        Returns the reduced domains after checking col constraints
        """
        row, col = var
        for i in range(9):
            domain = domains[i][col]
            if i != row and value in domain:
                domain.remove(value)
                if (i, col) not in values_removed:
                    values_removed[(i, col)] = {value}
                else:
                    values_removed[(i, col)].add(value)
                if len(domain) == 0:
                    return None
        return domains

    def check_box(self, var, domains, value, values_removed):
        """
        Returns the reduced domains after checking box constraints
        """
        row, col = var
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3

        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                domain = domains[i][j]
                if (i, j) != var and value in domain:
                    domain.remove(value)
                    if (i, j) not in values_removed:
                        values_removed[(i, j)] = {value}
                    else:
                        values_removed[(i, j)].add(value)
                    if len(domain) == 0:
                        return None

        return domains

    def print_domains(self, state, domains):
        print("State:\n")
        for i in range(9):
            print(state[i])

        print("\nDomains:\n")
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
