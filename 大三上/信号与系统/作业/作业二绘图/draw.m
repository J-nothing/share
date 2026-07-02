%% 脉动喷水式推进器激励信号分析 —— 完整版（含第三问：带宽内功率占比）

clear; clc; close all;

%% 参数设置
T = 1.0;                    % 周期 (秒)
Fs = 5000;                  % 采样率
t_end = 2.4;                % 模拟时间
t = 0 : 1/Fs : t_end;
N = length(t);

% 构造周期非对称三角脉冲：尖峰在 0.2, 1.2...；结束于 0.3, 1.3...
x = zeros(size(t));
for i = 1:N
    ti = t(i);
    k = floor(ti);
    tau = ti - k;
    if tau >= 0 && tau < 0.2
        x(i) = 25 * tau;                     % 上升段
    elseif tau >= 0.2 && tau < 0.3
        x(i) = 50 * (0.3 - tau);             % 下降段
    else
        x(i) = 0;
    end
end

%% FFT 分析
X = fft(x);
X_shift = fftshift(X);
f = (-N/2:N/2-1) * Fs / N;
omega = 2 * pi * f;
idx_plot = (omega >= -4) & (omega <= 4);

%% (1) 绘图：时域 + 频谱
figure('Position', [100, 100, 900, 600]);
subplot(2,1,1);
plot(t, x, 'b', 'LineWidth', 1.5);
title('激励信号 x(t)', 'FontSize', 12);
xlabel('时间 t (s)'); ylabel('x(t)');
grid on; xlim([0, 2.4]); ylim([-0.5, 5.5]);

subplot(2,1,2);
plot(omega(idx_plot), abs(X_shift(idx_plot)), 'b', 'LineWidth', 1.5);
title('频谱 |X(\omega)| （-4 \leq \omega \leq 4）', 'FontSize', 12);
xlabel('角频率 \omega (rad/s)'); ylabel('|X(\omega)|');
grid on;

fname1 = 'signal_and_spectrum.png';
print(gcf, '-dpng', '-r300', fname1);

%% (2) 计算 95% 功率带宽
power_spectrum = (abs(X_shift).^2) / (N^2);   % 每个频点的平均功率
total_power = sum(power_spectrum);            % 总平均功率

[~, sort_idx] = sort(abs(omega));
cum_power = cumsum(power_spectrum(sort_idx));

threshold = 0.95;
idx_95 = find(cum_power >= threshold * total_power, 1, 'first');

if ~isempty(idx_95)
    omega_95 = abs(omega(sort_idx(idx_95)));
    bandwidth_rad = 2 * omega_95;  % 双边带宽
else
    bandwidth_rad = Inf;
end

fprintf('总平均功率: %.6f\n', total_power);

%% ✅ (3) 第三问：计算该带宽内的实际功率占比（核心补充！）
idx_band = (omega >= -omega_95) & (omega <= omega_95);
power_in_band = sum(power_spectrum(idx_band));
energy_ratio = power_in_band / total_power;   % 即“带宽内能量占比”

fprintf('95%% 功率对应的带宽: %.4f rad/s\n', bandwidth_rad);
fprintf('该带宽内实际功率占比: %.4f%%\n', energy_ratio * 100);  % ← 第三问答案！

%% (4) 重构信号 + 幅频/相频
X_filtered = zeros(size(X_shift));
X_filtered(idx_band) = X_shift(idx_band);
x_recon = real(ifft(ifftshift(X_filtered)));

figure('Position', [150, 150, 900, 600]);
subplot(2,1,1);
plot(t, x, 'b', 'LineWidth', 1.5);
hold on;
plot(t, x_recon, 'r--', 'LineWidth', 1.2);
title('原始信号 vs 带宽内重构信号', 'FontSize', 12);
xlabel('时间 t (s)'); ylabel('x(t)');
legend('原始信号', '重构信号');
grid on; xlim([0, 2.4]); ylim([-0.5, 5.5]);

subplot(2,1,2);
yyaxis left;
plot(omega(idx_plot), abs(X_shift(idx_plot)), 'b', 'LineWidth', 1.5);
ylabel('幅度 |X(\omega)|', 'Color', 'b');
yyaxis right;
plot(omega(idx_plot), angle(X_shift(idx_plot)), 'r--', 'LineWidth', 1.2);
ylabel('相位 (rad)', 'Color', 'r');
xlabel('角频率 \omega (rad/s)');
title('幅频与相频特性', 'FontSize', 12);
grid on;

fname2 = 'reconstructed_and_freq_response.png';
print(gcf, '-dpng', '-r300', fname2);

%% (5) 手动验证脉冲（无工具箱）
num_pulses = floor(t_end) + 1;
fprintf('\n✅ 脉冲验证:\n');
for k = 0:num_pulses-1
    idx_range = (t >= k) & (t < k+1);
    if any(idx_range)
        [~, local_max_idx] = max(x(idx_range));
        global_idx = find(idx_range, 1) + local_max_idx - 1;
        t_peak = t(global_idx);
        after_peak = (t >= t_peak) & (t < k+1);
        zero_idx = find(x(after_peak) < 0.1, 1);
        t_end_pulse = NaN;
        if ~isempty(zero_idx)
            t_end_pulse = t(find(after_peak,1) + zero_idx - 1);
        end
        fprintf('  脉冲 %d: 尖峰 t=%.3f, 结束≈%.3f\n', k+1, t_peak, t_end_pulse);
    end
end

fprintf('\n✅ 图像已保存至当前文件夹：\n');
fprintf('   %s\n', fname1);
fprintf('   %s\n', fname2);