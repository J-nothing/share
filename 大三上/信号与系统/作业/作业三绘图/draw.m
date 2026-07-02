% 清空环境
clear; clc;

% k 从 0 到 11（共12个点）
k_list = 0:11;
N = length(k_list);  % N = 12

% 初始化 a_k
a_k = zeros(1, N);
sqrt2 = sqrt(2);

% k = 0（对应索引 1）
a_k(1) = (11 - sqrt2) / 12;
fprintf('a_%d = %.6f\n', k_list(1), a_k(1));

% k = 1 到 11（对应索引 2 到 12）
for idx = 2:N
    k = k_list(idx);  % k = 1, 2, ..., 11
    
    numerator = (1i / 12) * sqrt2 * exp(1i * (3 - k) * pi / 6);
    denom = 1 - sqrt2 * exp(-1i * k * pi / 6) + exp(-1i * k * pi / 3);
    
    if abs(denom) < 1e-12
        warning('分母接近零，设 a_k = 0，k = %d', k);
        a_k(idx) = 0;
    else
        a_k(idx) = numerator / denom;
    end
    
    fprintf('a_%d = %.6f + %.6fi\n', k, real(a_k(idx)), imag(a_k(idx)));
end

% 计算幅度和相位
magnitude = abs(a_k);
phase_deg = rad2deg(angle(a_k));

% 显示前几个值
disp('前几个幅度:');
disp(magnitude(1:4)');
disp('前几个相位（度）:');
disp(phase_deg(1:4)');

% 绘图
figure('Position', [100, 100, 1000, 400]);

subplot(1,2,1);
stem(k_list, magnitude, 'filled', 'MarkerSize', 6);
title('|a_k| (Magnitude)');
xlabel('k');
ylabel('|a_k|');
grid on;

subplot(1,2,2);
stem(k_list, phase_deg, 'filled', 'MarkerSize', 6);
title('\angle a_k (Phase in degrees)');
xlabel('k');
ylabel('Phase (degrees)');
grid on;

% 保存图像到当前脚本目录
script_dir = fileparts(mfilename('fullpath'));
output_path = fullfile(script_dir, 'ak_magnitude_phase.png');
saveas(gcf, output_path);
disp(['✅ 图像已保存到: ', output_path]);

% 创建成功标记
fid = fopen(fullfile(script_dir, 'SUCCESS.txt'), 'w');
fprintf(fid, 'MATLAB绘图成功！\n图像路径: %s\n', output_path);
fclose(fid);