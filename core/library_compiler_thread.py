from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
import _pickle as pickle
from lang.networkx_tools import networkx_graph
import networkx as nx
from gfx.language_gfx_view import LanguageGfxView
from gfx.logical_rule_view import LogicalRuleView

class LibraryCompilerThread(QThread):
    
    def __init__(self, filenames:list):
        super().__init__()
        self._filenames = filenames
        self._compiledGraph = nx.Graph()
        
    def run(self):
        app = QApplication.instance()
        
        for filename in self._filenames:
            documents = app.documents_from_app_data(filename)
            
            for document in documents:
                canvases = document.language_canvases
                for canvas in canvases:
                    graph = networkx_graph(canvas.items())
                    print(graph)
            #// graph = networkx_graph(view.scene().items())
            #// self._compiledGraph.add_nodes_from(graph.nodes())
            #// self._compiledGraph.add_edges_from(graph.edges())
                
        print(self._compiledGraph)
        print(self._compiledGraph.nodes())
        print(self._compiledGraph.edges())