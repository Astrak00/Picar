import math
import numpy as np
import time

def astar(map: np.array, start: tuple[int, int], end: tuple[int, int], facing: int) -> list[tuple[int, int]]:
    num_cols, num_rows = map.shape
    # Check if start and end positions are within the map
    if not (0 <= start[0] < num_cols and 0 <= start[1] < num_rows):
        raise ValueError("Start position is out of bounds.")
    
    if not (0 <= end[0] < num_cols and 0 <= end[1] < num_rows):
        raise ValueError("End position is out of bounds.")
    
    # Check if start and end positions are not obstacles
    if map[start] == 1:
        raise ValueError("Start position is an obstacle.")
    if map[end] == 1:
        raise ValueError("End position is an obstacle.")
    
    # Check if facing direction is valid
    if facing not in [0, 90, 180, 270]:
        raise ValueError("Invalid facing direction.")


    movements = [
        (0, 1, 1),    # Up
        (1, 0, 1),    # Right
        (0, -1, 1),   # Down
        (-1, 0, 1),   # Left
    ]

    # Define the heuristic function
    def heuristic(a: tuple[int, int], b: tuple[int, int]) -> float:
        return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
    
    # Define the cost function
    def cost(a: tuple[int, int], b: tuple[int, int]) -> float:
        return 1 if a[0] == b[0] or a[1] == b[1] else math.sqrt(2)
    
    # Initialize the open and closed lists
    open_list = [start]
    closed_list = []

    # Initialize the g and f values
    g_values = {start: 0}
    f_values = {start: heuristic(start, end)}

    # Initialize the parent dictionary
    parent = {}

    # Main loop
    while open_list:
        # Get the current node
        current = min(open_list, key=lambda x: f_values[x])
        open_list.remove(current)
        closed_list.append(current)

        # Check if we have reached the end
        if current == end:
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            return path
        
        # Generate the children
        for dx, dy, cost in movements:
            new_pos = (current[0] + dx, current[1] + dy)
            # Check if the new position is within the map
            if not (0 <= new_pos[0] < num_cols and 0 <= new_pos[1] < num_rows):
                continue
            # Check if the new position is an obstacle
            if map[new_pos] == 1:
                continue
            # Check if the new position is in the closed list
            if new_pos in closed_list:
                continue
            
            # Calculate the new g value
            new_g = g_values[current] + cost
            # Check if the new position is in the open list
            if new_pos not in open_list:
                open_list.append(new_pos)
            elif new_g >= g_values[new_pos]:
                continue
            
            # Update the parent, g, and f values
            parent[new_pos] = current
            g_values[new_pos] = new_g
            f_values[new_pos] = new_g + heuristic(new_pos, end)

    # No path found
    return []




if "__main__" == __name__:
    # Define the map
    map = np.array([
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, ],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, ],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, ],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, ],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, ],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, ],
        [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, ],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ]
    ])

    # Define the start and end positions
    start = (0, 0)
    end = len(map) - 1, len(map[0]) - 1

    # Define the facing direction
    facing = 0

    # Find the path
    a = time.time()
    path = astar(map, start, end, facing)
    print("Time taken: ", time.time() - a)

    # Print the path
    # print("Path:")
    # for pos in path:
    #     print(pos)

    a = time.time()
    # Print the map with the path
    map_with_path = map.copy()
    for pos in path:
        map_with_path[pos] = 2
    
    print("Map with path:")

    for row in map_with_path:
        print("".join(str(cell) for cell in row))
    print("Time taken: ", time.time() - a)
