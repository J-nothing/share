import heapq
import math

def manhattan(p1, p2):
    """曼哈顿距离"""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def euclidean(p1, p2):
    """欧氏距离"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def chebyshev(p1, p2):
    """切比雪夫距离"""
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

def A_star_search(grid, start, goal, heuristic_type='manhattan'): 

    rows, cols = len(grid), len(grid[0])
    
    if heuristic_type == 'manhattan':
        h_func = lambda a, b: manhattan(a, b) * 10
    elif heuristic_type == 'euclidean':
        h_func = lambda a, b: euclidean(a, b) * 10
    elif heuristic_type == 'chebyshev':
        h_func = lambda a, b: chebyshev(a, b) * 10
    else:
        raise ValueError("heuristic_type must be 'manhattan', 'euclidean', or 'chebyshev'")

    open_list = []
    g_score = {start: 0}
    f_score = {start: h_func(start, goal)}
    came_from = {}
    close_list = set()
    # 向堆中插入元素
    heapq.heappush(open_list, (f_score[start], 0, start[0], start[1])) 

    # 8方向移动：上下左右 + 四个对角线
    directions = [
        (1, 0, 10),   # 下
        (-1, 0, 10),  # 上
        (0, 1, 10),   # 右
        (0, -1, 10),  # 左
        (1, 1, 14),   # 右下
        (1, -1, 14),  # 左下
        (-1, 1, 14),  # 右上
        (-1, -1, 14), # 左上
    ]

    while open_list:
        _, current_g, r, c = heapq.heappop(open_list) # 弹出堆中的最小值
        current = (r, c)

        if current in close_list:
            continue # 跳过本次循环
        close_list.add(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return g_score[goal], path, g_score, f_score

        for dr, dc, cost in directions:
            n_r = r + dr
            n_c = c + dc
            if 0 <= n_r < rows and 0 <= n_c < cols and grid[n_r][n_c] == 0:
                neighbor = (n_r, n_c)
                tentative_g = g_score[current] + cost

                if neighbor in close_list:
                    continue

                # 更新路径为当前这个更近更优的方案
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h = h_func(neighbor, goal) 
                    f = tentative_g + h           # f'(n) = g'(n) + h'(n)
                    f_score[neighbor] = f
                    heapq.heappush(open_list, (f, tentative_g, n_r, n_c))

    return float('inf'), [], {}, {}

if __name__ == "__main__":
    """
    测试
    """
    grid = [
        [0, 0, 0, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ] # 预设障碍物地图
    start = (0, 0)
    goal = (4, 4)
    cost, path, g_dict, f_dict = A_star_search(grid, start, goal)
    
    print("A* 结果:")
    print("总代价:", cost)
    path_visual = [(r+1, c+1) for (r, c) in path]
    print("路径:", path_visual)

    print("\n节点 f'(n) = g'(n) + h'(n) 验证:")
    for node in path:
        g = g_dict[node]
        h = manhattan(node, goal) * 10
        f = g + h
        print(f"({node[0]+1},{node[1]+1}): g'(n)={g}, h'(n)={h}, f'(n)={f}")