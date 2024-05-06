# 读取xlsx文件，赋值给pandas矩阵
import pandas as pd
from datetime import datetime, timedelta

def change(date):
    # 将 "11" 替换为 "12"
    new_date_str = date.replace("-11-", "-12-")
    new_date_str = new_date_str.replace("-0","-")
    return new_date_str

data = pd.read_excel('附录二插值结果.xlsx')

pre_data=pd.read_csv('./data/结果表1.csv')

# 创建一个新矩阵,表头为分拣中心/日期/小时/货量
res = {'分拣中心': [],
         '日期': [],
         '小时': [],
         '货量': []}
# 按照data'SC'列进行分组
grouped = data.groupby('SC')
for name, group in grouped:
    groupsum=group['立方样条插值'].sum()
    for index,item in group.iterrows():
        temp=pre_data[(pre_data['分拣中心']==name) & (pre_data['日期']==change(item['日期'].strftime("%Y-%m-%d")))]
        res['分拣中心'].append(name)
        res['日期'].append(change(item['日期'].strftime("%Y-%m-%d")))
        res['小时'].append(item['小时'])
        ht=item['立方样条插值']
        if ht<0:
            ht=0
        res['货量'].append((ht/groupsum)*(temp['货量'].sum()))

print(res)
df = pd.DataFrame(res)
df.to_csv('output1_2.csv', index=False)