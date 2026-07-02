clear; clc; close all;

fprintf('============================================\n');
fprintf('🚀 激光切割轨迹分析程序开始运行\n');
fprintf('============================================\n');

% 定义阶跃函数
u = @(t, a) double(t >= a);

% 定义 u_x(t) 函数
u_x = @(t) 2 + u(t, 0) - 0.293*u(t, 3) - 1.414*u(t, 4.414) - 0.293*u(t, 5.828) ...
          + u(t, 6.828) + u(t, 7.828) - 0.143*u(t, 9.828) + 0.143*u(t, 15.659) ...
          - u(t, 17.659) - u(t, 20.659) + 0.106*u(t, 22.659) - 0.106*u(t, 27.132) ...
          + u(t, 32.123);

% 定义 u_y(t) 函数
u_y = @(t) 7 - 0.707*u(t, 3) + 0.707*u(t, 5.828) ...
          - u(t, 6.828) + u(t, 7.828) + 0.515*u(t, 9.828) - 0.515*u(t, 15.659) ...
          - u(t, 17.659) + u(t, 20.659) - 0.447*u(t, 22.659) - 0.447*u(t, 27.132) ...
          + u(t, 32.123);

fprintf('📊 开始计算轨迹数据...\n');

% 创建时间数组
t = linspace(0, 35, 3500);
fprintf('✅ 时间数组创建完成\n');

% 计算速度信号
ux_values = arrayfun(u_x, t);
uy_values = arrayfun(u_y, t);
fprintf('✅ 速度信号计算完成\n');

% 计算位置 (通过数值积分)
dt = t(2) - t(1);
x_pos = cumsum(ux_values) * dt;
y_pos = cumsum(uy_values) * dt;
fprintf('✅ 位置轨迹计算完成\n');

fprintf('🎨 开始绘制图形...\n');

% 创建图形窗口
figure('Position', [100, 100, 1400, 900]);

% (1) 绘制速度信号波形
subplot(2, 2, 1);
plot(t, ux_values, 'b-', 'LineWidth', 1.5);
title('速度控制信号 u_x(t)');
xlabel('时间 t (s)');
ylabel('u_x(t)');
grid on;
xlim([0, 35]);

subplot(2, 2, 2);
plot(t, uy_values, 'r-', 'LineWidth', 1.5);
title('速度控制信号 u_y(t)');
xlabel('时间 t (s)');
ylabel('u_y(t)');
grid on;
xlim([0, 35]);

% (2) 绘制 x-y 轨迹
subplot(2, 2, [3, 4]);
plot(x_pos, y_pos, 'g-', 'LineWidth', 2);
hold on;

% 添加钢板边界
plot([0, 150], [0, 0], 'k--', 'LineWidth', 1, 'Color', [0.5, 0.5, 0.5]);
plot([0, 150], [90, 90], 'k--', 'LineWidth', 1, 'Color', [0.5, 0.5, 0.5]);
plot([0, 0], [0, 90], 'k--', 'LineWidth', 1, 'Color', [0.5, 0.5, 0.5]);
plot([150, 150], [0, 90], 'k--', 'LineWidth', 1, 'Color', [0.5, 0.5, 0.5]);

% 标记起点和终点
plot(x_pos(1), y_pos(1), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'b');
plot(x_pos(end), y_pos(end), 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');

xlabel('x 位置 (mm)');
ylabel('y 位置 (mm)');
title('激光切割轨迹 (x-y 关系曲线)');
grid on;
axis equal;
legend('切割轨迹', '钢板边界', 'Location', 'best');

% 保存图片
filename = '激光切割轨迹结果.png';
saveas(gcf, filename);
fprintf('✅ 图片已保存: %s\n', filename);

% 显示轨迹信息
fprintf('\n📊 轨迹信息:\n');
fprintf('起点位置: (%.2f, %.2f) mm\n', x_pos(1), y_pos(1));
fprintf('终点位置: (%.2f, %.2f) mm\n', x_pos(end), y_pos(end));
fprintf('x 范围: [%.2f, %.2f] mm\n', min(x_pos), max(x_pos));
fprintf('y 范围: [%.2f, %.2f] mm\n', min(y_pos), max(y_pos));

fprintf('\n🎉 程序执行完成!\n');