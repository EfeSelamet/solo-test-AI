"""
Standalone Peg Solitaire branching factor calculator.
Computes the MAXIMUM number of legal moves in any reachable state
from the standard English 7×7 board.

Representation:
    -1 = invalid / off-board
     0 = empty hole
     1 = peg
"""

from copy import deepcopy


# ----------------------------------------------------------------------
# 1. Build the standard 7×7 English board
# ----------------------------------------------------------------------

TEMPLATE = [
    "  xxx",
    "  xxx",
    "xxxxxxx",
    "xxxoxxx",
    "xxxxxxx",
    "  xxx",
    "  xxx"
]

ROWS, COLS = 7, 7

board = [[-1] * COLS for _ in range(ROWS)]
for r, row in enumerate(TEMPLATE):
    for c, ch in enumerate(row):
        if ch == "x":
            board[r][c] = 1
        elif ch == "o":
            board[r][c] = 0


# Moves allowed: up, down, left, right
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ----------------------------------------------------------------------
# 2. Legal moves
# ----------------------------------------------------------------------

def legal_moves(b):
    """
    Return all legal moves as ((r_from, c_from), (r_to, c_to)).
    """
    moves = []
    for r in range(ROWS):
        for c in range(COLS):
            if b[r][c] != 1:
                continue
            for dr, dc in DIRECTIONS:
                r_mid = r + dr
                c_mid = c + dc
                r_to = r + 2 * dr
                c_to = c + 2 * dc

                if not (0 <= r_mid < ROWS and 0 <= c_mid < COLS):
                    continue
                if not (0 <= r_to < ROWS and 0 <= c_to < COLS):
                    continue

                if b[r_mid][c_mid] == 1 and b[r_to][c_to] == 0:
                    moves.append(((r, c), (r_to, c_to)))
    return moves


# ----------------------------------------------------------------------
# 3. Apply move
# ----------------------------------------------------------------------

def apply_move(b, move):
    """
    Return a new board after applying a move.
    move = ((r_from, c_from), (r_to, c_to))
    """
    (r_from, c_from), (r_to, c_to) = move
    newb = [row[:] for row in b]

    r_mid = (r_from + r_to) // 2
    c_mid = (c_from + c_to) // 2

    newb[r_from][c_from] = 0
    newb[r_mid][c_mid] = 0
    newb[r_to][c_to] = 1

    return newb


# ----------------------------------------------------------------------
# 4. Serialize board for hashing
# ----------------------------------------------------------------------

def serialize(b):
    return tuple(tuple(row) for row in b)


# ----------------------------------------------------------------------
# 5. DFS exploration to compute maximum branching factor
# ----------------------------------------------------------------------

def compute_max_branching_factor():
    seen = set()
    stack = [deepcopy(board)]
    max_bf = 0

    count = 1
    
    while stack:
        print(max_bf, len(stack), count)
        count += 1
        b = stack.pop()
        key = serialize(b)

        if key in seen:
            continue
        seen.add(key)

        moves = legal_moves(b)
        bf = len(moves)

        if bf > max_bf:
            max_bf = bf

        for m in moves:
            child = apply_move(b, m)
            stack.append(child)

    return max_bf


# ----------------------------------------------------------------------
# 6. Run and output result
# ----------------------------------------------------------------------

if __name__ == "__main__":
    result = compute_max_branching_factor()
    print("\nMaximum branching factor (max legal moves in any state):")
    print(result)
