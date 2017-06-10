'''
this is a module of add-on methods that get injected into the nx.Graph class within IPySig
Sigma calls these on graph object instances stored in the IPySig data store

'''
import pandas as pd
import networkx as nx
from numpy import cos, sin, pi
from numpy.random import randint 
import json

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
    self.sigma_node_add_extra()  # adds the extra node attributes to the data frame
    self.sigma_edge_weights()  # if graph has weighted edges this adds that attribute to the list
    
    
def sigma_export_json(self):
    '''
    sets and returns obj dictionary with node and edge list arrays(sigma compatible)
    assuming all goes well above, this method returns the sigma_json graph object
    '''
    
    sigma_obj = { 'graph': {} }  
    sigma_obj['graph']['nodes'] = self.sigma_nodes.to_dict('records')
    sigma_obj['graph']['edges'] = self.sigma_edges.to_dict('records')
    
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

    :returns: self.sigma_nodes, self.sigma_edges
    '''
    nodelist = self.nodes(data=True)   
    nodes = {}

    nodes['id'] = [i[0] for i in nodelist]       
    for k in nodelist[0][1].keys():   # the api always injects at least centrality measuers
        nodes[k] = [i[1][k] for i in nodelist]
        

    # edges
    e = self.edges(data=True)
    edgelist = [0 for i in xrange(len(self.edges()))] # init for optimization (large edgelists)

    for i in range(len(edgelist)):
        edgelist[i] = {'id': i, 'source':e[i][0], 'target':e[i][1]}
        if (len(e[i][2]) != 0):   # if edge weight exists
            edgelist[i]['weight'] = e[i][2]['weight']


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
    self.sigma_nodes['color'] = '#79a55c' 
    self.sigma_nodes['size'] = 0.25 + 15 * self.sigma_nodes['sigma_deg_central']  # set to degree central


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


if __name__ == '__main__':
    
    import networkx as nx

    nx.Graph.sigma_make_graph = sigma_make_graph          # these each need to be tested 
    nx.Graph.sigma_export_json = sigma_export_json

    nx.Graph.sigma_add_degree_centrality = sigma_add_degree_centrality
    nx.Graph.sigma_add_betweenness_centrality = sigma_add_betweenness_centrality
    nx.Graph.sigma_add_pagerank = sigma_add_pagerank
        
    nx.Graph.sigma_node_add_extra = sigma_node_add_extra
    nx.Graph.sigma_choose_edge_color = sigma_choose_edge_color
    nx.Graph.sigma_build_pandas_dfs = sigma_build_pandas_dfs
    nx.Graph.sigma_edge_weights = sigma_edge_weights


    G = nx.complete_graph(5)

    G.sigma_make_graph()
    print G.sigma_nodes
    print G.sigma_edges
    print(G.sigma_export_json())

