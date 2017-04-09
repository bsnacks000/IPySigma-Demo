'''
A module with some mock classes that can or have been used for testing/debugging
'''
import json


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
