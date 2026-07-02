import numpy as np
import math
import time
from itertools import permutations

# 前10个城市
cities_10 = [
    (116.46, 39.92),   # 北京 1
    (117.2, 39.13),    # 天津 2
    (121.48, 31.22),   # 上海 3
    (106.54, 29.59),   # 重庆 4
    (91.11, 29.97),    # 拉萨 5
    (87.68, 43.77),    # 乌鲁木齐 6
    (106.27, 38.47),   # 银川 7
    (111.65, 40.82),   # 呼和浩特 8
    (108.33, 22.84),   # 南宁 9
    (126.63, 45.75),   # 哈尔滨 10
]

city_names_10 = [
    "北京(1)", "天津(2)", "上海(3)", "重庆(4)", "拉萨(5)",
    "乌鲁木齐(6)", "银川(7)", "呼和浩特(8)", "南宁(9)", "哈尔滨(10)"
]

def calculate_distance_matrix(cities):
    """计算城市间的欧氏距离矩阵"""
    n = len(cities)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                x1, y1 = cities[i]
                x2, y2 = cities[j]
                dist_matrix[i][j] = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return dist_matrix

def exhaustive_tsp_10_cities():
    """穷举法解决前10个城市的TSP问题"""
    print("城市列表：")
    for i, (name, coord) in enumerate(zip(city_names_10, cities_10)):
        print(f"  城市{name}：坐标({coord[0]:.2f}, {coord[1]:.2f})")
    
    # 计算距离矩阵
    dist_matrix = calculate_distance_matrix(cities_10)
    
    start_time = time.time()
    
    # 城市编号
    n = 10
    cities_idx = list(range(1, n))  # 除去起始城市序号0
    total_permutations = math.factorial(n-1) # 计算路径总数：(n-1)!
    
    print(f"需要检查的路径总数: {total_permutations:,}")
    
    best_path = None
    best_distance = float('inf')
    count = 0
    
    # 遍历所有可能的排列
    for perm in permutations(cities_idx):
        count += 1
        
        # 构造完整路径：从城市1出发，最后回到城市1
        path = [0] + list(perm) + [0]
        
        # 计算路径总距离
        distance = 0
        for i in range(len(path)-1):
            distance += dist_matrix[path[i]][path[i+1]]
        
        # 更新最优解
        if distance < best_distance:
            best_distance = distance
            best_path = path
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n" + "=" * 60)
    print("计算结果")
    print("=" * 60)

    # 输出最优路径信息
    print_detailed_path_info(best_path, dist_matrix)
    
    # 输出最小开销
    print(f"最小开销: {best_distance:.2f}")
    
    
    # 显示城市名称
    city_names_path = [city_names_10[i] for i in best_path]
    print(f"路线: {' → '.join(city_names_path)}")
    
    
    return best_path, best_distance, dist_matrix

def print_detailed_path_info(path, dist_matrix):
    """打印路径的详细信息"""
    print(f"\n" + "-" * 60)
    print("最优路径详细信息")
    print("-" * 60)
    
    total_distance = 0
    print(f"{'路段':<25} {'距离':<10} {'累积距离':<10}")
    print("-" * 50)
    
    for i in range(len(path)-1):
        from_city = path[i]
        to_city = path[i+1]
        distance = dist_matrix[from_city, to_city]
        total_distance += distance
        
        from_name = city_names_10[from_city]
        to_name = city_names_10[to_city]
        
        print(f"{from_name} → {to_name:<15} {distance:9.2f} {total_distance:9.2f}")
    
    print("-" * 50)
    print(f"{'总距离':<25} {'':<10} {total_distance:9.2f}")

def main():
    
    best_path, best_distance, dist_matrix = exhaustive_tsp_10_cities()
    
    
    

if __name__ == "__main__":
    main()