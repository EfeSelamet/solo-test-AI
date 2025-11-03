"""
Solo (Peg Solitaire) CLI game on the 7x7 English board shape.

Internal board:
  -1 = invalid / corner
   0 = empty hole
   1 = peg
"""

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

# Directions for orthogonal jumps: (dr, dc)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

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

def legal_moves() -> List[Tuple[int, int]]:
    """Return list of legal moves as (from_idx, to_idx)."""
    moves = []
    for frm, (r, c) in index_to_pos.items():
        if board[r][c] != 1:
            continue
        for dr, dc in DIRECTIONS:
            mid_r, mid_c = r + dr, c + dc
            to_r, to_c = r + 2*dr, c + 2*dc
            if (
                0 <= to_r < ROWS and 0 <= to_c < COLS and
                board[mid_r][mid_c] == 1 and
                board[to_r][to_c] == 0
            ):
                moves.append((frm, pos_to_index[(to_r, to_c)]))
    return moves

# ---------------------------------------------------------

def is_valid_move(frm: int, to: int) -> bool:
    if frm not in index_to_pos or to not in index_to_pos:
        return False
    r1, c1 = index_to_pos[frm]
    r2, c2 = index_to_pos[to]
    if board[r1][c1] != 1 or board[r2][c2] != 0:
        return False
    dr, dc = r2 - r1, c2 - c1
    if abs(dr) == 2 and dc == 0:
        mid = (r1 + dr // 2, c1)
    elif abs(dc) == 2 and dr == 0:
        mid = (r1, c1 + dc // 2)
    else:
        return False
    mid_r, mid_c = mid
    return board[mid_r][mid_c] == 1

# ---------------------------------------------------------

def make_move(frm: int, to: int) -> bool:
    if not is_valid_move(frm, to):
        return False
    r1, c1 = index_to_pos[frm]
    r2, c2 = index_to_pos[to]
    mid_r, mid_c = (r1 + r2) // 2, (c1 + c2) // 2

    board[r1][c1] = 0
    board[mid_r][mid_c] = 0
    board[r2][c2] = 1
    return True

# ---------------------------------------------------------

def peg_count() -> int:
    return sum(cell == 1 for row in board for cell in row)

def print_help():
    print("""
Commands:
  <from> <to>   : jump from hole <from> to <to> (e.g. "12 19")
  moves         : list legal moves
  showids       : show numbered board
  board         : show current board
  help          : show help
  quit / exit   : quit
""")

def print_status():
    print(render())
    print(f"Pegs remaining: {peg_count()}")
    lm = legal_moves()
    print(f"Legal moves: {len(lm)}")

def list_moves():
    lm = legal_moves()
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

def main_loop():
    print("Welcome to Solo (Peg Solitaire)!")
    print(render(show_numbers=True))
    print_help()
    while True:
        print("\nCurrent board:")
        print_status()
        if peg_count() == 1:
            print("\n★ You win! Only one peg remains. ★")
            break
        if not legal_moves():
            print("\nNo legal moves — game over.")
            break
        cmd = input("\nEnter command: ").strip().lower()
        if cmd in ("quit", "exit"):
            print("Goodbye!")
            break
        elif cmd == "help":
            print_help()
        elif cmd == "showids":
            print(render(show_numbers=True))
        elif cmd == "board":
            print(render())
        elif cmd == "moves":
            list_moves()
        else:
            parts = cmd.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                frm, to = map(int, parts)
                if make_move(frm, to):
                    print(f"Moved {frm} -> {to}")
                else:
                    print("Illegal move.")
            else:
                print("Unknown command. Type 'help'.")

# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        main_loop()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted.")
        sys.exit(0)
