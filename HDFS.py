"""
Solo (Peg Solitaire) CLI game on the 7x7 English board shape.

Internal board:
  -1 = invalid / corner
   0 = empty hole
   1 = peg
"""

from typing import List, Tuple, Dict
import sys
from copy import deepcopy

# Board pattern (holes)
TEMPLATE = [
    "  xxx",
    "  xxx",
    "xxxxxxx",
    "xxxoxxx",
    "xxxxxxx",
    "  xxx",
    "  xxx"
]

class treenodes:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
ROWS, COLS = 7, 7

# Build the 7x7 state array
board: List[List[int]] = [[-1]*COLS for _ in range(ROWS)]
index_to_pos: Dict[int, Tuple[int, int]] = {}
pos_to_index: Dict[Tuple[int, int], int] = {}

idx = 1
for r, row in enumerate(TEMPLATE):
    for c, ch in enumerate(row):
        if ch in ("x", "o"):
            pos_to_index[(r, c)] = idx
            index_to_pos[idx] = (r, c)
            board[r][c] = 1 if ch == "x" else 0
            idx += 1

NUM_HOLES = idx - 1

# Directions for orthogonal jumps: (dr, dc)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# ---------------------------------------------------------

def render(current_board) -> str:
    """Return a multi-line string showing the current board."""
    lines = []
    for r in range(ROWS):
        out = []
        for c in range(COLS):
            val = current_board[r][c]
            if val == -1:
                out.append("  ")
            else:
                out.append("x " if val == 1 else "o ")
        lines.append("".join(out))
    return "\n".join(lines)

# ---------------------------------------------------------

def legal_moves(current_board) -> List[Tuple[int, int]]:
    """Return list of legal moves as (from_idx, to_idx)."""
    moves = []
    for frm, (r, c) in index_to_pos.items():
        if current_board[r][c] != 1:
            continue
        for dr, dc in DIRECTIONS:
            mid_r, mid_c = r + dr, c + dc
            to_r, to_c = r + 2*dr, c + 2*dc
            if (
                0 <= to_r < ROWS and 0 <= to_c < COLS and
                current_board[mid_r][mid_c] == 1 and
                current_board[to_r][to_c] == 0
            ):
                moves.append((frm, pos_to_index[(to_r, to_c)]))
    return moves

# ---------------------------------------------------------


def peg_count(current_board) -> int:
    return sum(cell == 1 for row in current_board for cell in row)


def print_status(current_board):
    print(render(current_board))
    print(f"Pegs remaining: {peg_count(current_board)}")
    lm = legal_moves(current_board)
    print(f"Legal moves: {len(lm)}")

def list_moves(current_board):
    lm = legal_moves(current_board)
    if not lm:
        print("No legal moves.")
        return
    by_from: Dict[int, List[int]] = {}
    for f, t in lm:
        by_from.setdefault(f, []).append(t)
    for f in sorted(by_from):
        tos = ", ".join(str(t) for t in sorted(by_from[f]))
        print(f"{f} -> {tos}")

# ---------------------------------------------------------
def serialize(board_state):
    """Convert a 7x7 board into a hashable tuple for visited-state checking."""
    return tuple(tuple(cell for cell in row) for row in board_state)

frontier = []
chechked_boards = []
explored = []

def generate_child_boards(current_board):
    """
    Given a board state, generate all possible child boards
    by applying every legal move once.
    Returns a list of (new_board, move) pairs,
    where move = (from_idx, to_idx).
    """
    children = []
    possible_moves = legal_moves(current_board.board)
    
    for from_idx, to_idx in possible_moves:
        # Copy the board so we don't modify the original
        new_board = deepcopy(current_board.board)
        
        # Apply the move on the copied board
        r1, c1 = index_to_pos[from_idx]
        r2, c2 = index_to_pos[to_idx]
        mid_r, mid_c = (r1 + r2) // 2, (c1 + c2) // 2
        
        # Execute the move (peg jump)
        new_board[r1][c1] = 0
        new_board[mid_r][mid_c] = 0
        new_board[r2][c2] = 1
        
        children.append(treenodes(new_board, current_board,(from_idx, to_idx)))
    
    return children

def print_path(node):
    path = []
    while node:
        path.append(node)
        node = node.parent
    for step in reversed(path):
        print_status(step.board)
        if step.move:
            print(f"Move: {step.move[0]} -> {step.move[1]}")
        print()


def DFS():
    first_copy = treenodes([row[:] for row in board], None)
    add_to_frontier(first_copy)
    chechked_boards.append(serialize(first_copy.board))
    while True:
        if not frontier:
            print("No solution found.")
            break
        print("\nCurrent board:")
        node = frontier.pop()
        explored.append(node)
        chechked_boards.append(serialize(node.board))
        print_status(node.board)
        
        
        if peg_count(node.board) == 1:
            print("\n★ You win! Only one peg remains. ★")
            print_path(node)
            break
        '''
        if not legal_moves(node.board):
            print("\n★ You win! Max peg remains. ★")
            break
        '''
        
        list_moves(node.board)
        #children = [child for child, move in generate_child_boards(node)]
        children = generate_child_boards(node)
        children = heuristic_order(children)
        
        for child in children:
            serialized_child = serialize(child.board)
            if serialized_child not in explored:
                add_to_frontier(child)
                
def heuristic_order(children):
    return reversed(sorted(children, key=lambda x: 1/(len(legal_moves(x.board)) + 1)))

#---------------------------------------------------------
def add_to_frontier(state):
    if state not in chechked_boards:
        frontier.append(state)

#---------------------------------------------------------
#Heuristic the cost of the child node is 1/(number of moves available)
if __name__ == "__main__":
    try:
        DFS()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted.")
        sys.exit(0)



