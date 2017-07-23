'''
nose tests for ipysig.sigma_addon_methods.py
'''

import unittest 
import networkx as nx
import pandas as pd
import json

from ..sigma_addon_methods import *
from ..exceptions import IPySigmaGraphDataFrameValueError, \
    IPySigmaGraphEdgeIndexError, IPySigmaGraphNodeIndexError, \
    IPySigmaNodeTypeError, IPySigmaLabelError
from .mocks import InjectedGraph

import logging
logger = logging.getLogger(__name__)


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

        nx.Graph.sigma_node_add_color_node_type = sigma_node_add_color_node_type
        nx.Graph.sigma_node_add_label = sigma_node_add_label

        nx.Graph.sigma_color_picker = sigma_color_picker
        nx.Graph.sigma_assign_node_colors = sigma_assign_node_colors
 
    def setUp(self):

        self.graph = nx.complete_graph(10)
        self.weighted_graph =nx.Graph()

        self.weighted_graph.add_edge('a','b',weight=0.6)
        self.weighted_graph.add_edge('a','c',weight=0.2)
        self.weighted_graph.add_edge('c','d',weight=0.1)
        self.weighted_graph.add_edge('c','e',weight=0.7)

        self.graph_attr = nx.Graph()
        self.graph_attr.add_edge(0,1)
        self.graph_attr.add_edge(1,2)
        self.graph_attr.add_edge(3,0)
        self.graph_attr.add_node(0,{'node_type':'A', 'label':'node0'})
        self.graph_attr.add_node(1,{'node_type':'A', 'label':'node1'})
        self.graph_attr.add_node(2,{'node_type': 'B', 'label':'node2'})
        self.graph_attr.add_node(3,{'node_type': 'C', 'label':'node2'})    



    def tearDown(self):
        self.graph = None
        self.weighted_graph = None
        self.graph_attr = None

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
        
        correct_nodes = ['id','x','y','label','node_type','color','size', 'sigma_deg_central', 'sigma_pagerank', 'sigma_between_central']
        correct_edges = ['id','source', 'target', 'color']
        correct_edges_weighted = ['id', 'source','target','color','weight','size']

        self.graph.sigma_make_graph()
        self.weighted_graph.sigma_make_graph()

        node_col_list = self.graph.sigma_nodes.columns.tolist()
        edge_col_list = self.graph.sigma_edges.columns.tolist()
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


    def test_sigma_build_pandas_dfs_raise_node_index_error_if_blank(self):

        blank_graph = InjectedGraph()
        self.assertRaises(IPySigmaGraphNodeIndexError, blank_graph.sigma_make_graph)


    def test_sigma_build_pandas_dfs_raise_edge_index_error_if_blank(self):

        blank_graph = InjectedGraph()
        blank_graph.add_nodes_from(['a','b','c'])
        self.assertRaises(IPySigmaGraphEdgeIndexError, blank_graph.sigma_make_graph)


    def test_sigma_build_pandas_dfs_raise_error_if_none(self):

        def sigma_build_pandas_dfs_none():
            '''
            this simulates a bogus override of the sigma_build_pandas_df method
            '''
            return pd.DataFrame(None), pd.DataFrame(None)

        self.graph.sigma_build_pandas_dfs = sigma_build_pandas_dfs_none

        self.assertRaises(IPySigmaGraphDataFrameValueError, self.graph.sigma_make_graph)



    def test_export_json_flag_if_empty(self):
        
        def sigma_build_pandas_dfs_none():
            '''
            this simulates a bogus override of the sigma_build_pandas_df method
            '''
            return pd.DataFrame(None), pd.DataFrame(None)

        self.graph.sigma_build_pandas_dfs = sigma_build_pandas_dfs_none
        self.graph.sigma_nodes, self.graph.sigma_edges = self.graph.sigma_build_pandas_dfs()

        j = self.graph.sigma_export_json()

        self.assertTrue(json.loads(j)['error'] == 'true')

    def test_export_json_flag_if_dfs_do_not_exist(self):
        

        j = self.graph.sigma_export_json()

        self.assertTrue(json.loads(j)['error'] == 'true')


    def test_sigma_color_picker_correctly_assigns_random_colors(self):
        
        self.graph_attr.sigma_make_graph()


        n1_value = self.graph_attr.sigma_nodes['color'][0]
        n2_value = self.graph_attr.sigma_nodes['color'][1]
        n3_value = self.graph_attr.sigma_nodes['color'][2]
        n4_value = self.graph_attr.sigma_nodes['color'][3]

        self.assertEqual(n1_value,n2_value)
        self.assertNotEqual(n3_value,n4_value)



    def test_sigma_node_add_color_raises_node_type_error(self):

        for node in self.graph_attr.nodes(data=True):
            del node[1]['node_type']

        self.graph_attr.sigma_nodes, self.graph_attr.sigma_edges = self.graph_attr.sigma_build_pandas_dfs()

        with self.assertRaises(IPySigmaNodeTypeError):
            self.graph_attr.sigma_node_add_color_node_type()



    def test_sigma_node_add_label_raises_label_error(self):

        for node in self.graph_attr.nodes(data=True):
            del node[1]['label']

        self.graph_attr.sigma_nodes, self.graph_attr.sigma_edges = self.graph_attr.sigma_build_pandas_dfs()

        with self.assertRaises(IPySigmaLabelError):
            self.graph_attr.sigma_node_add_label()


    def test_sigma_node_add_color_default_assigns_default_to_node_type(self):

        for node in self.graph_attr.nodes(data=True):
            del node[1]['node_type']

        self.graph_attr.sigma_make_graph()

        nt = self.graph_attr.sigma_nodes['node_type'].tolist()
        correct = ['undefined node_type' for i in range(4)]

        self.assertEqual(nt, correct) 



    def test_sigma_node_add_label_default_assigns_id_to_label(self):

        for node in self.graph_attr.nodes(data=True):
            del node[1]['label']

        self.graph_attr.sigma_make_graph()

        id_col = self.graph_attr.sigma_nodes['id'].tolist()
        label_col = self.graph_attr.sigma_nodes['label'].tolist()

        self.assertEqual(id_col, label_col)

