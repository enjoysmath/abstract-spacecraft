from PyQt5.QtCore import QThread
import _pickle as pickle
from networkx_tools import networkx_graph
import networkx as nx

class LibraryCompilerThread(QThread):
    
    def __init__(self, filenames:list):
        super().__init__()
        self._filenames = filenames
        self._compiledGraph = nx.Graph()
        
    def run(self):
        for filename in self._filenames:
            with open(filename, 'rb') as file:
                view = pickle.load(file)
                graph = networkx_graph(view.scene().items())
                self._compiledGraph.add_nodes_from(graph.nodes())
                self._compiledGraph.add_edges_from(graph.edges())
                
        print(self._compiledGraph)
        print(self._compiledGraph.nodes())
        print(self._compiledGraph.edges())