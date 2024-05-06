import random
import numpy as np
import pandas as pd

# 读取文件
df = pd.read_csv(r"C:\Users\Yao\Downloads\结果表4.csv",encoding='gbk')

# 获取分拣中心列表
centers = df["分拣中心"].unique().tolist()
predicted_workload = df["货量"].unique().tolist()

# 定义班次列表
shifts = [(0, 8),(5, 13),(8, 16),(12, 20),(14, 22),(16, 24)]

# 定义目标函数
def objective_function(solution):
    # 计算总人天数
    total_man_days = 0
    for day in range(30):
        for center in range(len(centers)):
            for shift in range(len(shifts)):
                total_man_days += solution[day][center][shift]

    # 计算实际小时人效
    actual_efficiency = []
    for day in range(30):
        for center in range(len(centers)):
            for shift in range(len(shifts)):
                if solution[day][center][shift].any() > 0:
                    if day * len(centers) + center < len(predicted_workload):
                        actual_efficiency.append(
                            predicted_workload[day * len(centers) + center] / (
                                solution[day][center][shift] * (shifts[shift][1] - shifts[shift][0]))
                        )

    # 计算标准差
    std_efficiency = np.std(actual_efficiency)

    # 目标函数 = 总人天数 + 标准差
    return total_man_days + std_efficiency

# 定义模拟退火算法
def simulated_annealing(objective_function, initial_solution, temperature, cooling_rate):
    current_solution = initial_solution
    best_solution = current_solution
    best_objective = objective_function(current_solution)

    while temperature > 0.01:
        # 随机生成一个新的解
        new_solution = generate_neighbor(current_solution)

        # 计算新解的目标函数值
        new_objective = objective_function(new_solution)

        # 如果新解的目标函数值更优，则接受新解
        if new_objective.any() < best_objective.any():
            best_solution = new_solution
            best_objective = new_objective

        # 否则，以一定的概率接受新解
        else:
            p = np.exp(-(new_objective - best_objective) / temperature)
            if random.random() < p.any():
                current_solution = new_solution

        # 降低温度
        temperature *= cooling_rate

    return best_solution

# 定义生成邻近解的函数
def generate_neighbor(solution):
    # 随机选择一个分拣中心和一个班次
    day = random.randint(0, 29)
    center = random.randint(0, len(centers) - 1)
    shift = random.randint(0, len(shifts) - 1)
    worker_type = random.randint(0, 1)  # 0 表示正式工，1 表示临时工

    # 随机增加或减少出勤人数
    new_solution = solution.copy()
    if worker_type == 0:
        max_workers = 60  # 正式工人数上限
    else:
        max_workers = 200  # 临时工人数上限
    new_solution[day][center][shift] += random.randint(-10, 10)

    # 确保出勤人数在 0 到最大人数之间
    new_solution[day][center][shift] = max(0, min(max_workers, new_solution[day][center][shift].any()))

    # 确保每个班次中正式工的人数不超过 20
    for shift in range(len(shifts)):
        total_formal_workers = new_solution[day][center][shift][0]
        if total_formal_workers > 60:
            new_solution[day][center][shift][0] = 60
            new_solution[day][center][shift][1] = max(0, max_workers - 60)

    # 确保每个分拣中心每天的正式工人数不超过 20
    for center in range(len(centers)):
        total_formal_workers = 0
        for day in range(30):
            for shift in range(len(shifts)):
                total_formal_workers += new_solution[day][center][shift][0]
        if total_formal_workers > 60:
            for day in range(30):
                for shift in range(len(shifts)):
                    if new_solution[day][center][shift][0] > 0:
                        new_solution[day][center][shift][0] -= 1
                        total_formal_workers -= 1
                        break

    # 计算前几个时段的正式工总和
    early_periods = 10  # 前几个时段
    total_formal_workers = 0
    for day in range(early_periods):
        for center in range(len(centers)):
            for shift in range(len(shifts)):
                total_formal_workers += new_solution[day][center][shift][0]

    # 如果前几个时段的正式工总和达到 60，则后续不再使用正式工
    if total_formal_workers == 60:
        for day in range(early_periods, 30):
            for center in range(len(centers)):
                for shift in range(len(shifts)):
                    new_solution[day][center][shift][0] = 0

    # 确保每个时间段的正式工人数不超过 20
    for day in range(30):
        for center in range(len(centers)):
            for shift in range(len(shifts)):
                total_formal_workers = new_solution[day][center][shift][0]
                if total_formal_workers > 20:
                    new_solution[day][center][shift][0] = 20
                    new_solution[day][center][shift][1] = max(0, max_workers - 20)

    return new_solution

# 定义初始解
initial_solution = np.random.randint(0, 61, size=(30, len(centers), len(shifts), 2))

# 定义温度和冷却速率
temperature = 100
cooling_rate = 0.95

# 运行模拟退火算法
best_solution = simulated_annealing(
    objective_function, initial_solution, temperature, cooling_rate
)

# 获取 SC60 分拣中心的出勤计划
sc60_schedule = best_solution[:, centers.index("SC60"), :]

# 计算每名正式工的出勤率
formal_worker_attendance_rate = np.sum(sc60_schedule[:, :, 0], axis=1) / 30

# 筛选出出勤率符合要求的正式工
formal_workers = np.where(formal_worker_attendance_rate <= 0.85)[0]

# 构建结果表 6
result_table = pd.DataFrame(columns=["日期", "班次", "正式工人数", "临时工人数"])

# 循环遍历每一天和每个班次
for day in range(30):
    for shift in range(len(shifts)):
        # 计算正式工人数
        formal_workers_on_duty = np.sum(sc60_schedule[day, shift, 0])

        # 计算临时工人数
        temporary_workers_on_duty = np.sum(sc60_schedule[day, shift, 1])

        # 将数据添加到结果表 6 中
        result_table = result_table.append({
            "日期": day + 1,
            "班次": f"{shifts[shift][0]}:00-{shifts[shift][1]}:00",
            "正式工人数": formal_workers_on_duty,
            "临时工人数": temporary_workers_on_duty
        }, ignore_index=True)

# 打印结果表 6
print(result_table)
result_table.to_csv("output.csv")