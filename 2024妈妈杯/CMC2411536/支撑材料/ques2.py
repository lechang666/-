import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt


def find(str,G):
    x=0
    for u,v,d in G.edges(data=True):
        if v==str:
            x=x+d['货量']
        if u==str:
            x=x-d['货量']
    return x

edges_df=pd.read_csv('附件3.csv',encoding='utf-8')
G=nx.from_pandas_edgelist(
    edges_df,
    source='始发分拣中心',
    target='到达分拣中心',
    edge_attr='货量',
    create_using=nx.DiGraph()
)
future_edges_df=pd.read_csv('附件4.csv')

for _,row in future_edges_df.iterrows():
    src,dst=row['始发分拣中心'],row['到达分拣中心']
    if G.has_edge(src,dst):
        specific_avg =edges_df[
            (edges_df['始发分拣中心']==src)|(edges_df['到达分拣中心']==dst)
        ]['货量'].mean()
        G[src][dst]['货量']=specific_avg
    else:
        specific_avg=edges_df[
            (edges_df['始发分拣中心'] == src) | (edges_df['到达分拣中心'] == dst)
        ]['货量'].mean()
        G.add_edge(src, dst, 货量=specific_avg if not pd.isna(specific_avg) else 0)

for edge in G.edges(data=True):
    print(edge)

# # 基于问题一预测12月结果，对每个分拣中心货量进行修改，根据G.edges修改货量值，小时同理
# data=pd.read_csv('./data/结果表1.csv')
# modified_data = pd.DataFrame(columns=data.columns)
# # data=pd.read_csv('answer.csv',encoding='utf-8')
# for index,row in data.iterrows():
#     # 修改货量
#     row['货量']=row['货量']+find(row['分拣中心'],G)
#     # 将修改后的行添加到新的 DataFrame
#     modified_data = modified_data._append(row, ignore_index=True)
#
# modified_data.to_csv('ques2_1.csv',index=False)

# 小时
data=pd.read_csv('./data/结果表2.csv')
modified_data = pd.DataFrame(columns=data.columns)
# data=pd.read_csv('answer.csv',encoding='utf-8')
for index,row in data.iterrows():
    # 修改货量
    row['货量']=row['货量']+find(row['分拣中心'],G)/24
    # 将修改后的行添加到新的 DataFrame
    modified_data = modified_data._append(row, ignore_index=True)

modified_data.to_csv('ques2_2.csv',index=False)