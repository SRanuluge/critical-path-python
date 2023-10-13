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
            max_early_finish = max([di_graph.nodes[predecessor]['EF'] for predecessor in di_graph.predecessors(node)], default=0)
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


def visualize_graph(di_graph, critical_path):
    """Get all the node values and visualizing the graph, we can set node position using pos values"""
    pos = {'A': [0, -0.50], 'B': [-0.5, 0.20], 'C': [1, -0.05], 'D': [2, -0.75], 'E': [3, 0.15], 'F': [4, 0],
           'G': [5, 0.25], 'H': [2, -0.25], 'I': [3, 0.50]}
    nodes = di_graph.nodes
    node_colors = ['red' if node in critical_path else 'green' for node in di_graph.nodes]
    nx.draw_networkx(di_graph, pos, nodelist=nodes, with_labels=True, node_size=1000, node_color=node_colors)
    edge_labels = {(u, v): f"LF: {di_graph.nodes[v]['LF']}" for u, v in di_graph.edges}
    nx.draw_networkx_edge_labels(di_graph, pos, edge_labels=edge_labels)
    plt.ylim(-1, 1)
    plt.axis('off')
    plt.show()


def main(data):
    data_frame = pd.DataFrame(data)
    di_graph = nx.DiGraph()
    create_tasks(di_graph, data_frame)
    calculate_early_time(di_graph)
    calculate_late_time(di_graph)
    critical_path = indentify_critical_path(di_graph)
    visualize_graph(di_graph, critical_path)


def get_data(filename):
    """ Get data from csv file and create a dictionary as below example
    {
    'Task': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
   'Duration': [6, 9, 10, 8, 5, 6, 5, 8, 5],
   'Dependencies': [None, None, ['A', 'B'], ['C'], ['C'], ['E', 'D'], ['F'], ['F'], ['C']]
    }
    """
    data = pd.read_csv(filename)
    dictionary = dict()
    dictionary['Task'] = [task.upper() for task in data['activity']]
    dictionary['Duration'] = [int(x) for x in data['days']]
    dictionary['Dependencies'] = list(data['predecessors'])
    validated_predecessor_list = []
    for dep in data['predecessors']:
        if type(dep) is str:
            validated_predecessor_list.append(dep.upper().split(','))
        else:
            validated_predecessor_list.append(None)
    dictionary['Dependencies'] = validated_predecessor_list
    return dictionary


main(get_data('critical_path_data.csv'))
