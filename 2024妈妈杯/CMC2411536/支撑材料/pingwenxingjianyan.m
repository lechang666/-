data1 = readtable('C:\Users\86139\Desktop\附件1.csv');
tap=data1.SC == "'SC1'";
datas = data(tap, :);  % 选择分拣中心 12 的数据

% 提取日期和货量
date = data1.Dtae;
volumes = data1.Value;

[h, pValue, stat, cValue, reg] = adftest(volumes, 'lags', 0);
fprintf('ADF统计量值: %f\n', stat);
fprintf('p值: %f\n', pValue);
fprintf('临界值: %f\n', cValue);
if h == 0
    fprintf('数据是平稳的\n');
    % 生成一些模拟数据
N = 122; % 数据点数目

t = (1:N)';
monishujv=data;
% 拟合 ARMA 模型
p = 2; % AR 阶数
q = 1; % MA 阶数
arma_model = armax(monishujv, [p q]);

% 预测未来的值
future_steps = 30; % 要预测的未来步数
[monishujv_pred, monishujv_pred_cov] = forecast(arma_model, monishujv, future_steps);

% 绘制原始数据和预测值
figure;
plot(t, monishujv, 'b', 'LineWidth', 1.5);
hold on;
plot(t(end)+1:t(end)+future_steps, monishujv_pred, 'r--', 'LineWidth', 1.5);
xlabel('时间');
ylabel('观测值');
legend('原始数据', '预测值', 'Location', 'NorthWest');
title('ARMA 模型预测');

% 绘制预测区间
lower_bound = monishujv_pred - 1.96*sqrt(monishujv_pred_cov);
upper_bound = monishujv_pred + 1.96*sqrt(monishujv_pred_cov);
patch([t(end)+1:t(end)+future_steps fliplr(t(end)+1:t(end)+future_steps)], [lower_bound' fliplr(upper_bound')], 'r', 'FaceAlpha', 0.3, 'EdgeColor', 'none');
else
    

% 提取日期和货量
dates = data.Date;
volumes = data.Value;

% 绘制时间序列图
plot(dates, volumes);
xlabel('日期');
ylabel('货量');
title('分拣中心 1 货量时间序列图');
% 一阶差分消除趋势
diff_volumes = diff(volumes);

% 季节性差分 (假设以周为周期)
seasonal_diff_volumes = diff(diff_volumes, 30);

% 对齐日期和差分后的货量向量
aligned_dates = dates(32:end);
aligned_volumes = seasonal_diff_volumes;

% 绘制差分后的时间序列图
figure;
plot(aligned_dates, aligned_volumes);
xlabel('日期');
ylabel('差分后货量');
title('分拣中心 1 差分后货量时间序列图');

% 自相关和偏自相关分析
autocorr(aligned_volumes);
parcorr(aligned_volumes);

% 根据自相关和偏自相关图，选择合适的 p, d, q 值
p = 1;  % 自回归阶数
d = 1;  % 差分阶数
q = 0;  % 移动平均阶数
% 建立 ARIMA 模型
model = arima(p, d, q);

% 估计模型参数
est_model = estimate(model, seasonal_diff_volumes);

% 模型检验
[residuals, ~, ~] = infer(est_model, seasonal_diff_volumes);

% 残差分析
figure;
plot(residuals);
xlabel('时间');
ylabel('残差');
title('分拣中心 1 ARIMA 模型残差图');

% 白噪声检验
[h, pValue] = lbqtest(residuals);
% 预测未来 30 天的货量
forecast_volumes = forecast(est_model, 30, seasonal_diff_volumes);

% 还原差分
forecast_volumes = cumsum(forecast_volumes);
forecast_volumes = cumsum(forecast_volumes) + volumes(end);

% 绘制预测结果
figure;
plot(volumes);
hold on;
plot(length(volumes) + (1:30), forecast_volumes);
xlabel('日期');
ylabel('货量');
title('分拣中心 1 货量预测');
legend('实际货量', '预测货量');
end
