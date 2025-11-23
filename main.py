#Mehmet Efe Selamet 150122058
#Barış Korkmaz 150122016

import sys

import Astar
import bfs
import dfs
import HDFS
import iddfs
import maxrdfs
import maxUCS
import rdfs

if __name__ == "__main__":
    print("Enter Time Limit in seconds:")
    time_limit = int(input().strip())
    print("Select Game Variant:")
    print("Game A - Standard Peg Solitaire")
    print("Game B - Max Peg Solitaire")
    choice = int(input("Enter '1' or '2': ").strip())
    if choice == 1:
        print("Select which algorithm to use for Game A:")
        print("1. Breadth-First Search (BFS)")
        print("2. Depth-First Search (DFS)")
        print("3. Iterative Deepening DFS (IDDFS)")
        print("4. Randomized DFS (RDFS)")
        print("5. Heuristic DFS (HDFS)")
        Achoice = int(input("Enter choice (1-5): ").strip())
        if Achoice == 1:
            bfs.BFS(time_limit)
        elif Achoice == 2:
            dfs.DFS(time_limit)
        elif Achoice == 3:
            iddfs.IDDFS(time_limit)
        elif Achoice == 4:
            rdfs.RDFS(time_limit)
        elif Achoice == 5:
            HDFS.HDFS(time_limit)
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)
    elif choice == 2:
        print("Select which algorithm to use for Game B:")
        print("1. Maximal Depth-First Search (MaxRDFS)")
        print("2. Maximal Uniform Cost Search (MaxUCS)")
        print("3.A* Search (Astar)")
        Bchoice = int(input("Enter choice (1-3): ").strip())
        if Bchoice == 1:
            maxrdfs.MAXRDFS(time_limit)
        elif Bchoice == 2:
            maxUCS.MAXUCS(time_limit)
        elif Bchoice == 3:
            Astar.Astar(time_limit)
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)