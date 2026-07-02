import numpy as np
from typing import List, Tuple
import random
import math
import matplotlib.pyplot as plt
import time

# 设置 matplotlib 使用中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示问题

# 中国34个主要城市数据
cities_data = [
    ("北京", 116.46, 39.92),
    ("天津", 117.2, 39.13),
    ("上海", 121.48, 31.22),
    ("重庆", 106.54, 29.59),
    ("拉萨", 91.11, 29.97),
    ("乌鲁木齐", 87.68, 43.77),
    ("银川", 106.27, 38.47),
    ("呼和浩特", 111.65, 40.82),
    ("南宁", 108.33, 22.84),
    ("哈尔滨", 126.63, 45.75),
    ("长春", 125.35, 43.88),
    ("沈阳", 123.38, 41.8),
    ("石家庄", 114.48, 38.03),
    ("太原", 112.53, 37.87),
    ("西宁", 101.74, 36.56),
    ("济南", 117, 36.65),
    ("郑州", 113.65, 34.76),
    ("南京", 118.78, 32.04),
    ("合肥", 117.27, 31.86),
    ("杭州", 120.19, 30.26),
    ("福州", 119.3, 26.08),
    ("南昌", 115.89, 28.68),
    ("长沙", 113, 28.21),
    ("武汉", 114.31, 30.52),
    ("广州", 113.23, 23.16),
    ("台北", 121.5, 25.05),
    ("海口", 110.35, 20.02),
    ("兰州", 103.73, 36.03),
    ("西安", 108.95, 34.27),
    ("成都", 104.06, 30.67),
    ("贵阳", 106.71, 26.57),
    ("昆明", 102.73, 25.04),
    ("香港", 114.1, 22.2),
    ("澳门", 113.33, 22.13),
]

class TSPSolver:
    def __init__(self, cities: List[Tuple[str, float, float]]):
        self.cities = cities
        self.n_cities = len(cities) #计算城市数量
        self.distance_matrix = self._calculate_distance_matrix()

    #计算城市之间的欧式距离矩阵
    def _calculate_distance_matrix(self) -> np.ndarray:
        dist_matrix = np.zeros((self.n_cities, self.n_cities))
        for i in range(self.n_cities):
            for j in range(self.n_cities):
                if i != j:
                    x1, y1 = self.cities[i][1], self.cities[i][2]
                    x2, y2 = self.cities[j][1], self.cities[j][2]
                    dist_matrix[i][j] = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return dist_matrix

    #初始种群的创建（大小等于种群规模）
    def _create_initial_population(self, pop_size: int) -> List[List[int]]:
        population = []
        for _ in range(pop_size):
            route = list(range(self.n_cities))
            random.shuffle(route)
            population.append(route)
        return population

    #适应度函数，倒数
    def _calculate_fitness(self, route: List[int]) -> float:

        total_distance = 0
        for i in range(len(route)):
            from_city = route[i]
            to_city = route[(i + 1) % len(route)]
            total_distance += self.distance_matrix[from_city][to_city]
        return 1 / total_distance

    #使用轮盘赌选择算法，根据适应度值选择父母路径。
    def _select_parent(self, population: List[List[int]], fitness_scores: List[float]) -> List[int]:
        total_fitness = sum(fitness_scores)
        #计算选择概率，适应度越高，选择概率越大
        selection_probs = [f / total_fitness for f in fitness_scores]
        return random.choices(population, weights=selection_probs, k=1)[0]

    #通过双点交叉方法生成新路径（子代）
    def _crossover(self, parent1: List[int], parent2: List[int], crossover_rate: float) -> List[int]:
        #随机决定要不要交叉
        if random.random() > crossover_rate:
            return parent1.copy()

        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))
        child = [-1] * size
        child[start:end + 1] = parent1[start:end + 1]

        #将第二个父母填充到孩子剩余中（不重复城市）
        current_idx = (end + 1) % size
        for city in parent2:
            if city not in child:
                while child[current_idx] != -1:
                    current_idx = (current_idx + 1) % size
                child[current_idx] = city

        return child

    #通过交换两个城市位置实现变异
    def _mutate(self, route: List[int], mutation_rate: float) -> List[int]:
        if random.random() < mutation_rate:
            i, j = random.sample(range(len(route)), 2)
            route[i], route[j] = route[j], route[i]
        return route

    def solve(self, pop_size: int = 100,
              generations: int = 1000,
              mutation_rate: float = 0.01,
              crossover_rate: float = 1.0,
              elite_rate: float = 0.25) -> Tuple[List[int], float]:
        """求解TSP问题，添加父代保留率"""
        population = self._create_initial_population(pop_size)  #创建族群
        best_distance = float('inf')
        best_route = None    #记录当前最佳路径
        fitness_history = []   #保存每一代最好的

        for generation in range(generations):
            #相当于一个循环，大小为种群大小，结果是适应度
            fitness_scores = [self._calculate_fitness(route) for route in population]

            best_idx = fitness_scores.index(max(fitness_scores))
            current_best_route = population[best_idx]
            current_distance = 1 / fitness_scores[best_idx]#这一次大循环中，最好的（种群最好的）

            #保存当前最好以及本次最佳
            if current_distance < best_distance:
                best_distance = current_distance
                best_route = current_best_route.copy()
            fitness_history.append(max(fitness_scores))

            #精英策略，保留一部分直接作为下一代
            sorted_population = [x for _, x in sorted(zip(fitness_scores, population), reverse=True)]
            elite_count = int(elite_rate * pop_size)
            new_population = sorted_population[:elite_count]

            #通过轮盘赌选择父代，交叉变异 生成子代
            while len(new_population) < pop_size:
                parent1 = self._select_parent(population, fitness_scores)
                parent2 = self._select_parent(population, fitness_scores)
                child = self._crossover(parent1, parent2, crossover_rate)
                child = self._mutate(child, mutation_rate)
                new_population.append(child)

            population = new_population

            #每50代输出一次当前最优距离
            #if generation % 50 == 0:
               # print(f"Generation {generation}: Best distance = {best_distance:.2f}")

        end_time = time.time()

        plt.figure(figsize=(10, 6))
        plt.plot(fitness_history, label='适应度函数')
        plt.xlabel('代数')
        plt.ylabel('适应度')
        plt.title('适应度函数随代数的变化')
        plt.grid(True)
        plt.legend()
        plt.show()

        return best_route, best_distance, end_time

    #可视化过程
    def plot_route(self, route: List[int]):
        plt.figure(figsize=(15, 10))
        xs = [self.cities[i][1] for i in range(self.n_cities)]
        ys = [self.cities[i][2] for i in range(self.n_cities)]
        plt.scatter(xs, ys, c='red', s=50)

        #在城市旁边标注名换
        for i in range(self.n_cities):
            plt.annotate(self.cities[i][0], (xs[i], ys[i]), xytext=(5, 5), textcoords='offset points')

        for i in range(len(route)):
            city1 = route[i]
            city2 = route[(i + 1) % len(route)]
            plt.plot([self.cities[city1][1], self.cities[city2][1]],
                     [self.cities[city1][2], self.cities[city2][2]], 'b-', alpha=0.6)#0.6表示透明度

        plt.title('中国34个城市TSP最优路线')
        #plt.xlabel('X坐标')
        #plt.ylabel('Y坐标')
        plt.grid(True)
        plt.show()

def main():
    population_size = 100  # 种群规模
    generations = 1000  # 迭代次数
    crossover_rate = 0.6   # 交叉概率
    mutation_rate = 0.03     # 变异概率
    elite_rate = 0.25       # 精英保留率

    # 创建求解器实例并求解
    solver = TSPSolver(cities_data)
    start_time = time.time()

    # 求解TSP问题
    best_route, best_distance, end_time = solver.solve(
        pop_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate,
        elite_rate=elite_rate
    )

    # 打印结果
    for i in best_route:
        print(cities_data[i][0], end=" > ")
    print(cities_data[best_route[0]][0])  # 回到起点
    print(f"最小开销: {best_distance:.2f}    运行时间: {end_time - start_time:.2f}")
    # 绘制路线图
    solver.plot_route(best_route)

if __name__ == "__main__":
    main()