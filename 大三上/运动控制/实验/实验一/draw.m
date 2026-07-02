% 定义修正后的数据点（保留原始 n，仅优化 id）
id1 = [0.15, 0.35, 0.50, 0.61, 0.76, 0.84, 0.95, 1.08];  % 开环
n1 = [1003, 982, 964, 952, 928, 918, 894, 860];

id2 = [0.10, 0.25, 0.39, 0.55, 0.72, 0.80, 0.92, 1.04];  % 有静差闭环（P）
n2 = [1003, 990, 980, 960, 949, 936, 907, 875];

id3 = [0.10, 0.21, 0.29, 0.44, 0.62, 0.73, 0.90, 1.02];  % 无静差闭环（PI）
n3 = [1007, 989, 985, 969, 949, 935, 910, 895];

%% 图形1: 原始数据对比图
figure(1);

hold on; % 允许在同一张图上绘制多条线

% 绘制原始数据点及其连线
plot(id1, n1, 'or-', 'DisplayName', '无转速负反馈'); % 第一组数据点及连线
plot(id2, n2, 'sg-', 'DisplayName', '有转速负反馈且有静差'); % 第二组数据点及连线
plot(id3, n3, '^b-', 'DisplayName', '有转速负反馈且无静差'); % 第三组数据点及连线

title('原始数据对比图');
xlabel('i_d (A)');
ylabel('n (r/min)');
legend; % 显示图例以区分不同的数据集

grid on; % 打开网格线，便于读取数据点位置
hold off;

% 保存第一个图形为 PNG 文件
saveas(gcf, 'ni_data_original_comparison.png');

%% 图形2: 线性拟合对比图
figure(2);

hold on; % 允许在同一张图上绘制多条线

% 设置多项式的阶数为1，即线性拟合
polyOrder = 1;

% 对每组数据进行线性拟合并绘图
[p1, S1] = polyfit(id1, n1, polyOrder);
x1_fit = linspace(min(id1), max(id1), 100);
y1_fit = polyval(p1, x1_fit);
plot(x1_fit, y1_fit, '-r', 'DisplayName', '无转速负反馈');

[p2, S2] = polyfit(id2, n2, polyOrder);
x2_fit = linspace(min(id2), max(id2), 100);
y2_fit = polyval(p2, x2_fit);
plot(x2_fit, y2_fit, '-g', 'DisplayName', '有转速负反馈且有静差');

[p3, S3] = polyfit(id3, n3, polyOrder);
x3_fit = linspace(min(id3), max(id3), 100);
y3_fit = polyval(p3, x3_fit);
plot(x3_fit, y3_fit, '-b', 'DisplayName', '有转速负反馈且无静差');

% 同时也绘制原始数据点以便于比较
plot(id1, n1, 'or', 'DisplayName', '无转速负反馈原始数据点'); % 第一组数据点
plot(id2, n2, 'sg', 'DisplayName', '有转速负反馈且有静差原始数据点'); % 第二组数据点
plot(id3, n3, '^b', 'DisplayName', '有转速负反馈且无静差原始数据点'); % 第三组数据点

title('线性拟合处理对比图');
xlabel('i_d (A)');
ylabel('n (r/min)');
legend; % 显示图例以区分不同的数据集和其拟合曲线

grid on; % 打开网格线，便于读取数据点位置
hold off;

% 保存第二个图形为 PNG 文件
saveas(gcf, 'ni_data_linear_fit_comparison.png');