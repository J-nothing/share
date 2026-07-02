%% 最小二乘线性拟合

%% 输入数据
% X坐标 (mm)
x = [-2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2, 1.6, 2.0];

% U0电压值 (mV)
y = [-1011, -830, -660, -385, -204, 0, 147, 405, 670, 942, 1120];

%% 最小二乘线性拟合
% 使用polyfit进行线性拟合（1次多项式）
p = polyfit(x, y, 1);

% 提取斜率和截距
k = p(1);  % 斜率
b = p(2);  % 截距

% 计算拟合值
y_fit = polyval(p, x);

% 计算相关系数
r = corrcoef(x, y);
r_squared = r(1,2)^2;  % 决定系数R²

%% 输出拟合结果
fprintf('========== 最小二乘线性拟合结果 ==========\n');
fprintf('拟合方程: U₀ = %.4f × X + %.4f\n', k, b);
fprintf('斜率 k = %.4f mV/mm\n', k);
fprintf('截距 b = %.4f mV\n', b);
fprintf('决定系数 R² = %.6f\n', r_squared);
fprintf('=========================================\n');

%% 计算坐标轴范围（自动适应数据）
% X轴范围：数据范围左右各留5%的边距
x_min = min(x);
x_max = max(x);
x_margin = (x_max - x_min) * 0.05;
xlim_low = x_min - x_margin;
xlim_high = x_max + x_margin;

% Y轴范围：考虑原始数据和拟合数据，左右各留10%的边距
y_min = min([y, y_fit]);
y_max = max([y, y_fit]);
y_margin = (y_max - y_min) * 0.1;
ylim_low = y_min - y_margin;
ylim_high = y_max + y_margin;

%% 绘制图像
figure('Position', [100, 100, 800, 600]);

% 绘制原始数据点
plot(x, y, 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'b', 'LineWidth', 1.5);
hold on;

% 绘制拟合直线（使用更密集的点使直线更平滑）
x_dense = linspace(x_min, x_max, 100);
y_dense_fit = polyval(p, x_dense);
plot(x_dense, y_dense_fit, 'r-', 'LineWidth', 2);

% 添加图例、标签和标题
legend('原始数据点', sprintf('拟合直线: U₀ = %.2fX + %.2f (R² = %.4f)', k, b, r_squared), ...
       'Location', 'best', 'FontSize', 11);
xlabel('X (mm)', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('U₀ (mV)', 'FontSize', 12, 'FontWeight', 'bold');
title('最小二乘线性拟合结果', 'FontSize', 14, 'FontWeight', 'bold');
grid on;

% 设置坐标轴范围（自动适应）
xlim([xlim_low, xlim_high]);
ylim([ylim_low, ylim_high]);


% 在图中添加拟合方程文本
% text(-1.8, 200, sprintf('拟合方程: U₀ = %.4fX + %.4f', k, b), ...
%      'FontSize', 10, 'BackgroundColor', 'w', 'EdgeColor', 'k');
% text(-1.8, 160, sprintf('R² = %.6f', r_squared), ...
%      'FontSize', 10, 'BackgroundColor', 'w', 'EdgeColor', 'k');

% 调整图形显示
set(gca, 'FontSize', 10);
box on;

%% 保存图像
% 保存为PNG格式（高清）
saveas(gcf, 'linear_fit_result_3.png');
% 保存为FIG格式（可编辑）
% savefig('linear_fit_result.fig');
% 保存为PDF格式（适合文档）
% print('linear_fit_result', '-dpdf', '-r300');

fprintf('\n图像已保存到当前文件夹:\n');
fprintf('  - linear_fit_result_3.png \n');
% fprintf('  - linear_fit_result.fig (MATLAB可编辑格式)\n');
% fprintf('  - linear_fit_result.pdf (PDF格式)\n');

%% 计算残差并逐一输出
% 计算拟合值
y_fit = polyval(p, x);

% 计算残差（实际值 - 拟合值）
residuals = y - y_fit;

% 计算相对误差（如果有零值需要处理）
% 避免除以零，对接近零的值特殊处理
relative_errors = zeros(size(y));
for i = 1:length(y)
    if abs(y_fit(i)) > 1e-6
        relative_errors(i) = (residuals(i) / y_fit(i)) * 100;
    else
        relative_errors(i) = NaN;  % 拟合值为0时，相对误差无定义
    end
end

% 输出残差表
fprintf('\n========== 残差分析结果 ==========\n');
fprintf('%-10s %-12s %-12s %-12s %-12s\n', '序号', 'X (mm)', '实际值(mV)', '拟合值(mV)', '残差(mV)');
fprintf('%-10s %-12s %-12s %-12s %-12s\n', '---', '------', '----------', '----------', '---------');
for i = 1:length(x)
    fprintf('%-10d %-12.2f %-12.2f %-12.2f %-12.2f\n', i, x(i), y(i), y_fit(i), residuals(i));
end

% 输出残差统计信息
fprintf('\n========== 残差统计信息 ==========\n');
fprintf('残差平方和 (SSE): %.4f\n', sum(residuals.^2));
fprintf('均方根误差 (RMSE): %.4f\n', sqrt(mean(residuals.^2)));
fprintf('残差最大值: %.4f (X = %.2f)\n', max(residuals), x(residuals == max(residuals)));