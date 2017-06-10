'''
nose tests for ipysig.sigma_addon_methods.py
'''

import unittest 
import networkx as nx
import pandas as pd

from ipysig.sigma_addon_methods import *



class TestSigmaAddOns(unittest.TestCase):

    @classmethod 
    def setUpClass(cls):
        nx.Graph.sigma_make_graph = sigma_make_graph          
        nx.Graph.sigma_export_json = sigma_export_json

        nx.Graph.sigma_add_degree_centrality = sigma_add_degree_centrality
        nx.Graph.sigma_add_betweenness_centrality = sigma_add_betweenness_centrality
        nx.Graph.sigma_add_pagerank = sigma_add_pagerank
        
        nx.Graph.sigma_node_add_extra = sigma_node_add_extra
        nx.Graph.sigma_choose_edge_color = sigma_choose_edge_color
        nx.Graph.sigma_build_pandas_dfs = sigma_build_pandas_dfs
        nx.Graph.sigma_edge_weights = sigma_edge_weights 
 
    def setUp(self):

        self.graph = nx.complete_graph(10)
        self.weighted_graph =nx.Graph()

        self.weighted_graph.add_edge('a','b',weight=0.6)
        self.weighted_graph.add_edge('a','c',weight=0.2)
        self.weighted_graph.add_edge('c','d',weight=0.1)
        self.weighted_graph.add_edge('c','e',weight=0.7)


    def tearDown(self):
        self.graph = None
        self.weighted_graph = None

    def test_make_graph(self):

        self.graph.sigma_make_graph()
        self.assertTrue(hasattr(self.graph, 'sigma_edges'))
        self.assertTrue(hasattr(self.graph, 'sigma_nodes'))    


    def test_degree_centrality_is_added_to_graph_obj(self):
        
        self.graph.sigma_add_degree_centrality()
        node_data = self.graph.nodes(data=True)

        for node in node_data:
            self.assertIn('sigma_deg_central',node[1])    


    def test_betweenness_centrality_is_added_to_graph_obj(self):
        
        self.graph.sigma_add_betweenness_centrality()
        node_data = self.graph.nodes(data=True)

        for node in node_data:
            self.assertIn('sigma_between_central',node[1])    


    def test_pagerank_is_added_to_graph_obj(self):
        
        self.graph.sigma_add_pagerank()
        node_data = self.graph.nodes(data=True)

        for node in node_data:
            self.assertIn('sigma_pagerank',node[1]) 


    def test_sigma_build_pandas_dfs_edges_nodes_exist(self):
    
        self.graph.sigma_nodes, self.graph.sigma_edges = self.graph.sigma_build_pandas_dfs()

        self.assertTrue(hasattr(self.graph, 'sigma_edges'))
        self.assertTrue(hasattr(self.graph, 'sigma_nodes'))

        self.weighted_graph.sigma_nodes, self.weighted_graph.sigma_edges = self.weighted_graph.sigma_build_pandas_dfs()

        self.assertTrue(hasattr(self.weighted_graph, 'sigma_edges'))
        self.assertTrue(hasattr(self.weighted_graph, 'sigma_nodes'))


    def test_sigma_build_pandas_dfs_edges_nodes_not_none(self):

        self.graph.sigma_nodes, self.graph.sigma_edges = self.graph.sigma_build_pandas_dfs()

        self.assertIsNotNone(self.graph.sigma_nodes)
        self.assertIsNotNone(self.graph.sigma_edges)

        self.weighted_graph.sigma_nodes, self.weighted_graph.sigma_edges = self.weighted_graph.sigma_build_pandas_dfs()

        self.assertIsNotNone(self.weighted_graph.sigma_nodes)
        self.assertIsNotNone(self.weighted_graph.sigma_edges)


    def test_extras_are_added_to_graph_obj(self):
        
        self.graph.sigma_make_graph()
        
        self.assertIn('y',self.graph.sigma_nodes) 
        self.assertIn('color',self.graph.sigma_nodes)  
        self.assertIn('size',self.graph.sigma_nodes)
        self.assertIn('x', self.graph.sigma_nodes)


    def test_edge_weight_color_size_are_set_if_exist(self):

        self.weighted_graph.sigma_nodes, self.weighted_graph.sigma_edges = self.weighted_graph.sigma_build_pandas_dfs()
        self.weighted_graph.sigma_edge_weights()

        self.assertIn('size', self.weighted_graph.sigma_edges)
        self.assertIn('color', self.weighted_graph.sigma_edges)


    def test_sigma_node_df_has_id(self):
        
        self.graph.sigma_nodes, self.graph.sigma_edges = self.graph.sigma_build_pandas_dfs()
        self.assertIn('id',self.graph.sigma_nodes)


    def test_sigma_make_graph_produces_neccesary_columns(self):
        
        correct_nodes = ['id','x','y','color','size', 'sigma_deg_central', 'sigma_pagerank', 'sigma_between_central']
        correct_edges = ['id','source', 'target', 'color']
        correct_edges_weighted = ['id', 'source','target','color','weight','size']

        self.graph.sigma_make_graph()
        self.weighted_graph.sigma_make_graph()

        node_col_list = self.graph.sigma_nodes.columns.tolist()
        edge_col_list = self.graph.sigma_edges.columns.tolist()
        print edge_col_list
        weight_edge_col_list = self.weighted_graph.sigma_edges.columns.tolist()

        for n in node_col_list:
            self.assertIn(n, correct_nodes)

        for e in edge_col_list:
            self.assertIn(e, correct_edges)

        for w in weight_edge_col_list:
            self.assertIn(w, correct_edges_weighted)


    def test_sigma_node_df_contains_additional_columns_if_available(self):
        
        nx.set_node_attributes(self.graph, 'some_attr', 'xxx')

        self.graph.sigma_make_graph()

        self.assertIn('some_attr',self.graph.sigma_nodes)


    def test_export_json(self):
        pass


    def test_sigma_build_pandas_dfs_raise_error_if_none(self):

        #TODO implement exception and test
        pass 
