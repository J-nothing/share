import heapq

def dijkstra_search(grid, start, goal):
    # 获取地图网格行列数
    rows, cols = len(grid), len(grid[0])
    # 存储待考察的节点
    open_list = []
    # g'(n) 节点n距离起点的代价
    g_score = {start: 0}
    came_from = {}
    # 存储已考察完毕的节点
    close_list = set()

    heapq.heappush(open_list, (0, start[0], start[1]))

    # 待考察网格相对坐标和H，（x，y，G）；上下左右移动代价为10，对角线移动代价为14
    directions = [
        (1, 0, 10), (-1, 0, 10), (0, 1, 10), (0, -1, 10),
        (1, 1, 14), (1, -1, 14), (-1, 1, 14), (-1, -1, 14)
    ]

    while open_list:
        current_g, r, c = heapq.heappop(open_list)
        current = (r, c)

        if current in close_list:
            continue
        close_list.add(current)

        # 如果当前网格是目标网格，则回溯路径
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return g_score[goal], path

        # 探索相邻网格
        for dr, dc, cost in directions:
            n_r, n_c = r + dr, c + dc
            if 0 <= n_r < rows and 0 <= n_c < cols and grid[n_r][n_c] == 0:
                neighbor = (n_r, n_c)
                # 计算相邻网格的g'(n)值
                tentative_g = g_score[current] + cost
                # 如果当前网格的g'(n)值小于其他相邻网格的g'(n)值，则更新最优路径
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    came_from[neighbor] = current
                    heapq.heappush(open_list, (tentative_g, n_r, n_c))

    return float('inf'), []  # 无路径

if __name__ == "__main__":
    grid = [
        [0, 0, 0, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    start = (0, 0)
    goal = (4, 4)
    cost, path = dijkstra_search(grid, start, goal)
    print("Dijkstra 结果:")
    print("总代价:", cost)
    path_visual = [(r+1, c+1) for (r, c) in path]
    print("路径:", path_visual)