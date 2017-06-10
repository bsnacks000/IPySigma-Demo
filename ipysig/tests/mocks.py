'''
A module with some mock classes that can or have been used for testing/debugging
'''
import json
import networkx as nx
from ipysig.sigma_addon_methods import *


class DummyGraph(object):
    ''' simulates storage of a JSON graph.. method gets called and sends to node server'''
    _store = {}

    def __init__(self):
        self.graph = {
            "graph": {
                "nodes": [{"id": "n0","label": "A node","x": 0,"y": 0,"size": 3},{"id": "n1","label": "Another node","x": 3,"y": 1,"size": 2},{"id": "n2","label": "And a last one","x": 1,"y": 3,"size": 1}],
                "edges": [{"id": "e0","source": "n0","target": "n1"},{"id": "e1","source": "n1","target": "n2"},{"id": "e2","source": "n2","target": "n0"}]
            }
        }
        self.name = 'dumb_graph'
        DummyGraph._store[self.name] = self

    @classmethod
    def get_graph(cls, name):
        return json.dumps(cls._store[name].graph)


class InjectedGraph(object):
    '''
    returns an injected graph for development testing if not already done

    '''

    def __new__(cls, g=None):

        cls.g = g or nx.Graph()

        if not hasattr(cls.g,'sigma_make_graph'):

            nx.Graph.sigma_make_graph = sigma_make_graph          
            nx.Graph.sigma_export_json = sigma_export_json

            nx.Graph.sigma_add_degree_centrality = sigma_add_degree_centrality
            nx.Graph.sigma_add_betweenness_centrality = sigma_add_betweenness_centrality
            nx.Graph.sigma_add_pagerank = sigma_add_pagerank
            
            nx.Graph.sigma_node_add_extra = sigma_node_add_extra
            nx.Graph.sigma_choose_edge_color = sigma_choose_edge_color
            nx.Graph.sigma_build_pandas_dfs = sigma_build_pandas_dfs
            nx.Graph.sigma_edge_weights = sigma_edge_weights

        return cls.g 