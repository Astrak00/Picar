import math
import numpy as np
import time

def astar(map: np.array, start: tuple[int, int], end: tuple[int, int], facing: int, num_obstacles_found: list[tuple[int, int]]) -> tuple[list[tuple[int, int]], float, list[str], tuple[int, int, int]]:
    num_cols:int
    num_rows:int

    num_cols, num_rows = map.shape

    # Input validation
    if not (0 <= start[0] < num_cols and 0 <= start[1] < num_rows):
        raise ValueError("Start position is out of bounds.")
    if not (0 <= end[0] < num_cols and 0 <= end[1] < num_rows):
        raise ValueError("End position is out of bounds.")
    if map[start] == 1:
        raise ValueError("Start position is an obstacle.")
    if map[end] == 1:
        raise ValueError("End position is an obstacle.")
    # Allow any facing that is a multiple of 30 degrees
    if facing % 30 != 0:
        raise ValueError("Invalid facing direction (must be a multiple of 30).")

    def get_turn_cost(current_facing: int, new_facing: int) -> float:
        """Calculate the cost of turning from current facing to new facing,
        using 30° increments (0.5 cost per 30°)."""
        angle_diff = abs(current_facing - new_facing)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        return (angle_diff / 30) * 0.5

    def heuristic(pos: tuple[int, int], goal: tuple[int, int]) -> float:
        """Combined Manhattan distance and obstacle proximity heuristic"""
        manhattan_distance = abs(goal[0] - pos[0]) + abs(goal[1] - pos[1])
        
        if num_obstacles_found == []:
            return manhattan_distance
        # Find the closest obstacle
        min_obstacle_distance = float('inf')
        for obstacle in num_obstacles_found:
            distance = abs(obstacle[0] - pos[0]) + abs(obstacle[1] - pos[1])
            if distance < min_obstacle_distance:
                min_obstacle_distance = distance

        
        # Combine the heuristics
        return manhattan_distance + (100 - min_obstacle_distance)

    def custom_round(x: float) -> int:
        """Round half-up (i.e. 0.5 -> 1, -0.5 -> -1)"""
        if x >= 0:
            return int(x + 0.5)
        else:
            return int(x - 0.5)

    # Initialize open and closed sets with state tuples (x, y, facing)
    start_state = (start[0], start[1], facing)
    open_set: set[tuple[int, int, int]] = {start_state}
    closed_set: set[tuple[int, int, int]] = set()

    came_from: set[tuple[int, int, int]] = {}
    g_score = {start_state: 0}
    f_score = {start_state: heuristic(start, end)}

    # Allowed turning options relative to the current facing (in degrees)
    turn_options = [-30, 0, 30]

    while open_set:
        current: tuple[int, int, int] = min(open_set, key=lambda s: f_score.get(s, float('inf')))

        # Check goal (position only, regardless of facing)
        if (current[0], current[1]) == end:
            final_state = current
            path: list[tuple[int, int]] = []
            movements: list[str] = []
            picar_movements: list[tuple[int, int, int]] = []
            state = current
            while state in came_from:
                path.append((state[0], state[1]))
                prev_state = came_from[state]
                if state[2] != prev_state[2]:
                    movements.append(f"Turn to {state[2] - prev_state[2]} degrees")
                    picar_movements.append((state[0], state[1], state[2] - prev_state[2] ))
                else :
                    picar_movements.append((state[0], state[1], 0))
                movements.append(f"Move to {(state[0], state[1])}")
                state = prev_state
            path.append((start[0], start[1]))
            movements.append(f"Start at {(start[0], start[1])}")
            final_cost = g_score[final_state]
            return path[::-1], final_cost, movements[::-1], picar_movements[::-1]

        open_set.remove(current)
        closed_set.add(current)

        current_pos = (current[0], current[1])
        current_facing = current[2]

        for turn in turn_options:
            new_facing = (current_facing + turn) % 360
            # Compute movement: move 1 cell in the direction of new_facing.
            # Using custom_round to approximate the next grid cell.
            dx = round(math.cos(math.radians(new_facing)))
            dy = round(math.sin(math.radians(new_facing)))
            next_pos = (current_pos[0] + dx, current_pos[1] + dy)

            # Skip if out of bounds or obstacle
            if not (0 <= next_pos[0] < num_cols and 0 <= next_pos[1] < num_rows):
                continue
            if map[next_pos] == 1:
                continue

            next_state = (next_pos[0], next_pos[1], new_facing)
            if next_state in closed_set:
                continue

            move_cost = 1  # base cost to move one cell forward
            turn_cost = get_turn_cost(current_facing, new_facing)
            tentative_g_score = g_score[current] + move_cost + turn_cost

            if next_state not in open_set:
                open_set.add(next_state)
            elif tentative_g_score >= g_score.get(next_state, float('inf')):
                continue

            came_from[next_state] = current
            g_score[next_state] = tentative_g_score
            f_score[next_state] = tentative_g_score + heuristic(next_pos, end)

    return [], float('inf'), []  # No path found

if __name__ == "__main__":
    path = False
    # Define the map (0: free, 1: obstacle)
    # map = np.array([
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    # ])
    while not path:
        try:

            map = np.random.choice([0, 1], size=(20, 20), p=[0.65, 0.35])

            # Test parameters
            start = (0, 0)
            end = (len(map) - 1, len(map[0]) - 1)
            facing = 0  # must be a multiple of 30

            start_time = time.time()
            path, total_cost, movements, picar_movements = astar(map, start, end, facing)

            if path:
                print(f"Path finding time: {time.time() - start_time:.3f} seconds")
                print(f"Total path cost: {total_cost:.2f} (including turning costs)")
                # Visualize the path on the map (2 indicates the path)
                map_with_path = map.copy()
                for pos in path:
                    map_with_path[pos] = 2

                print("\nMap with path (0: free, 1: obstacle, 2: path):")
                for row in map_with_path:
                    print("".join('.' if cell == 0 else str(cell) for cell in row))

                print("\nMovements taken:")
                for move in movements:
                    print(move)

                print("\nPicar movements:")
                print(picar_movements)
            else:
                print("No path found!")
        except ValueError as e:
            print(f"Error: {e}")
            continue
