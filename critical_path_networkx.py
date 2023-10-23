import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


def create_tasks(di_graph, df):
    """Creating Tasks Using Graph and Data Frame"""
    for index, row in df.iterrows():
        di_graph.add_node(row['Task'], duration=row['Duration'])
        if row['Dependencies']:
            if isinstance(row['Dependencies'], list):
                for dep_task in row['Dependencies']:
                    di_graph.add_edge(dep_task, row['Task'])
            else:
                di_graph.add_edge(row['Dependencies'], row['Task'])


def calculate_early_time(di_graph):
    """Calculate Early Start Time and Early Finish Time and Assign to Node"""

    for node in nx.topological_sort(di_graph):
        if not di_graph.predecessors(node):
            di_graph.nodes[node]['ES'] = 0
            di_graph.nodes[node]['EF'] = di_graph.nodes[node]['duration']
        else:
            max_early_finish = max([di_graph.nodes[predecessor]['EF'] for predecessor in di_graph.predecessors(node)], default=0.0)
            di_graph.nodes[node]['ES'] = max_early_finish

            di_graph.nodes[node]['EF'] = max_early_finish + di_graph.nodes[node]['duration']




def calculate_late_time(di_graph):
    """Calculate Latest Start Time and Latest Finish Time and Assign to Node"""
    predecessor_list = []
    earliest_finish = []
    for node in list(nx.topological_sort(di_graph))[::-1]:
        for predecessor in di_graph.predecessors(node):
            predecessor_list.append(predecessor)
            earliest_finish.append(di_graph.nodes[node]['EF'])
    for node in list(nx.topological_sort(di_graph))[::-1]:
        if node not in predecessor_list:
            di_graph.nodes[node]['LF'] = max(earliest_finish)
        else:
            di_graph.nodes[node]['LF'] = min([di_graph.nodes[successor]['LS'] for successor in di_graph.successors(node)],
                                      default=di_graph.nodes[node]['EF'])
        di_graph.nodes[node]['LS'] = di_graph.nodes[node]['LF'] - di_graph.nodes[node]['duration']


def indentify_critical_path(di_graph):
    """Identify critical path using slack (delta) if there is no slack, it's mean it's a critical task"""
    for node in di_graph.nodes:
        di_graph.nodes[node]['delta'] = di_graph.nodes[node]['LF'] - di_graph.nodes[node]['EF']  # calculating Slack
    return [node for node in di_graph.nodes if di_graph.nodes[node]['delta'] == 0]


def creating_data_table(di_graph, df):
    """Creating data frame and csv file"""
    df2 = pd.DataFrame({
        'Description': df['Description'],
        'Activity': df['Task'],
        'Predecessors': df['Dependencies'],
        'Days': df['Duration'],
        'ES': pd.Series([di_graph.nodes[node]['ES'] for node in di_graph]),
        'EF': pd.Series([di_graph.nodes[node]['EF'] for node in di_graph]),
        'LS': pd.Series([di_graph.nodes[node]['LS'] for node in di_graph]),
        'LF': pd.Series([di_graph.nodes[node]['LF'] for node in di_graph]),
        'Slack': pd.Series([di_graph.nodes[node]['delta'] for node in di_graph]),
    })
    return df2


def visualize_graph(di_graph, critical_path, file_name , data_frame):
    """Get all the node values and visualizing the graph, we can set node position using pos values"""
    pos = {'A': [0, -0.25], 'B': [0, 1], 'C': [3, 1], 'D': [3, -1.2], 'E': [3, -0.25], 'F': [6, -0.25],
           'G': [10, -0.25], 'H': [10, -1.2], 'I': [7, 1], 'J': [10, 1], 'K': [14, 1],'L': [14, -0.25], 'M': [14, -1.2], 'N': [14, 0.40], 'O': [2, -1.2], 'P': [4, -1.2]}

    node_lebels_pos = {}
    for node, (x, y) in pos.items():
        node_lebels_pos[node] = (x, y + 0.12)

    nodes = di_graph.nodes
    node_colors = ['#e41749' if node in critical_path else '#6CF990' for node in di_graph.nodes]
    nx.draw_networkx(di_graph, pos, nodelist=nodes, with_labels=True, node_size=1000, node_color=node_colors)

    # edge_labels = {(u, v): f"LF: {di_graph.nodes[v]['LF']}" for u, v in di_graph.edges}
    node_labels = {n: f"(ES: {d['ES']}, LF: {d['LF']}, Duration: {d['duration']})" for n, d in di_graph.nodes(data=True)}

    # nx.draw_networkx_edge_labels(di_graph, pos, edge_labels=None, font_size=10, font_color="gray")
    nx.draw_networkx_labels(di_graph, pos=node_lebels_pos, labels=node_labels, font_color="black", font_size=10,
                            font_family="Times New Roman", horizontalalignment='right')
    """Displaying Description"""
    for y, des in enumerate(data_frame['Description']):
        plt.text(-2, -1.6 - y*0.1,  f"{data_frame['Task'][y]} = {des}")

    plt.xlim(-3, 15)
    plt.axis('off')
    plt.title(f"Network Diagram for {file_name}", loc='center')
    plt.show()


def get_data(filename):
    """ Get data from csv file and create a dictionary as below example
    {
    'Description':[]
    'Task': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
   'Duration': [6, 9, 10, 8, 5, 6, 5, 8, 5],
   'Dependencies': [None, None, ['A', 'B'], ['C'], ['C'], ['E', 'D'], ['F'], ['F'], ['C']]
    }
    """
    data = pd.read_csv(filename)
    dictionary = dict()
    dictionary['Description'] = [task.upper() for task in data['Description']]
    dictionary['Task'] = [task.upper() for task in data['Activity']]
    dictionary['Duration'] = [float(x) for x in data['Days']]
    validated_predecessor_list = []
    for dep in data['Predecessors']:
        if type(dep) is str:
            validated_predecessor_list.append(dep.upper().split(','))
        else:
            validated_predecessor_list.append(None)
    dictionary['Dependencies'] = validated_predecessor_list
    return dictionary


def main(file_name):
    data = get_data(file_name)
    data_frame = pd.DataFrame(data)
    di_graph = nx.DiGraph()
    create_tasks(di_graph, data_frame)
    calculate_early_time(di_graph)
    calculate_late_time(di_graph)
    critical_path = indentify_critical_path(di_graph)
    finalDf = creating_data_table(di_graph,data_frame)
    finalDf.to_csv('final-emp-table.csv', index=False)
    visualize_graph(di_graph, critical_path, file_name, data_frame)


main("emp-data.csv")
