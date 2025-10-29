"""
Solo (Peg Solitaire) CLI game on the 7x7 English board shape.

Board pattern (holes):
   xxx
   xxx
xxxxxxx
xxxoxxx
xxxxxxx
   xxx
   xxx
"""

from typing import Tuple, Dict, List
import sys

# Board template: 'x' = peg hole, 'o' = empty hole, ' ' = no-slot
TEMPLATE = [
    "  xxx",
    "  xxx",
    "xxxxxxx",
    "xxxoxxx",
    "xxxxxxx",
    "  xxx",
    "  xxx"
]

# Build mapping: index -> (r,c) and (r,c) -> index for only valid holes
index_to_pos: Dict[int, Tuple[int, int]] = {}
pos_to_index: Dict[Tuple[int, int], int] = {}

idx = 1
for r, row in enumerate(TEMPLATE):
    for c, ch in enumerate(row):
        if ch in ("x", "o"):
            index_to_pos[idx] = (r, c)
            pos_to_index[(r, c)] = idx
            idx += 1
NUM_HOLES = idx - 1

# Initial state: True = peg present, False = empty
state: Dict[int, bool] = {}
for i, (r, c) in index_to_pos.items():
    state[i] = (TEMPLATE[r][c] == "x")

# Directions for orthogonal jumps: (dr, dc)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def render(show_numbers: bool = False) -> str:
    """Return a multi-line string showing the current board."""
    lines = []
    for r, row in enumerate(TEMPLATE):
        out = []
        for c, ch in enumerate(row):
            if ch == " ":
                out.append("  ")
            else:
                idx = pos_to_index[(r, c)]
                if show_numbers:
                    out.append(f"{idx:02d}")
                else:
                    out.append("X " if state[idx] else ". ")
        lines.append("".join(out))
    return "\n".join(lines)

def legal_moves() -> List[Tuple[int, int]]:
    """Return list of legal moves as (from_idx, to_idx)."""
    moves = []
    for i, occupied in state.items():
        if not occupied:
            continue
        r, c = index_to_pos[i]
        for dr, dc in DIRECTIONS:
            mid = (r + dr, c + dc)
            dest = (r + 2*dr, c + 2*dc)
            if mid in pos_to_index and dest in pos_to_index:
                mid_idx = pos_to_index[mid]
                dest_idx = pos_to_index[dest]
                if state[mid_idx] and not state[dest_idx]:
                    moves.append((i, dest_idx))
    return moves

def is_valid_move(frm: int, to: int) -> bool:
    if frm not in state or to not in state:
        return False
    if not state[frm] or state[to]:
        return False
    r1, c1 = index_to_pos[frm]
    r2, c2 = index_to_pos[to]
    dr, dc = r2 - r1, c2 - c1
    if abs(dr) == 2 and dc == 0:
        mid = (r1 + dr // 2, c1)
    elif abs(dc) == 2 and dr == 0:
        mid = (r1, c1 + dc // 2)
    else:
        return False
    if mid not in pos_to_index:
        return False
    mid_idx = pos_to_index[mid]
    return state[mid_idx]

def make_move(frm: int, to: int) -> bool:
    if not is_valid_move(frm, to):
        return False
    r1, c1 = index_to_pos[frm]
    r2, c2 = index_to_pos[to]
    mid = ((r1 + r2) // 2, (c1 + c2) // 2)
    mid_idx = pos_to_index[mid]
    state[frm] = False
    state[mid_idx] = False
    state[to] = True
    return True

def peg_count() -> int:
    return sum(state.values())

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

if __name__ == "__main__":
    try:
        main_loop()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted.")
        sys.exit(0)
