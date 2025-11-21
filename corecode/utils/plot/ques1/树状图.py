import graphviz
import os

# 创建目标目录（如果不存在）
target_dir = r'C:\Users\15963\Desktop\APMCM-training\results\figures\ques1\树状图'
os.makedirs(target_dir, exist_ok=True)  # exist_ok=True 避免目录已存在时报错

# 创建有向图，设置整体样式
dot = graphviz.Digraph(
    name='SoybeanDataHierarchy',
    format='png',
    graph_attr={
        'rankdir': 'TB',  # 从上到下布局
        'bgcolor': '#f9f9f9',  # 背景色柔和
        'fontname': 'Arial',
        'fontsize': '10'
    },
    node_attr={
        'shape': 'box',  # 矩形节点
        'style': 'filled,rounded',  # 填充+圆角
        'fillcolor': '#e8f4f8',  # 节点填充色（淡蓝）
        'color': '#b3d9e6',  # 边框色（浅蓝）
        'fontname': 'Arial',
        'fontsize': '9',
        'margin': '0.3,0.2'  # 节点内边距，避免文字拥挤
    },
    edge_attr={
        'color': '#999999',  # 边的颜色（浅灰）
        'arrowsize': '0.8',  # 箭头大小
        'penwidth': '1'  # 边的宽度
    }
)

# 根节点
dot.node('root', 'Soybean Related Data', fillcolor='#d4e6f1')

# 一级节点：Trading Related Data
dot.node('t1', 'Trading Related Data')
dot.edge('root', 't1')
# 二级节点：Exchange Rate / Tariff
dot.node('t1a', 'Exchange Rate')
dot.node('t1b', 'Tariff')
dot.edge('t1', 't1a')
dot.edge('t1', 't1b')

# 一级节点：Trade Flow Data
dot.node('t2', 'Trade Flow Data', fillcolor='#e8f5e9')  # 淡绿区分
dot.edge('root', 't2')
# 二级节点：Import/Export Data
dot.node('t2a', 'Import Data:\nChina\'s Soybean Imports')  # 换行避免过长
dot.node('t2b', 'Export Data:\nSoybean Production & Exports')
dot.edge('t2', 't2a')
dot.edge('t2', 't2b')

# 一级节点：Price Data
dot.node('t3', 'Price Data', fillcolor='#fff3e0')  # 淡黄区分
dot.edge('root', 't3')
# 二级节点：International/Country-specific Price
dot.node('t3a', 'International Futures Price:\nUS Soybean Price Index, Price Data')
dot.node('t3b', 'Country-specific Price:\nBrazil/Argentina Soybean Price Data')
dot.edge('t3', 't3a')
dot.edge('t3', 't3b')

# 渲染并保存图片到指定路径
dot.render('soybean_data_hierarchy', directory=target_dir, cleanup=True)  # cleanup=True 删除中间文件
print(f"图表已保存到：{target_dir}\\soybean_data_hierarchy.png")