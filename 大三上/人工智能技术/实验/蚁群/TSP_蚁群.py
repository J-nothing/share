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
    """将路径转换为城市中文名称"""
    return " → ".join(city_names[i] for i in path)

def format_path_for_display(path):
    """格式化路径显示"""
    names = [city_names[i] for i in path]
    formatted = ""
    for i in range(0, len(names), 6):
        formatted += "  " + " → ".join(names[i:i+6]) + "\n"
    return formatted.strip()

class ACO_TSP_Solver:
    """
    蚁群算法求解TSP问题
    """
    def __init__(self, cities, num_ants=50, alpha=1.0, beta=3.0, 
                 rho=0.3, Q=100.0, max_iter=200, seed=None):
        """
        初始化蚁群算法参数
        
        参数:
        cities: 城市坐标列表
        num_ants: 蚂蚁数量
        alpha: 信息素重要性因子
        beta: 启发信息重要性因子
        rho: 信息素挥发系数
        Q: 信息素总量常数
        max_iter: 最大迭代次数
        seed: 随机种子，如果为None则不设置特定种子
        """
        self.cities = np.array(cities, dtype=np.float32)
        self.num_cities = len(cities)
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.Q = Q
        self.max_iter = max_iter
        
        # 为本次实验设置随机种子（如果提供了种子）
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        # 计算距离矩阵
        self.distance_matrix = self._calc_distance_matrix()
        
        # 初始化启发信息矩阵
        self.heuristic_matrix = np.zeros_like(self.distance_matrix)
        np.fill_diagonal(self.heuristic_matrix, 0)  # 对角线设为0
        
        # 避免除以0
        for i in range(self.num_cities):
            for j in range(self.num_cities):
                if i != j and self.distance_matrix[i, j] > 0:
                    self.heuristic_matrix[i, j] = 1.0 / self.distance_matrix[i, j]
        
        # 初始化信息素矩阵
        self.pheromone_matrix = np.ones((self.num_cities, self.num_cities))
        np.fill_diagonal(self.pheromone_matrix, 0)  # 对角线设为0
        
        # 存储最佳解
        self.best_path = None
        self.best_distance = float('inf')
        
        # 记录每代最佳距离
        self.best_distances_history = []
        self.avg_distances_history = []
    
    def _calc_distance_matrix(self):
        """计算城市间的距离矩阵"""
        diff = self.cities[:, np.newaxis, :] - self.cities[np.newaxis, :, :]
        return np.sqrt(np.sum(diff**2, axis=2))
    
    def _calc_path_distance(self, path):
        """计算路径总距离"""
        distance = 0.0
        for i in range(len(path) - 1):
            distance += self.distance_matrix[path[i], path[i+1]]
        return distance
    
    def _select_next_city(self, current_city, visited_cities):
        """
        使用轮盘赌选择法，根据概率选择下一个城市
        """
        allowed_cities = [city for city in range(self.num_cities) 
                         if city not in visited_cities]
        
        if not allowed_cities:
            return None
        
        # 计算所有可选城市的概率
        probabilities = []
        for city in allowed_cities:
            pheromone = self.pheromone_matrix[current_city, city] ** self.alpha
            heuristic = self.heuristic_matrix[current_city, city] ** self.beta
            probabilities.append(pheromone * heuristic)
        
        # 处理概率为0的情况
        probabilities = np.array(probabilities)
        if np.sum(probabilities) == 0:
            probabilities = np.ones_like(probabilities) / len(probabilities)
        else:
            probabilities = probabilities / np.sum(probabilities)
        
        # 轮盘赌选择
        selected_idx = np.random.choice(range(len(allowed_cities)), p=probabilities)
        return allowed_cities[selected_idx]
    
    def _construct_solution(self, ant_id):
        """
        一只蚂蚁构建一条完整的路径
        """
        # 随机选择起始城市
        start_city = np.random.randint(0, self.num_cities)
        
        path = [start_city]
        visited_cities = set([start_city])
        current_city = start_city
        
        # 构建完整路径
        for _ in range(self.num_cities - 1):
            next_city = self._select_next_city(current_city, visited_cities)
            if next_city is None:
                # 如果没有可选城市，随机选择一个未访问的城市
                unvisited = [c for c in range(self.num_cities) if c not in visited_cities]
                next_city = np.random.choice(unvisited)
            
            path.append(next_city)
            visited_cities.add(next_city)
            current_city = next_city
        
        # 返回起始城市，形成回路
        path.append(start_city)
        return path
    
    def _update_pheromone(self, ant_paths, ant_distances):
        """
        更新信息素矩阵
        1. 信息素挥发
        2. 蚂蚁在路径上留下信息素
        """
        n = self.num_cities
        
        # 信息素挥发
        self.pheromone_matrix *= (1.0 - self.rho)
        
        # 防止信息素过小
        min_pheromone = 0.001
        self.pheromone_matrix = np.maximum(self.pheromone_matrix, min_pheromone)
        
        # 每只蚂蚁在路径上留下信息素
        for ant_id in range(self.num_ants):
            path = ant_paths[ant_id]
            distance = ant_distances[ant_id]
            
            # 信息素增量 Δτ = Q / L
            delta_pheromone = self.Q / distance
            
            # 在路径的每条边上增加信息素
            for i in range(len(path) - 1):
                from_city = path[i]
                to_city = path[i+1]
                
                # 对称更新（路径是无向的）
                self.pheromone_matrix[from_city, to_city] += delta_pheromone
                self.pheromone_matrix[to_city, from_city] += delta_pheromone
    
    def solve(self, verbose=True):
        """
        运行蚁群算法求解TSP问题
        """        
        start_time = time.time()
        
        for iteration in range(self.max_iter):
            # 存储所有蚂蚁的路径和距离
            ant_paths = []
            ant_distances = []
            
            # 每只蚂蚁构建一条路径
            for ant_id in range(self.num_ants):
                path = self._construct_solution(ant_id)
                distance = self._calc_path_distance(path)
                
                ant_paths.append(path)
                ant_distances.append(distance)
                
                # 更新全局最优解
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_path = path.copy()
            
            # 更新信息素
            self._update_pheromone(ant_paths, ant_distances)
            
            # 记录本代统计信息
            best_in_iteration = min(ant_distances)
            avg_in_iteration = np.mean(ant_distances)
            self.best_distances_history.append(best_in_iteration)
            self.avg_distances_history.append(avg_in_iteration)
            
            # 每50代输出一次进度
            if verbose and (iteration % 50 == 0 or iteration == self.max_iter - 1):
                print(f"迭代 {iteration:4d}: 最佳={best_in_iteration:7.2f}, 平均={avg_in_iteration:7.2f}, 全局最佳={self.best_distance:7.2f}")
        
        run_time = time.time() - start_time
        
        print(f"求解完成!")
        print(f"运行时间: {run_time:.2f}秒")
        print(f"最优路径距离: {self.best_distance:.2f}")
        
        # 详细输出最优路径
        if self.best_path:
            print(f"\n最优路径详情:")
            print(f"路径长度: {len(self.best_path)} 个节点 (包含返回起点)")
            print(f"路径索引: {self.best_path}")
            
            # 计算并显示每段距离
            print(f"\n各段距离:")
            total_distance = 0
            for i in range(len(self.best_path) - 1):
                from_city = self.best_path[i]
                to_city = self.best_path[i+1]
                segment_dist = self.distance_matrix[from_city, to_city]
                total_distance += segment_dist
                print(f"  {city_names[from_city]} → {city_names[to_city]}: {segment_dist:.2f}")
            
            print(f"总距离: {total_distance:.2f}")
            
            # 显示完整路径
            print(f"\n最优路径:")
            print(format_path_for_display(self.best_path))
        
        return self.best_path, self.best_distance, run_time


def run_parameter_experiments():
    """
    运行不同参数组合的实验
    """
    
    # 实验参数设置（参考PDF中的建议范围）
    experiments = [
        # 基础实验
        {"id": 1, "num_ants": 20, "alpha": 1.0, "beta": 2.0, "rho": 0.3, "Q": 100, "max_iter": 200},
        
        # 调整蚂蚁数量
        {"id": 2, "num_ants": 10, "alpha": 1.0, "beta": 2.0, "rho": 0.3, "Q": 100, "max_iter": 200},
        {"id": 3, "num_ants": 50, "alpha": 1.0, "beta": 2.0, "rho": 0.3, "Q": 100, "max_iter": 200},
        
        # 调整信息素因子α
        {"id": 4, "num_ants": 20, "alpha": 0.5, "beta": 2.0, "rho": 0.3, "Q": 100, "max_iter": 200},
        {"id": 5, "num_ants": 20, "alpha": 3.0, "beta": 2.0, "rho": 0.3, "Q": 100, "max_iter": 200},
        
        # 调整启发函数因子β
        {"id": 6, "num_ants": 20, "alpha": 1.0, "beta": 0.5, "rho": 0.3, "Q": 100, "max_iter": 200},
        {"id": 7, "num_ants": 20, "alpha": 1.0, "beta": 5.0, "rho": 0.3, "Q": 100, "max_iter": 200},
        
        # 调整信息素挥发系数ρ
        {"id": 8, "num_ants": 20, "alpha": 1.0, "beta": 2.0, "rho": 0.1, "Q": 100, "max_iter": 200},
        {"id": 9, "num_ants": 20, "alpha": 1.0, "beta": 2.0, "rho": 0.5, "Q": 100, "max_iter": 200},
        
        # 调整信息素总量Q
        {"id": 10, "num_ants": 20, "alpha": 1.0, "beta": 2.0, "rho": 0.3, "Q": 10, "max_iter": 200},
        {"id": 11, "num_ants": 20, "alpha": 1.0, "beta": 2.0, "rho": 0.3, "Q": 500, "max_iter": 200},


        {"id": 12, "num_ants": 50, "alpha": 1.0, "beta": 3.0, "rho": 0.2, "Q": 200, "max_iter": 300},
    ]
    
    results = []
    
    for exp in experiments:
        print(f"实验 {exp['id']}:")
        
        # 随机种子：使用当前时间和实验ID的组合，确保每次运行每个实验都有不同的随机种子
        current_time_ns = time.time_ns()  
        random_seed_value = int(current_time_ns % (2**32)) + exp['id']
        
        # 创建求解器并运行
        solver = ACO_TSP_Solver(
            cities_34,
            num_ants=exp['num_ants'],
            alpha=exp['alpha'],
            beta=exp['beta'],
            rho=exp['rho'],
            Q=exp['Q'],
            max_iter=exp['max_iter'],
            seed=random_seed_value  
        )
        
        best_path, best_distance, run_time = solver.solve(verbose=False)
        
        # 输出实验结果
        print(f"参数: 蚂蚁={exp['num_ants']}, α={exp['alpha']}, β={exp['beta']}, ρ={exp['rho']}, Q={exp['Q']}, 迭代={exp['max_iter']}")
        print(f"结果: 最优距离={best_distance:.2f}, 运行时间={run_time:.2f}秒")
        
        # 检查是否达到目标（<250）
        if best_distance < 250:
            print(f"✓ 达到目标: {best_distance:.2f} < 250")
        else:
            print(f"✗ 未达目标: {best_distance:.2f} ≥ 250")
        
        # 输出最优路径
        if best_path:
            print(f"\n最优路径（实验{exp['id']}）:")
            print(f"路径索引: {best_path}")
            print(f"路径长度: {len(best_path)} 个城市（包含返回起点）")
            print(f"城市顺序:")
            path_str = path_to_city_names(best_path)
            path_parts = path_str.split(" → ")
            for i in range(0, len(path_parts), 6):
                print("  " + " → ".join(path_parts[i:i+6]))
        
        # 存储结果
        results.append({
            "id": exp['id'],
            "num_ants": exp['num_ants'],
            "alpha": exp['alpha'],
            "beta": exp['beta'],
            "rho": exp['rho'],
            "Q": exp['Q'],
            "max_iter": exp['max_iter'],
            "distance": best_distance,
            "time": run_time,
            "best_path": best_path,
            "best_path_str": path_to_city_names(best_path) if best_path else ""
        })
    
    return results


def display_results_table(results):
    """
    以表格形式显示实验结果
    """
    print("\n" + "="*120)
    print("蚁群算法参数实验结果汇总")
    print("="*120)
    
    # 表头
    headers = ["实验", "蚂蚁数", "α", "β", "ρ", "Q", "迭代", "距离", "时间(s)", "是否达标"]
    col_widths = [6, 8, 8, 8, 8, 8, 8, 12, 10, 10]
    
    # 打印表头
    header_row = " ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(header_row)
    print("-"*len(header_row))
    
    # 打印每行数据
    for r in results:
        is_achieved = "✓" if r['distance'] < 250 else "✗"
        row_data = [
            str(r['id']),
            str(r['num_ants']),
            f"{r['alpha']:.1f}",
            f"{r['beta']:.1f}",
            f"{r['rho']:.2f}",
            str(r['Q']),
            str(r['max_iter']),
            f"{r['distance']:.2f}",
            f"{r['time']:.2f}",
            is_achieved
        ]
        row_str = " ".join(f"{d:<{w}}" for d, w in zip(row_data, col_widths))
        print(row_str)
    
    print("-"*len(header_row))


def analyze_parameter_effects(results):
    """
    分析参数对算法性能的影响
    """
    print("\n" + "="*80)
    print("参数影响分析")
    print("="*80)
    
    # 找出最佳解
    best_result = min(results, key=lambda x: x['distance'])
    print(f"全局最佳解: 实验{best_result['id']}, 距离={best_result['distance']:.2f}")
    
    # 输出最佳解的路径详情
    if best_result['best_path']:
        print(f"\n最佳路径详情（实验{best_result['id']}）:")
        print(f"路径索引: {best_result['best_path']}")
        print(f"城市顺序:")
        path_parts = best_result['best_path_str'].split(" → ")
        for i in range(0, len(path_parts), 6):
            print("  " + " → ".join(path_parts[i:i+6]))
    
    # 分析蚂蚁数量的影响
    print("\n1. 蚂蚁数量影响分析:")
    ants_results = {}
    for r in results:
        if r['alpha'] == 1.0 and r['beta'] == 2.0 and r['rho'] == 0.3 and r['Q'] == 100:
            ants_results[r['num_ants']] = (r['distance'], r['id'])
    
    for num_ants in sorted(ants_results.keys()):
        distance, exp_id = ants_results[num_ants]
        print(f"   蚂蚁数={num_ants} (实验{exp_id}): 距离={distance:.2f}")
    
    # 分析α的影响
    print("\n2. 信息素因子α影响分析:")
    alpha_results = {}
    for r in results:
        if r['num_ants'] == 20 and r['beta'] == 2.0 and r['rho'] == 0.3 and r['Q'] == 100:
            alpha_results[r['alpha']] = (r['distance'], r['id'])
    
    for alpha in sorted(alpha_results.keys()):
        distance, exp_id = alpha_results[alpha]
        effect = "高探索" if alpha < 1.0 else "高利用" if alpha > 2.0 else "平衡"
        print(f"   α={alpha:.1f} ({effect}, 实验{exp_id}): 距离={distance:.2f}")
    
    # 分析β的影响
    print("\n3. 启发函数因子β影响分析:")
    beta_results = {}
    for r in results:
        if r['num_ants'] == 20 and r['alpha'] == 1.0 and r['rho'] == 0.3 and r['Q'] == 100:
            beta_results[r['beta']] = (r['distance'], r['id'])
    
    for beta in sorted(beta_results.keys()):
        distance, exp_id = beta_results[beta]
        effect = "高探索" if beta < 1.0 else "贪心" if beta > 3.0 else "平衡"
        print(f"   β={beta:.1f} ({effect}, 实验{exp_id}): 距离={distance:.2f}")
    
    # 分析ρ的影响
    print("\n4. 信息素挥发系数ρ影响分析:")
    rho_results = {}
    for r in results:
        if r['num_ants'] == 20 and r['alpha'] == 1.0 and r['beta'] == 2.0 and r['Q'] == 100:
            rho_results[r['rho']] = (r['distance'], r['id'])
    
    for rho in sorted(rho_results.keys()):
        distance, exp_id = rho_results[rho]
        effect = "记忆强" if rho < 0.2 else "探索强" if rho > 0.4 else "平衡"
        print(f"   ρ={rho:.2f} ({effect}, 实验{exp_id}): 距离={distance:.2f}")
    
    # 分析Q的影响
    print("\n5. 信息素总量Q影响分析:")
    q_results = {}
    for r in results:
        if r['num_ants'] == 20 and r['alpha'] == 1.0 and r['beta'] == 2.0 and r['rho'] == 0.3:
            q_results[r['Q']] = (r['distance'], r['id'])
    
    for q in sorted(q_results.keys()):
        distance, exp_id = q_results[q]
        effect = "信息素弱" if q < 50 else "信息素强" if q > 200 else "适中"
        print(f"   Q={q} ({effect}, 实验{exp_id}): 距离={distance:.2f}")
    
    # 总体分析
    print("\n" + "="*80)
    print("总体分析:")
    
    achieved_count = sum(1 for r in results if r['distance'] < 250)
    print(f"• 达标实验数: {achieved_count}/{len(results)} (距离 < 250)")
    
    if achieved_count > 0:
        best_achieved = min(r['distance'] for r in results if r['distance'] < 250)
        best_achieved_exp = min(r['id'] for r in results if r['distance'] == best_achieved)
        print(f"• 最佳达标距离: {best_achieved:.2f} (实验{best_achieved_exp})")
    else:
        print(f"• 最佳距离: {best_result['distance']:.2f} (实验{best_result['id']}, 未达标)")
    
    print(f"• 平均运行时间: {np.mean([r['time'] for r in results]):.2f}秒")
    print(f"• 平均距离: {np.mean([r['distance'] for r in results]):.2f}")
    

def main():
    """
    主函数
    """
    
    # 运行参数实验
    results = run_parameter_experiments()
    
    # 显示结果表格
    display_results_table(results)
    
    # 分析参数影响
    analyze_parameter_effects(results)
    
    print("实验完成!")


if __name__ == "__main__":
    main()