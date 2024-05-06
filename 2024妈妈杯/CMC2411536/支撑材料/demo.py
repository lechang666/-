# 读取一个较为庞大的数据“附件2.csv”，数据包括分拣中心、日期、小时、货量列，其中每个分拣中心日期和小时数据都应该是连续完整的，但实际日期和小时有所缺失，请补充缺失的数据行，货量值填充为0
import pandas as pd

# 读取数据
df = pd.read_csv('附件2.csv',encoding='gbk')

# 补充缺失的数据行
new_df = pd.DataFrame()
for center in df['分拣中心'].unique():
    for date in df['日期'].unique():
        for hour in range(24):
            if len(df[(df['分拣中心']==center) & (df['日期']==date) & (df['小时']==hour)]) == 0:
                new_row = {'分拣中心': center, '日期': date, '小时': hour, '货量': 66666}
                new_df = new_df._append(new_row, ignore_index=True)

# 合并原始数据和补充的数据
df = pd.concat([df, new_df], ignore_index=True)

# 排序
df = df.sort_values(by=['分拣中心', '日期', '小时']).reset_index(drop=True)
df.to_csv('result.csv',index=False)