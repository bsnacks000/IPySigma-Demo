'''
this is a module of add-on methods that get injected into the nx.Graph class within IPySig
Sigma calls these on graph object instances stored in the IPySig data store

'''
import pandas as pd
import networkx as nx
from numpy import cos, sin, pi
from numpy.random import randint 

import json

import logging
logger = logging.getLogger(__name__)

from exceptions import IPySigmaGraphNodeIndexError, \
        IPySigmaGraphEdgeIndexError, IPySigmaGraphDataFrameValueError, \
        IPySigmaGraphJSONValueError, IPySigmaNodeTypeError, IPySigmaLabelError


#PUBLIC API

def sigma_make_graph(self):
    '''
    A method that serves as a rbuild script for the sigma add on methods
    adds centrality measures , and extra attributes that sigma needs for node and edgelists
    '''

    self.sigma_add_degree_centrality()
    self.sigma_add_pagerank()
    self.sigma_add_betweenness_centrality()
    
    self.sigma_nodes, self.sigma_edges = self.sigma_build_pandas_dfs()  # makes df and assigns sigma_nodes and sigma_edges instance variables
    
    try:
        if len(self.sigma_nodes.index) == 0 or len(self.sigma_nodes.columns) == 0:
            raise IPySigmaGraphDataFrameValueError('Sigma Node and Edge dataframes are empty')

    except IPySigmaGraphDataFrameValueError as err:
        logger.error("Sigma Node and Edge dataframes are empty ")
        raise err

    try:
        self.sigma_node_add_extra()  # adds the extra node attributes to the data frame

    except IPySigmaNodeTypeError as err:
        logger.warn('No node_type field detected for node attributes: using default color for all nodes')

    except IPySigmaLabelError as err:
        logger.warn('No label field detected for node attributes: using node id for node label')


    self.sigma_edge_weights()  # if graph has weighted edges this adds that attribute to the list
    
    
def sigma_export_json(self):
    '''
    sets and returns obj dictionary with node and edge list arrays(sigma compatible)
    assuming all goes well above, this method returns the sigma_json graph object
    '''
    

    try:

        sigma_obj = { 'error': 'false', 'graph': {} }  
        sigma_obj['graph']['nodes'] = self.sigma_nodes.to_dict('records')
        sigma_obj['graph']['edges'] = self.sigma_edges.to_dict('records')
        
        if len(sigma_obj['graph']['nodes']) == 0:
            raise IPySigmaGraphJSONValueError(' Sigma JSON Export Error ')


    except AttributeError as err: 
        logger.warning('Sigma Node and Edges have not been set yet: make sure G.sigma_make_graph() has been called first')
        sigma_obj['error'] = 'true'


    except IPySigmaGraphJSONValueError as err:
        logger.warning('Sigma JSON object node and edgelists are empty') 
        sigma_obj['error'] = 'true'


    return json.dumps(sigma_obj)


def sigma_add_degree_centrality(self):
    dc = nx.degree_centrality(self)
    nx.set_node_attributes(self, 'sigma_deg_central',dc)


def sigma_add_betweenness_centrality(self):
    bc = nx.betweenness_centrality(self)
    nx.set_node_attributes(self,'sigma_between_central',bc)


def sigma_add_pagerank(self):
    pr = nx.pagerank(self)
    nx.set_node_attributes(self, 'sigma_pagerank',pr)


def sigma_build_pandas_dfs(self):
    '''
    dumps graph data into pandas dfs... returns a node and edge dataframe
    for nodes just need to dump attribute dictionary
    
    Throws index errors if node or edgelists are blank

    :returns: self.sigma_nodes, self.sigma_edges
    '''
    
    try:

        nodelist = self.nodes(data=True)   
        
        if len(nodelist) == 0:
            raise IPySigmaGraphNodeIndexError('nx.Graph.nodes list is empty')

        nodes = {}

        nodes['id'] = [i[0] for i in nodelist]       
        for k in nodelist[0][1].keys():   # the api always injects at least centrality measuers
            nodes[k] = [i[1][k] for i in nodelist]
    
        e = self.edges(data=True)
        
        if len(e) == 0:
            raise IPySigmaGraphEdgeIndexError('nx.Graph.edges list is empty')

        edgelist = [0 for i in xrange(len(self.edges()))] # init for optimization (large edgelists)

        for i in range(len(edgelist)):
            edgelist[i] = {'id': i, 'source':e[i][0], 'target':e[i][1]}
            if (len(e[i][2]) != 0):   # if edge weight exists
                edgelist[i]['weight'] = e[i][2]['weight']


    except (IPySigmaGraphNodeIndexError, IPySigmaGraphEdgeIndexError) as err:
        logger.error("Node and Edge lists of nx.Graph object have been left blank ")
        raise 


    sigma_edges = pd.DataFrame(edgelist)   # these are the pandas dfs that will get exported
    sigma_nodes = pd.DataFrame(nodes)

    return sigma_nodes, sigma_edges




def sigma_node_add_extra(self):
    # adds extra stuff to the nodes list needed for sigma
    node_len = len(self.sigma_nodes)

    # spreads nodes in a circle for forceAtlas2
    x = 10 * cos(2 * randint(0,node_len,node_len) * pi/node_len)
    y = 10 * sin(2 * randint(0,node_len,node_len) * pi/node_len)

    # stuff for sigma nodes
    self.sigma_nodes['x'] = x
    self.sigma_nodes['y'] = y
    self.sigma_nodes['size'] = 0.25 + 15 * self.sigma_nodes['sigma_deg_central']  # set to degree central

    # color picker logic and label logic
    # NOTE errors are raised here and handled as warnings in sigma_build method
    #TODO this is confusing
    default_node_color = '#79a55c'
    
    try:
        if 'node_type' not in self.sigma_nodes:
            self.sigma_nodes['color'] = default_node_color
            raise IPySigmaNodeTypeError

        

        colors = self.sigma_color_picker()
        self.sigma_nodes['color'] = self.sigma_nodes.apply(self.sigma_assign_node_colors, args=(colors,), axis=1) 

    except IPySigmaNodeTypeError as err: 
        raise

def sigma_add_label(self):
    try:

        if 'label' not in self.sigma_nodes:   # assigns the label field to id if label is not provided
            self.sigma_nodes['label'] = self.sigma_nodes['id']
            raise IPySigmaLabelError    

    except IPySigmaLabelError as err:
        raise 

def sigma_color_picker(self):
    '''
    helper method that picks colors based on node_type column
    '''
    if 'node_type' not in self.sigma_nodes:
        return None
    
    # assign colors based for each unique value in node_type 
    node_type_vals_list = self.sigma_nodes['node_type'].unique().tolist()
    node_type_color_dict = {}

    for node_type in node_type_vals_list:
        r = lambda: randint(0,255)
        color = '#%02X%02X%02X' % (r(),r(),r())
        node_type_color_dict[node_type] = color 

    return node_type_color_dict


def sigma_assign_node_colors(self, row, color_dict):
    '''
    callback for sigma color picker apply method
    '''
    return color_dict[row['node_type']]



def sigma_edge_weights(self):
    # if edges have weight attribute change column name to size
    if 'weight' in self.sigma_edges.columns:
        self.sigma_edges['size'] = self.sigma_edges['weight'] * 2
        # color code edges
        self.sigma_edges['color'] = self.sigma_edges.apply(self.sigma_choose_edge_color, axis=1)
    else:
        self.sigma_edges['color'] = '#d3d3d3' # grey if not weighted


def sigma_choose_edge_color(self,row):
    # callback for sigma_edge_weights 
    # bins the color weight and returns a darker hex value as it increases
    if row['weight'] == 1:
        return 'rgba(211, 211, 211, 0.1)'
    if row['weight'] >= 2 and row['weight'] < 5:
        return 'rgba(214, 50, 50, 0.7)'
    if row['weight'] >= 5:
        return 'rgba(112, 0, 0, 0.95)'



