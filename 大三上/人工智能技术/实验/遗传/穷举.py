import matplotlib.pyplot as plt
import math
import itertools
import time
from typing import List

# 定义城市及其坐标
cities = {
    "北京": (116.46, 39.92),
    "天津": (117.2, 39.13),
    "上海": (121.48, 31.22),
    "重庆": (106.54, 29.59),
    "拉萨": (91.11, 29.97),
    "乌鲁木齐": (87.68, 43.77),
    "银川": (106.27, 38.47),
    "呼和浩特": (111.65, 40.82),
    "南宁": (108.33, 22.84),
    "哈尔滨": (126.63, 45.75)
}

# 计算两点之间的欧几里得距离
def euclidean_distance(city1, city2):
    x1, y1 = cities[city1]
    x2, y2 = cities[city2]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# 计算一条路径的总距离
def total_distance(path):
    distance = 0
    for i in range(len(path) - 1):
        distance += euclidean_distance(path[i], path[i + 1])
    distance += euclidean_distance(path[-1], path[0])  # 返回到起点
    return distance

# 设置 matplotlib 使用中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示问题

# TSP 可视化类
class TSPPlotter:
    def __init__(self, cities):
        self.cities = cities
        self.city_names = list(cities.keys())
        self.n_cities = len(cities)

    def plot_route(self, route: List[int]):
        """绘制路线图"""
        plt.figure(figsize=(15, 10))

        # 绘制所有城市点
        xs = [self.cities[self.city_names[i]][0] for i in route]
        ys = [self.cities[self.city_names[i]][1] for i in route]
        plt.scatter(xs, ys, c='red', s=50)

        # 添加城市名标签
        for i in range(len(route)):
            plt.annotate(self.city_names[route[i]], (xs[i], ys[i]), xytext=(5, 5),
                         textcoords='offset points')

        # 绘制路线
        for i in range(len(route)):
            city1 = route[i]
            city2 = route[(i + 1) % len(route)]
            plt.plot([xs[city1], xs[city2]], [ys[city1], ys[city2]], 'b-', alpha=0.6)

        plt.title('中国城市TSP最优路线')
        plt.xlabel('经度')
        plt.ylabel('纬度')
        plt.grid(True)
        plt.show()

# 实例化 TSP 可视化工具
plotter = TSPPlotter(cities)

# 记录开始时间
start_time = time.time()

# 穷举所有城市的排列
city_indices = list(range(len(cities)))  # 城市的索引列表
permutations = itertools.permutations(city_indices)

# 寻找最短路径
min_distance = float("inf")
best_route = None

for perm in permutations:
    distance = total_distance([plotter.city_names[i] for i in perm])
    if distance < min_distance:
        min_distance = distance
        best_route = perm

# 记录结束时间
end_time = time.time()

# 绘制最优路径图
plotter.plot_route(best_route)

# 输出最短路径及其长度
print("最短路径:", [plotter.city_names[i] for i in best_route])
print("最短路径长度:", min_distance)

# 输出计算时间
execution_time = end_time - start_time
print(f"计算最短路径的时间: {execution_time:.4f} 秒")