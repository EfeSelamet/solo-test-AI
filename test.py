from copy import deepcopy
from collections import deque
from typing import List, Tuple, Dict
import sys

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
DIRECTIONS = [(-1,0), (1,0), (0,-1), (0,1)]

# ---------------------------------------------------------

def render(show_numbers: bool = False) -> str:
    """Return a multi-line string showing the current board."""
    lines = []
    for r in range(ROWS):
        out = []
        for c in range(COLS):
            val = board[r][c]
            if val == -1:
                out.append("  ")
            else:
                if show_numbers:
                    out.append(f"{pos_to_index[(r, c)]:02d}")
                else:
                    out.append("x " if val == 1 else "o ")
        lines.append("".join(out))
    return "\n".join(lines)

# ---------------------------------------------------------

def peg_count() -> int:
    return sum(cell == 1 for row in board for cell in row)

# ---------------------------------------------------------
def serialize(board_state):
    """Convert a 7x7 board into a hashable tuple for visited-state checking."""
    return tuple(tuple(cell for cell in row) for row in board_state)


def generate_successor_states(current_board_state):
    """
    Generate all valid next board states from the current board state.
    Returns a list of tuples: (from_hole, to_hole, new_board_state)
    """
    successor_states = []

    for from_hole_index, (from_row, from_col) in index_to_pos.items():
        # Only consider holes that currently contain a peg
        if current_board_state[from_row][from_col] != 1:
            continue

        # Check all four orthogonal jump directions
        for row_step, col_step in DIRECTIONS:
            jumped_row = from_row + row_step
            jumped_col = from_col + col_step
            destination_row = from_row + 2 * row_step
            destination_col = from_col + 2 * col_step

            # Ensure destination is inside the board boundaries
            if not (0 <= destination_row < ROWS and 0 <= destination_col < COLS):
                continue

            # Check that the move is legal: jump over a peg into an empty hole
            if (
                current_board_state[jumped_row][jumped_col] == 1 and
                current_board_state[destination_row][destination_col] == 0
            ):
                # Create a deep copy of the board to apply the move
                new_board_state = deepcopy(current_board_state)

                # Apply move: remove source peg and jumped peg, place new peg
                new_board_state[from_row][from_col] = 0
                new_board_state[jumped_row][jumped_col] = 0
                new_board_state[destination_row][destination_col] = 1

                # Record the move and resulting board
                to_hole_index = pos_to_index[(destination_row, destination_col)]
                successor_states.append((from_hole_index, to_hole_index, new_board_state))

    return successor_states


def BFS():
    """
    Perform Breadth-First Search to find a sequence of moves
    that leaves only one peg in the center (hole 17).
    """
    # Start with the initial board configuration
    initial_board_state = deepcopy(board)
    initial_board_key = serialize(initial_board_state)

    # Each element in the frontier: (board_state, move_sequence)
    frontier_queue = deque([(initial_board_state, [])])
    visited_boards = {initial_board_key}

    while frontier_queue:
        current_board_state, current_move_sequence = frontier_queue.popleft()
        print(f"Exploring board with {sum(cell == 1 for row in current_board_state for cell in row)} pegs left.")
        print(render_board := "\n".join(
            "  ".join("x" if cell == 1 else "o" if cell == 0 else " " for cell in row)
            for row in current_board_state
        ))

        # Count remaining pegs
        remaining_pegs = sum(
            cell == 1 for row in current_board_state for cell in row
        )

        # Check for goal condition: one peg left, located at the center (row 3, col 3)
        if remaining_pegs == 1 and current_board_state[3][3] == 1:
            print("\n★ Goal reached! One peg remains in the center. ★")
            print(f"Total moves: {len(current_move_sequence)}")
            print("Move sequence (from → to):", current_move_sequence)
            return current_move_sequence

        # Explore all valid next states from this configuration
        for from_hole_index, to_hole_index, next_board_state in generate_successor_states(current_board_state):
            board_key = serialize(next_board_state)
            if board_key not in visited_boards:
                visited_boards.add(board_key)
                frontier_queue.append(
                    (next_board_state, current_move_sequence + [(from_hole_index, to_hole_index)])
                )

    # If no goal state was found
    print("\nNo solution found within BFS search limits.")
    return None


if __name__ == "__main__":
    BFS()