import numpy as np
import random
import time

# 城市坐标数据（34个城市）
cities_34 = [
    (116.46, 39.92),  # 北京 0
    (117.2, 39.13),   # 天津 1
    (121.48, 31.22),  # 上海 2
    (106.54, 29.59),  # 重庆 3
    (91.11, 29.97),   # 拉萨 4
    (87.68, 43.77),   # 乌鲁木齐 5
    (106.27, 38.47),  # 银川 6
    (111.65, 40.82),  # 呼和浩特 7
    (108.33, 22.84),  # 南宁 8
    (126.63, 45.75),  # 哈尔滨 9
    (125.35, 43.88),  # 长春 10
    (123.38, 41.8),   # 沈阳 11
    (114.48, 38.03),  # 石家庄 12
    (112.53, 37.87),  # 太原 13
    (101.74, 36.56),  # 西宁 14
    (117.36, 36.65),  # 济南 15
    (113.6, 34.76),   # 郑州 16
    (118.78, 32.04),  # 南京 17
    (117.27, 31.86),  # 合肥 18
    (120.19, 30.26),  # 杭州 19
    (119.3, 26.08),   # 福州 20
    (115.89, 28.68),  # 南昌 21
    (113.0, 28.21),   # 长沙 22
    (114.31, 30.52),  # 武汉 23
    (113.23, 23.16),  # 广州 24
    (121.5, 25.05),   # 台北 25
    (110.35, 20.02),  # 海口 26
    (103.73, 36.03),  # 兰州 27
    (108.95, 34.27),  # 西安 28
    (104.06, 30.67),  # 成都 29
    (106.71, 26.57),  # 贵阳 30
    (102.73, 25.04),  # 昆明 31
    (114.1, 22.2),    # 香港 32
    (113.33, 22.13)   # 澳门 33
]

# 城市名称（与 cities_34 顺序一致）
city_names = [
    "北京", "天津", "上海", "重庆", "拉萨", "乌鲁木齐", "银川", "呼和浩特",
    "南宁", "哈尔滨", "长春", "沈阳", "石家庄", "太原", "西宁", "济南",
    "郑州", "南京", "合肥", "杭州", "福州", "南昌", "长沙", "武汉",
    "广州", "台北", "海口", "兰州", "西安", "成都", "贵阳", "昆明",
    "香港", "澳门"
]

def path_to_city_names(path):
    """将路径（城市索引列表）转换为城市名称字符串"""
    return " → ".join(city_names[i] for i in path)

class TSPSolverCPU:
    def __init__(self, cities, pop_size=100, elite_ratio=0.25, mutation_rate=0.01, generations=500, crossover_rate=0.8):
        self.cities = cities
        self.num_cities = len(cities)
        self.pop_size = pop_size
        self.elite_size = int(pop_size * elite_ratio)
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.crossover_rate = crossover_rate
        
        self.dist_matrix = self._calculate_distance_matrix(cities)
        self.population = self._initialize_population()

    def _calculate_distance_matrix(self, cities):
        cities_array = np.array(cities, dtype=np.float32)
        diff = cities_array[:, np.newaxis, :] - cities_array[np.newaxis, :, :]
        return np.sqrt(np.sum(diff**2, axis=2))

    def _initialize_population(self):
        population = []
        paths_set = set()
        while len(population) < self.pop_size:
            path = list(range(1, self.num_cities))
            random.shuffle(path)
            path = [0] + path + [0]
            path_tuple = tuple(path)
            if path_tuple not in paths_set:
                paths_set.add(path_tuple)
                population.append(path)
        return np.array(population, dtype=np.int32)

    def _calculate_distance_batch_cpu(self, population):
        n_paths = population.shape[0]
        distances = np.zeros(n_paths, dtype=np.float32)
        for i in range(n_paths):
            path = population[i]
            from_cities = path[:-1]
            to_cities = path[1:]
            distances[i] = np.sum(self.dist_matrix[from_cities, to_cities])
        return distances

    def _calculate_fitness(self, population):
        distances = self._calculate_distance_batch_cpu(population)
        fitness = 1.0 / distances
        return fitness, distances

    def _roulette_wheel_selection(self, population, fitness):
        fitness_sum = np.sum(fitness)
        probs = fitness / fitness_sum
        selected_indices = np.random.choice(
            len(population),
            size=self.pop_size - self.elite_size,
            p=probs,
            replace=True
        )
        return population[selected_indices]

    def _order_crossover(self, parent1, parent2):
        """高效有序交叉（OX），保证路径合法且无重复"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()

        p1_mid = parent1[1:-1]
        p2_mid = parent2[1:-1]
        size = len(p1_mid)

        start, end = sorted(random.sample(range(size), 2))

        # Child 1
        child1_mid = [-1] * size
        child1_mid[start:end+1] = p1_mid[start:end+1]
        used1 = set(child1_mid[start:end+1])

        idx = (end + 1) % size
        for city in p2_mid:
            if city not in used1:
                while child1_mid[idx] != -1:
                    idx = (idx + 1) % size
                child1_mid[idx] = city
                idx = (idx + 1) % size

        # Child 2
        child2_mid = [-1] * size
        child2_mid[start:end+1] = p2_mid[start:end+1]
        used2 = set(child2_mid[start:end+1])

        idx = (end + 1) % size
        for city in p1_mid:
            if city not in used2:
                while child2_mid[idx] != -1:
                    idx = (idx + 1) % size
                child2_mid[idx] = city
                idx = (idx + 1) % size

        child1 = [0] + child1_mid + [0]
        child2 = [0] + child2_mid + [0]

        return np.array(child1, dtype=np.int32), np.array(child2, dtype=np.int32)

    def _swap_mutation(self, individual):
        if random.random() < self.mutation_rate:
            middle = individual[1:-1].copy()
            if len(middle) >= 2:
                i, j = random.sample(range(len(middle)), 2)
                middle[i], middle[j] = middle[j], middle[i]
                return np.array([0] + list(middle) + [0], dtype=np.int32)
        return individual

    def _inversion_mutation(self, individual):
        if random.random() < self.mutation_rate / 2:
            middle = individual[1:-1].copy()
            if len(middle) >= 2:
                i, j = sorted(random.sample(range(len(middle)), 2))
                middle[i:j+1] = middle[i:j+1][::-1]
                return np.array([0] + list(middle) + [0], dtype=np.int32)
        return individual

    def evolve(self):
        print(f" 参数: 种群={self.pop_size}, 精英={self.elite_size}({self.elite_size/self.pop_size*100:.0f}%)")
        print(f" 变异={self.mutation_rate}, 交叉={self.crossover_rate}, 迭代={self.generations}")
        
        start_time = time.time()

        for gen in range(self.generations):
            fitness, distances = self._calculate_fitness(self.population)
            best_distance = np.min(distances)

            if gen % 100 == 0 and gen > 0:
                avg_distance = np.mean(distances)
                print(f" 代 {gen:4d}: 最佳={best_distance:7.2f}, 平均={avg_distance:7.2f}")

            elite_indices = np.argsort(fitness)[-self.elite_size:]
            elite = self.population[elite_indices]

            parents = self._roulette_wheel_selection(self.population, fitness)

            new_population = [ind.copy() for ind in elite]
            while len(new_population) < self.pop_size:
                idx1, idx2 = random.sample(range(len(parents)), 2)
                parent1, parent2 = parents[idx1], parents[idx2]
                child1, child2 = self._order_crossover(parent1, parent2)
                
                child1 = self._swap_mutation(child1)
                child1 = self._inversion_mutation(child1)
                child2 = self._swap_mutation(child2)
                child2 = self._inversion_mutation(child2)
                
                new_population.append(child1)
                if len(new_population) < self.pop_size:
                    new_population.append(child2)

            self.population = np.array(new_population[:self.pop_size], dtype=np.int32)

        final_fitness, final_distances = self._calculate_fitness(self.population)
        best_idx = np.argmax(final_fitness)
        best_path = self.population[best_idx]
        best_distance = final_distances[best_idx]
        run_time = time.time() - start_time
        print(f" 结果: 最小开销={best_distance:.2f}, 时间={run_time:.2f}秒")
        return best_path, best_distance, run_time, False

def create_solver(cities, pop_size=100, elite_ratio=0.25, mutation_rate=0.01, generations=500, crossover_rate=0.8, force_cpu=True):
    return TSPSolverCPU(cities, pop_size, elite_ratio, mutation_rate, generations, crossover_rate)

def run_experiments():
    experiments = [
        {"id": 1, "pop_size": 80, "generations": 100, "crossover_rate": 0.6, "mutation_rate": 0.02},
        {"id": 2, "pop_size": 80, "generations": 100, "crossover_rate": 0.6, "mutation_rate": 0.03},
        {"id": 3, "pop_size": 80, "generations": 500, "crossover_rate": 0.6, "mutation_rate": 0.03},
        {"id": 4, "pop_size": 100, "generations": 500, "crossover_rate": 0.6, "mutation_rate": 0.03},
        {"id": 5, "pop_size": 100, "generations": 1000, "crossover_rate": 0.65, "mutation_rate": 0.035},
        {"id": 6, "pop_size": 100, "generations": 1000, "crossover_rate": 0.65, "mutation_rate": 0.03},
        {"id": 7, "pop_size": 100, "generations": 1000, "crossover_rate": 0.7, "mutation_rate": 0.04},
    ]
    results = []
    for exp in experiments:
        print(f"\n实验 {exp['id']}:")
        solver = create_solver(
            cities_34,
            pop_size=exp['pop_size'],
            elite_ratio=0.25,
            mutation_rate=exp['mutation_rate'],
            generations=exp['generations'],
            crossover_rate=exp['crossover_rate']
        )
        best_path, best_distance, run_time, used_gpu = solver.evolve()
        
        # 输出路径（城市编号和名称）
        print(f" 最优路径（编号）: {list(best_path)}")
        print(f" 最优路径（城市）: {path_to_city_names(best_path)}")
        
        results.append({
            "id": exp['id'],
            "pop_size": exp['pop_size'],
            "generations": exp['generations'],
            "crossover_rate": exp['crossover_rate'],
            "mutation_rate": exp['mutation_rate'],
            "distance": best_distance,
            "time": run_time,
            "used_gpu": used_gpu,
            "best_path": best_path 
        })
    return results

def display_results_table(results):
    print(f"{'':<10} {'1':<10} {'2':<10} {'3':<10} {'4':<10} {'5':<10} {'6':<10} {'7':<10}")
    print("-" * 85)
    pop_sizes = " ".join([f"{r['pop_size']:<10}" for r in results])
    print(f"{'种群规模':<10} {pop_sizes}")
    generations = " ".join([f"{r['generations']:<10}" for r in results])
    print(f"{'迭代次数':<10} {generations}")
    cross_rates = " ".join([f"{r['crossover_rate']:<10.2f}" for r in results])
    print(f"{'交叉概率':<10} {cross_rates}")
    mut_rates = " ".join([f"{r['mutation_rate']:<10.3f}" for r in results])
    print(f"{'突变概率':<10} {mut_rates}")
    distances = " ".join([f"{r['distance']:<10.2f}" for r in results])
    print(f"{'最小开销':<10} {distances}")
    run_times = " ".join([f"{r['time']:<10.2f}" for r in results])
    print(f"{'运行时间(秒)':<10} {run_times}")
    print("-" * 85)

def analyze_results(results):
    best_by_cost = min(results, key=lambda x: x['distance'])
    best_by_time = min(results, key=lambda x: x['time'])

    print("\n【本程序实验结果分析】")
    print("=" * 60)
    print(f"• 最优解（最小开销）: 实验 {best_by_cost['id']}, 开销 = {best_by_cost['distance']:.2f}")
    print(f"• 最快解（最短时间）: 实验 {best_by_time['id']}, 时间 = {best_by_time['time']:.2f} 秒")
    
    achieved = any(r['distance'] < 250 for r in results)
    best_overall = best_by_cost['distance']
    if achieved:
        print(f"✓ 目标达成：存在解 < 250（最佳为 {best_overall:.2f}）")
    else:
        print(f"✗ 未达成目标：所有解 ≥ 250（最佳为 {best_overall:.2f}）")

def main():

    print(f"城市数量: {len(cities_34)}")

    np.random.seed(42)
    random.seed(42)
    
    results = run_experiments()
    display_results_table(results)
    analyze_results(results)

if __name__ == "__main__":
    main()