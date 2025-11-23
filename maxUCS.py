from typing import List, Tuple, Dict
import sys
from copy import deepcopy
import bisect
import winsound
import time




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
    def __init__(self, board, parent=None, move=None, cost=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.cost = cost

ROWS, COLS = 7, 7

# Build the 7x7 state array from the template
# place 1 to represent peg, 0 to represent empty hole, -1 to represent invalid position
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
#for printing the board
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
#claculates the possblle legal moves so the algorithm can choose from them
#cycles through all positions and checks the one with pegs in them
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

# counts the number of pegs remaining on the board
def peg_count(current_board) -> int:
    return sum(cell == 1 for row in current_board for cell in row)


def print_status(current_board):
    print(render(current_board))
    print(f"Pegs remaining: {peg_count(current_board)}")
    lm = legal_moves(current_board)
    print(f"Legal moves: {len(lm)}")

#prints the legal moves
#it's not used in algorithm just visualization
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
#converts the board to a tuple of tuples for easier comparison and storage in lists
def serialize(board_state):
    return tuple(tuple(cell for cell in row) for row in board_state)

priority_queue = []
pq_costs = []
chechked_boards = []
explored = []

#copies the board and applies all possible legal moves to generate child boards
def generate_child_boards(current_board):
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
        
        child_cost = current_board.cost + 1  # Example cost function: increment by 1 per move
        
        children.append(treenodes(new_board, current_board,(from_idx, to_idx), child_cost))
    
    return children

#to print the path from initial state to goal state after solution is found
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

def MAXUCS(limit_time):
    start = time.monotonic()
    nodes = 0
    max_frontier_size = 0
    
    first_copy = treenodes([row[:] for row in board], None,0)
    priority_queue.append(first_copy)
    pq_costs.append(first_copy.cost)
    chechked_boards.append(serialize(first_copy.board))
    
    #remove node from priority queue with lowest cost
    #continue until solution is found or time limit exceeded
    #if the current board has no legal moves it's a win
    #else generate child boards and add to priority queue if not already explored
    #it basically works like BFS but uses priority queue instead of normal queue but it doesn't change the outcome for max pegs
    while True:
        nodes+= 1
        frontier_size = len(priority_queue)
        if frontier_size > max_frontier_size:
            max_frontier_size = frontier_size
        elapsed = time.monotonic() - start
        if elapsed > limit_time:
            print("Time limit exceeded. No solution found.")
            break
        
        if not priority_queue:
            print("No solution found.")
            break
        print("\nCurrent board:")
        node = priority_queue.pop(0)
        pq_costs.pop(0)
        explored.append(node)
        chechked_boards.append(serialize(node.board))
        print_status(node.board)
        
        '''
        if peg_count(node.board) == 1:
            print("\n★ You win! Only one peg remains. ★")
            print_path(node)
            break
        '''
        if not  legal_moves(node.board):
            print("\n★ You win! Max peg remains. ★")
            print_path(node)
            print("\n Game Variant B maxUCS")
            print("Elapsed time: {:.2f} seconds".format(elapsed))
            print("Total nodes explored:", nodes)
            print("Frontier size at solution:", max_frontier_size)
            print("Max pegs remaining: {}".format(peg_count(node.board)))
            break
        
        if peg_count(node.board) == 25:
            duration = 1000  # milliseconds
            freq = 440  # Hz
            winsound.Beep(freq, duration)
        
        list_moves(node.board)
        children = generate_child_boards(node)
        for child in children:
            serialized_child = serialize(child.board)
            if serialized_child not in explored:
                add_to_priority_queue(child)


#---------------------------------------------------------
#to make sure no duplicate boards are added to priority queue
#nodes are added based on their cost ascenndingly
def add_to_priority_queue(state):
    serialized_board = serialize(state.board)
    if serialized_board not in chechked_boards:
        index = bisect.bisect_left(pq_costs, state.cost)
        priority_queue.insert(index, (state))
        pq_costs.insert(index, state.cost)


#---------------------------------------------------------

if __name__ == "__main__":
    try:
        MAXUCS()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted.")
        sys.exit(0)
        




