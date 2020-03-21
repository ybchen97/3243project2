import sys
import copy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):

    global ROW, COL, BOX
    ROW = 0
    COL = 1
    BOX = 2

    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists

    def solve(self):

        # domain: 2D array of lists, where each list represents the domain of
        # each variable
        for row in self.puzzle:
            print(row)
        domains = self.init_domains()
        print()
        for row in domains:
            print(row)
        # state: literal state representation -> 2D array
        state = copy.deepcopy(self.puzzle)

        ans = run_back_tracking(state, domains)
        return ans

    def run_back_tracking(self, state, domains):
        initial_domain = domains
        if is_goal_state(state):
            return state
        # will brute force check the constraints and pick the most constraining and tie break, returning a tuple
        # object (row,col,box)
        var = select_unassigned_variable(state)

        # returns an ordered list containing the values starting from the least constraining value for that variable
        for value in order_domain_values(state, domains):
            if is_legal_assignment(value, var, state):
                state[var[ROW]][var[COL]] = value
                # inferences return list of domains
                inferences = inference(state, domains, var)

                if inferences != None:
                    domains = inferences
                    result = run_back_tracking(state, domains)

                    if result != None:
                        return result

            state[var[ROW]][var[COL]] = 0
            domains = initial_domain

        return None

    def is_goal_state(state):
        for row in state:
            min_value = min(row)
            if min_value == 0:
                return false
        return true

    def is_legal_assignment(value, variable, state):
        # state[variable[ROW]][variable[COL]] = value
        for other_num in state[variable[ROW]]:
            if other_num == value:
                return False
        for index in range(9):
            if state[index][variable[COL]] == value:
                return False
        if not is_legal_assignment(value, variable, state):
            return False
        return True

    def is_legal_box_assignment(value, var, state):
        box = var[BOX]
        box_row = box // 3
        box_col = col % 3

        for row in range(box_row*3, box_row*3+3):
            for col in range(box_col*3, box_col*3+3):
                if value == state[row][col]:
                return False
        return True

    def init_domains(self):
        # initialize as a 2d array of lists, representing domain of 1-9
        domains = [[[i for i in range(1,10)] for j in range(9)] for k in range(9)]

        # for each empty cell, check all 24 constraining neighbours, reduce
        # domain accordingly
        for row in range(9):
            for col in range(9):
                var = (row, col, self.get_box(row,col))
                val = self.puzzle[row][col]
                if val != 0:
                    domains[row][col] = 0 # assign domain value 0 if variable is assigned
                    continue

                domain = domains[row][col]
                domain = self.check_row(var, domain, self.puzzle)
                domain = self.check_col(var, domain, self.puzzle)
                domain = self.check_box(var, domain, self.puzzle)
                domains[row][col] = domain
        
        return domains

    def check_row(self, var, domain, state):
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
        box_row = row // 3
        box_col = col // 3
        box = box_row * 3 + box_col
        return box

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
