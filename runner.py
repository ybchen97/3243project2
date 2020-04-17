#!/usr/bin/env python2

import sys
import os
import subprocess
import time

"""
HOW IT WORKS:
    ./runner.py <algo filename> <n equals num> <test input num>

For example, typing:
    ./runner.py sudoku.py 1

Translates to executing:
    python sudoku.py public_tests_p2_sudoku/input1.txt sudoku_input_1.out
"""

# argv[0] represents the name of the file that is being executed
# argv[1] represents name of input file
# argv[2] represents size n of the puzzle
# argv[3] represents input number of test case
if len(sys.argv) != 3:
    print("Wrong number of arguments! Try:\n{0} <algo filename> <test input num>".format(sys.argv[0]))

filename = sys.argv[1]
input_num = sys.argv[2]

input_path = "public_tests_p2_sudoku/input{n}.txt".format(n=input_num)
output_file = "{file}_input{n}.out".format(file=filename.split(".", 1)[0], n=input_num)

# clean previous outputs
if os.path.isfile(output_file):
    os.remove(output_file)
f = open(output_file, "w+")

# start a timer
# start = time.time()

# run program
print("Running {filename} on input{n}.txt".format(filename=filename, n=input_num))
subprocess.call(["python", filename, input_path, output_file])
# end = time.time()
# print("Completed.\nDuration: {0} seconds".format(round(end-start, 2)))

# check answer for correctness
answer_file = open("public_tests_p2_sudoku/output{n}.txt".format(n=input_num),"r")
result = []
answer = []
print("\nYour output is:")
for line in f:
    print line,
    result.append(line.strip())
print

for line in answer_file:
    answer.append(line.strip())

is_different = False

for index in range(len(result)):
    if result[index] != answer[index]:
        print("line {n} is different".format(n=index))    
        print "result:   " + str(result[index]),
        print "expected: " + str(answer[index]),
        is_different = True

if not is_different:
    print("The solution is correct!")

f.close()
answer_file.close()

