# prototype API for IPySig networkx-sigmajs app

from __future__ import print_function
from __future__ import division

from socketIO_client import SocketIO, BaseNamespace

import os
import sys
import re
import webbrowser as web
import subprocess as sbp
import time
import json

import networkx as nx

# package imports 
from ipysig.sigma_addon_methods import *
from ipysig.exceptions import * 


class Singleton(type):
    '''
    A singleton metaclass for the IpySig controller

    '''
    _inst = {}
    
    def __call__(cls, *args, **kwargs):
        
        if cls not in cls._inst:
            cls._inst[cls] = super(Singleton, cls).__call__(*args,**kwargs)
        
        return cls._inst[cls]



class PyNamespace(BaseNamespace):
    '''
    SocketIO.client namespace. callback initializes a browser
    '''
    # callback established here
    def on_pyconnect_response(self, package):

        print('Node received: ' + package['echo_name'])               # callback from 
        web.open_new_tab('http://localhost:'+ package['http_port']) #TODO: check package for bad url
        time.sleep(1)    # possibly not needed


class IPySig(object):
    '''
    Main graph controller object -- keeper of the express server process

    This is a Singleton instance. References to graphs are kept in the _store dict and called by node via a class method

    Example:
        g = nx.Graph()  
        h = nx.Graph()
          
        ctrl = IPySig('path/to/nodeapp')   # load express, init datastore and inject nx.Graph object 
        ctrl.connect(g, 'key_name')    # sets key name and graph instance in datastore, spins up the browser and passes this data to sigma app 
        ctrl.connect(h, 'key_name')
    '''

    __metaclass__ = Singleton   # makes IPySig a singleton object 

    _store = {}  # store all instances keyed by name -- possibly used ordered dict so that node
    url = None          # url and token of currently running notebook server
    token = None          
    exp_process = None   # the express process
    activated = False    # sanity check for _sigma_api_injection call
    

    def __init__(self, node_path):
        # one time initialization
        self.node_path = node_path  # TODO: error check path for validity and possibly to see if the app is listed in the proper directory

        if not self.__class__.activated:                   
            self._sigma_api_injector()  # this injects our api into the networkx Graph class 
            self.__class__.activated = True    # Sigma networkx API is already activated - bypasses the injector

        if self.__class__.url is None:
            self._get_url_oneserver()  # gets the url ## TODO Catch attribute errors if no Notebook server is running

        if self.__class__.exp_process is None:
            self.init_express() # threading and subprocess calls run_node if subprocess not running

    #Anything node interacts with for IPySig objects must be a class method
    #class methods to help interact with globals: store{}, url, and token

    @classmethod
    def export_graph_instance(cls, name):   # TODO will need to check for key errors
        cls._store[name].sigma_make_graph()  # TODO error checking
        export = cls._store[name].sigma_export_json() # TODO error checking

        return export 


    def connect(self, graph, key_name):
        '''
        PUBLIC - stores a graph/key_name and emits those to a running node express server
        :CALLS: _emit_instance_name()

        '''
        self.__class__._store[key_name] = graph # TODO:: error check        
        self._emit_instance_name(key_name)   # send instance name and bind with browser socket id


    def disconnect(self, key_name):
        '''
        PUBLIC

        :TODO
        :FIXME 
        public method that disconnects the graph from the app
        -> this would require another emit using the py-room namespace method call as well as clean up code for the _store dict
        -> a callback could also be emitted here 

        '''
        pass

    def _get_url_oneserver(self):
        '''
        gets url and token if any and sets them... run once - need to error check here
        current implementation hard coded to work with only one running server
        '''
        # TODO: error checking target string
        out = sbp.check_output(['jupyter','notebook','list']).split('\n')[1].split(' ')[0]  # pulls out single url
        self.__class__.url = re.match(r'http://.+/',out).group()
        token = re.search(r'(?<=token=).+',out)

        if token:
            self.__class__.token = token.group()

    def init_express(self):
        '''
        PUBLIC
        calls the express app using _run_node().. not sure if this should be on a new thread.. 
        
        '''
        if self.__class__.exp_process is None:
            
            self.__class__.exp_process = self._run_node()  # TODO:: error check
            print('loading express... ')
            time.sleep(1)
            print('IPySig express has started... PID: '+ str(self.__class__.exp_process.pid))
        
        else:
            print('IPySIg is already running... PID: ' + str(self.__class__.exp_process))

    def _emit_instance_name(self, key_name):
        '''
        opens a socket and emits the user given instance name to express app
        CALLED BY: connect()
            
        '''
        with SocketIO('localhost', 3000) as socket:
            py_namespace = socket.define(PyNamespace, '/py')
            py_namespace.emit('py-object-name', key_name)
            socket.wait(seconds=1) # blocks for one second to wait for callbacks


    def _run_node(self):
        '''
        Runs the node express script with command arguments for baseUrl and token

        :CALLED BY: _init_express()
        :RETURNS: a subprocess with the node command running or None if fail

        '''
        express_app = None
        
        node_command = ['node', self.node_path +'/index.js', '--baseUrl', self.__class__.url]
        if self.__class__.token:
            node_command.append('--token={}'.format(self.__class__.token)) # attach if running notebook has token (4.2.3+)

        print(' '.join(node_command))      
        express_app = sbp.Popen(node_command, stdout=sbp.PIPE, bufsize=1, universal_newlines=True)  # TODO:: error check

        return express_app


    def kill_express_process(self):

        #if IPySig.exp_process is not None or IPySig.exp_process.poll() is None:
        
        if self.__class__.exp_process is not None:
            self.__class__.exp_process.kill()
            print(str(self.__class__.exp_process.pid) + ' has been killed')

            self.__class__.exp_process = None
        else:
            print('There is currently no IPySig.exp_process running')
    
    
    def _sigma_api_injector(self):
        '''
        injects sigma API methods into the nx.Graph class
        CALLED BY: __init__()
        '''    
        nx.Graph.sigma_make_graph = sigma_make_graph          
        nx.Graph.sigma_export_json = sigma_export_json        

        nx.Graph.sigma_add_degree_centrality = sigma_add_degree_centrality
        nx.Graph.sigma_add_betweenness_centrality = sigma_add_betweenness_centrality
        nx.Graph.sigma_add_pagerank = sigma_add_pagerank
        
        nx.Graph.sigma_node_add_extra = sigma_node_add_extra
        nx.Graph.sigma_choose_edge_color = sigma_choose_edge_color
        nx.Graph.sigma_build_pandas_dfs = sigma_build_pandas_dfs
        nx.Graph.sigma_edge_weights = sigma_edge_weights

        nx.Graph.sigma_color_picker = sigma_color_picker
        nx.Graph.sigma_assign_node_colors = sigma_assign_node_colors

        nx.Graph.sigma_node_add_color_node_type = sigma_node_add_color_node_type
        nx.Graph.sigma_node_add_label = sigma_node_add_label

