import matplotlib
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
import random

matplotlib.use('TkAgg')

def load_data(university_name):
    edges_file_path = f'universities_paths/{university_name}_paths.csv'  # 大学路径文件
    names_file_path = f'id_to_name/{university_name}_id_to_name.csv'  # 大学节点名称文件

    edges_data = pd.read_csv(edges_file_path, encoding='utf-8')
    names_data = pd.read_csv(names_file_path, encoding='utf-8')

    id_to_name = dict(zip(names_data['编号'], names_data['名称']))
    return edges_data, id_to_name

def find_shortest_path(G, start, end):
    return nx.shortest_path(G, source=start, target=end, weight='weight'), nx.shortest_path_length(G, source=start, target=end, weight='weight')

def create_graph(edges_data, id_to_name):
    G = nx.Graph()
    for index, row in edges_data.iterrows():
        start_name = id_to_name.get(row['起始点编号'], '未知')
        end_name = id_to_name.get(row['终止点编号'], '未知')
        if start_name != end_name:
            G.add_edge(start_name, end_name, weight=row['距离'])
    return G

def plot_graph(G, path, university_name):
    font = FontProperties(fname='C:\\Windows\\Fonts\\msyh.ttc', size=12)

    # 设置固定的随机种子
    np.random.seed(42)
    random.seed(42)

    # 使用 kamada_kawai_layout 布局
    pos = nx.kamada_kawai_layout(G, weight='weight')

    plt.figure(figsize=(16, 12))

    nx.draw(G, pos, node_color='skyblue', node_size=300, edge_color='k', with_labels=True, font_family=font.get_name(), font_size=10)
    nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='green', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=[path[0]], node_color='yellow', node_size=600)
    nx.draw_networkx_nodes(G, pos, nodelist=[path[-1]], node_color='red', node_size=600)

    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3)

    edge_labels = {(u, v): G[u][v]['weight'] for u, v in path_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_family=font.get_name())

    plt.title(f'{university_name} Campus Map: Shortest Path Highlighted', fontproperties=font)
    plt.axis('off')
    plt.show()

def main(university_name, start_node, end_node):
    edges_data, id_to_name = load_data(university_name)
    G = create_graph(edges_data, id_to_name)
    path, path_length = find_shortest_path(G, start_node, end_node)
    print(f"The shortest path is {path} with a distance of {path_length}")
    plot_graph(G, path, university_name)

# Call main function to run the program
if __name__ == "__main__":
    # 直接在此处指定参数
    university_name = "上海大学"
    start_node = "教学楼F"
    end_node = "超市Q"
    main(university_name, start_node, end_node)
