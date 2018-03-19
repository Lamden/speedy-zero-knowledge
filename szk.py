from merk import MerkleTree
import random

def generate_puzzle(leaves):
    # create a random string of 1s and 0s the length of the leaves
    puzzle = ''.join([random.choice(['1', '0']) for i in range(len(leaves))])
    # turn that binary string into a byte string
    return int(puzzle, 2).to_bytes(len(leaves)//8, byteorder='big')

def solve_puzzle(puzzle, leaves):
    # turn the puzzle bytes into binary
    bpuzzle = bin(int.from_bytes(puzzle, byteorder='big'))[2:]
    while len(bpuzzle) < len(leaves):
        bpuzzle = '0' + bpuzzle
        
    new_leaves = []
    for i in range(len(leaves)):
        if bpuzzle[i] == '1':
            ii = int.from_bytes(leaves[i], byteorder='big')
            #print(i)
            ii >>= len(leaves[i])
            #ii = (1 << len(leaves[i])) - 1 - ii
            new_leaves.append(ii.to_bytes(len(leaves[i]), byteorder='big', signed=True))
        else:
            new_leaves.append(leaves[i])
            
    m = MerkleTree(new_leaves)
    return m.root()

def puzzle_set(leaves):
    s = 0
    puzzles = []
    # creates puzzles until every transaction has been NOT'd at least once
    # a NOT is designated by a 1, so we just have to do a cumulative AND on the new puzzles
    while s < pow(2,len(leaves)) - 1:
        p = generate_puzzle(leaves)
        puzzles.append(p)
        s = s | int.from_bytes(p, byteorder='big')
    return b''.join(puzzles)

def solution_set(puzzle_set, leaves):
    solutions = []
    while len(puzzle_set) > 0:
        if len(puzzle_set) >= len(leaves)//8:
            puzzle = puzzle_set[:len(leaves)//8]
            puzzle_set = puzzle_set[len(leaves)//8:]
        else:
            puzzle = puzzle_set
            puzzle_set = b''
        solutions.append(solve_puzzle(puzzle, leaves))
    return b''.join(solutions)

def verify_solutions(solution_set, puzzle_set, leaves):
    while len(puzzle_set) > 0:
        if len(puzzle_set) >= len(leaves)//8:
            puzzle = puzzle_set[:len(leaves)//8]
            puzzle_set = puzzle_set[len(leaves)//8:]
        else:
            puzzle = puzzle_set
            puzzle_set = b''
        real_solution = solve_puzzle(puzzle, leaves)
        test_solution = solution_set[:len(real_solution)]
        solution_set = solution_set[len(real_solution):]
        if test_solution != real_solution:
            return False
    return True