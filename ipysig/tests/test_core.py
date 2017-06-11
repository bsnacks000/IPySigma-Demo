'''
nose tests for ipysig.core.py 

'''

import unittest
import os
import networkx as nx

from ..core import IPySig


#TODO mock out system calls and express process for tests

import unittest
from mock import patch

from ..core import IPySig


test_path = os.path.abspath(os.path.join('..','..','app'))

class TestIPySig(unittest.TestCase):
    

    @patch('ipysig.IPySig._get_url_oneserver', return_value='bypassed')
    @patch('ipysig.IPySig.init_express',return_value='bypassed')
    def test_IPySig_is_singleton(self,mock_get_url_oneserver,mock_init_express):


        ctrl = IPySig(test_path)
        ctrl2 = IPySig(test_path)
        
        self.assertTrue(ctrl is ctrl2)


    @patch('ipysig.IPySig._get_url_oneserver', return_value='bypassed')
    @patch('ipysig.IPySig.init_express',return_value='bypassed')
    def test_IPySig_set_to_true(self, mock_get_url_oneserver,mock_init_express):

        ctrl = IPySig(test_path)
        self.assertTrue(IPySig.activated)


    @patch('ipysig.IPySig._get_url_oneserver', return_value='bypassed')
    @patch('ipysig.IPySig.init_express',return_value='bypassed')
    def test_sigma_api_injector(self, mock_get_url_oneserver,mock_init_express):
        
        ctrl = IPySig(test_path)
        g = nx.Graph()

        self.assertTrue(hasattr(g, 'sigma_make_graph'))
        self.assertTrue(hasattr(g, 'sigma_export_json' ))
        self.assertTrue(hasattr(g, 'sigma_add_degree_centrality' ))
        self.assertTrue(hasattr(g, 'sigma_add_betweenness_centrality' ))
        self.assertTrue(hasattr(g, 'sigma_add_pagerank' ))
        self.assertTrue(hasattr(g, 'sigma_node_add_extra' ))
        self.assertTrue(hasattr(g, 'sigma_choose_edge_color'))
        self.assertTrue(hasattr(g, 'sigma_build_pandas_dfs'))
        self.assertTrue(hasattr(g, 'sigma_edge_weights'))
