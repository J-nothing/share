import matplotlib.pyplot as plt
import numpy as np

# 城市数据
cities_34 = [
    (116.4, 39.9),   # 北京
    (117.2, 39.1),   # 天津
    (121.5, 31.2),   # 上海
    (106.5, 29.5),   # 重庆
    (91.1, 29.7),    # 拉萨
    (87.6, 43.8),    # 乌鲁木齐
    (106.2, 38.5),   # 银川
    (111.7, 40.8),   # 呼和浩特
    (108.3, 22.8),   # 南宁
    (126.6, 45.8),   # 哈尔滨
    (125.3, 43.9),   # 长春
    (123.4, 41.8),   # 沈阳
    (114.5, 38.0),   # 石家庄
    (112.5, 37.9),   # 太原
    (101.8, 36.6),   # 西宁
    (117.0, 36.7),   # 济南
    (113.7, 34.7),   # 郑州
    (118.8, 32.0),   # 南京
    (117.3, 31.9),   # 合肥
    (120.2, 30.3),   # 杭州
    (119.3, 26.1),   # 福州
    (115.9, 28.7),   # 南昌
    (112.9, 28.2),   # 长沙
    (114.3, 30.6),   # 武汉
    (113.3, 23.1),   # 广州
    (121.5, 25.0),   # 台北
    (110.3, 20.0),   # 海口
    (103.8, 36.1),   # 兰州
    (108.9, 34.3),   # 西安
    (104.1, 30.7),   # 成都
    (106.7, 26.6),   # 贵阳
    (102.7, 25.0),   # 昆明
    (114.2, 22.3),   # 香港
    (113.5, 22.2)    # 澳门
]

city_names = [
    "北京", "天津", "上海", "重庆", "拉萨", "乌鲁木齐", "银川", "呼和浩特",
    "南宁", "哈尔滨", "长春", "沈阳", "石家庄", "太原", "西宁", "济南",
    "郑州", "南京", "合肥", "杭州", "福州", "南昌", "长沙", "武汉", "广州",
    "台北", "海口", "兰州", "西安", "成都", "贵阳", "昆明", "香港", "澳门"
]

# 蚁群算法最优路径
aco_best_path = [1, 15, 18, 17, 19, 2, 25, 20, 21, 23, 22, 24, 32, 33, 26, 8, 30, 3, 29, 31, 4, 5, 14, 27, 6, 28, 16, 12, 13, 7, 0, 11, 10, 9, 1]
aco_total_distance = 155.49

# 遗传算法最优路径
ga_best_path = [0, 12, 13, 7, 6, 27, 14, 5, 4, 31, 26, 24, 32, 33, 25, 2, 19, 17, 18, 20, 21, 23, 22, 8, 30, 3, 29, 28, 16, 15, 11, 9, 10, 1]
ga_total_distance = 170.75

# 构建路径坐标
def get_path_coordinates(path):
    lons = [cities_34[i][0] for i in path]
    lats = [cities_34[i][1] for i in path]
    # 添加闭环（回到起点）
    lons.append(lons[0])
    lats.append(lats[0])
    return lons, lats

aco_lons, aco_lats = get_path_coordinates(aco_best_path)
ga_lons, ga_lats = get_path_coordinates(ga_best_path)

# 设置图形
plt.figure(figsize=(14, 10))
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 绘制蚁群算法路径线（蓝色）
plt.plot(aco_lons, aco_lats, color='blue', linewidth=2, zorder=1, label=f'蚁群算法 (距离: {aco_total_distance:.2f})', alpha=0.7)

# 绘制遗传算法路径线（红色）
plt.plot(ga_lons, ga_lats, color='red', linewidth=2, zorder=2, label=f'遗传算法 (距离: {ga_total_distance:.2f})', alpha=0.7, linestyle='--')

# 绘制城市点
all_lons = [city[0] for city in cities_34]
all_lats = [city[1] for city in cities_34]
plt.scatter(all_lons, all_lats, color='green', s=60, edgecolors='black', zorder=3, label='城市点')

# 标注城市名（偏移避免重叠）
for i, (lon, lat) in enumerate(zip(all_lons, all_lats)):
    city_name = city_names[i]
    plt.annotate(city_name, (lon, lat), xytext=(5, 5), textcoords='offset points',
                 fontsize=9, ha='left', va='bottom', alpha=0.8)

# 图形设置
plt.title('34城市TSP - 蚁群算法 vs 遗传算法最优路径对比', fontsize=16, pad=20)
plt.xlabel('经度')
plt.ylabel('纬度')
plt.grid(True, linestyle='--', alpha=0.3)
plt.axis('equal')  # 保持比例

# 添加图例
plt.legend(loc='upper right', fontsize=12)

# 显示信息框
info_text = f'蚁群算法距离: {aco_total_distance:.2f}\n遗传算法距离: {ga_total_distance:.2f}\n距离差值: {ga_total_distance-aco_total_distance:.2f}'
plt.text(0.02, 0.02, info_text, transform=plt.gca().transAxes,
         fontsize=11, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9),
         verticalalignment='bottom', horizontalalignment='left')

plt.tight_layout()

# 保存图片
output_path = r"E:\NKUer\2025~2026第一学期\人工智能技术\实验\蚁群\tsp_comparison_result.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"对比图像已保存为: {output_path}")

plt.show()