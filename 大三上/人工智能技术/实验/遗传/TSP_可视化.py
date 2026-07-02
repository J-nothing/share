import matplotlib.pyplot as plt
import numpy as np
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

best_path = [0, 12, 13, 7, 6, 27, 14, 5, 4, 31, 26, 24, 32, 33, 25, 2, 19, 17, 18, 20, 21, 23, 22, 8, 30, 3, 29, 28, 16, 15, 11, 9, 10, 1]  # 示例：顺序遍历


total_distance = 170.75  

# 构建路径坐标
lons = [cities_34[i][0] for i in best_path]
lats = [cities_34[i][1] for i in best_path]

# 添加闭环（回到起点）
lons.append(lons[0])
lats.append(lats[0])

# 设置图形
plt.figure(figsize=(14, 10))
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 绘制路径线
plt.plot(lons, lats, color='black', linewidth=1.5, zorder=1)

# 绘制城市点
plt.scatter(lons[:-1], lats[:-1], color='red', s=60, edgecolors='black', zorder=2)

# 标注城市名（偏移避免重叠）
for i, (lon, lat) in enumerate(zip(lons[:-1], lats[:-1])):
    city_name = city_names[best_path[i]]
    plt.annotate(city_name, (lon, lat), xytext=(5, 5), textcoords='offset points',
                 fontsize=10, ha='left', va='bottom')

# 图形设置
plt.title('34城市TSP - 遗传算法最优路径）', fontsize=16, pad=20)
plt.xlabel('经度')
plt.ylabel('纬度')
plt.grid(True, linestyle='--', alpha=0.3)
plt.axis('equal')  # 保持比例
plt.tight_layout()

# 显示总距离
plt.text(0.02, 0.02, f'Distance={total_distance:.4f}', transform=plt.gca().transAxes,
         fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
         verticalalignment='bottom', horizontalalignment='left')

# 保存图片

output_path = r"E:\NKUer\2025~2026第一学期\人工智能技术\实验\遗传\tsp_result.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print("图像已保存为: tsp_experiment6_route.png")

plt.show()