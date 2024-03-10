import z3
import sys
import itertools


class SudokuSolver(object):
    _valid_charset = "123456789"
    _vars = [[None for _ in range(9)] for _ in range(9)]
    _nums = [['.' for _ in range(9)] for _ in range(9)]
    _solver = None

    def __init__(self, puzzle=None):
        self._solver = z3.Solver()

        # Create variables
        for row in range(9):
            for col in range(9):
                v = z3.Int(f'x_{row}_{col}')
                self._vars[row][col] = v

        self.parse_puzzle(puzzle)
        self.add_constraints()

    def parse_puzzle(self, puzzle=None):
        for row in range(9):
            for col in range(9):
                x = puzzle[row][col]
                if x == '.':
                    continue
                elif x not in self._valid_charset:
                    raise ValueError("Unrecognized character")
                self._nums[row][col] = int(x)
                self._solver.add(self._vars[row][col] == int(x))

    def add_constraints(self):
        # forall i,j: x_i_j is in [1..9]
        for r in range(9):
            for c in range(9):
                v = self._vars[r][c]
                self._solver.add(v >= 1, v <= 9)

        # distinct per row and column
        for i in range(9):
            self._solver.add(z3.Distinct(self._vars[i]))
            self._solver.add(z3.Distinct([self._vars[r][i] for r in range(9)]))

        # distinct in each 3x3 grid
        offsets = list(itertools.product(range(0, 3), range(0, 3)))
        for r in range(0, 9, 3):
            for c in range(0, 9, 3):
                box = [self._vars[r+dr][c+dc] for dr, dc in offsets]
                self._solver.add(z3.Distinct(box))

    def solve(self):
        if self._solver.check() == z3.sat:
            m = self._solver.model()
            for r in range(9):
                for c in range(9):
                    self._nums[r][c] = m.evaluate(self._vars[r][c])
            return True
        return False

    def print_solution(self):
        print("Solution:")
        for line in self._nums:
            for e in line:
                print(e, end=' ')
            print()


def parse_puzzle_file(filename=None):
    puzzle = None
    with open(filename, 'r') as f:
        puzzle = ["".join(line.split()) for line in f.readlines()]
    print("Puzzle:")
    for line in puzzle:
        print(' '.join(line))
    print()
    return puzzle


def main(filename=None):
    puzzle = parse_puzzle_file(filename)
    sudoku = SudokuSolver(puzzle)
    if sudoku.solve():
        sudoku.print_solution()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <puzzle.in>")
        sys.exit(1)
    main(sys.argv[1])
