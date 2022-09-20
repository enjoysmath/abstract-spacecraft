from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from core.networkx_tools import networkx_graph
import networkx as nx

class LibraryCompilerThread(QThread):
    
    def __init__(self, filenames:list):
        super().__init__()
        self._filenames = filenames
        self._compiledGraph = nx.MultiDiGraph()
        
    def run(self):
        app = QApplication.instance()
        
        for filename in self._filenames:
            documents = app.documents_from_app_data(filename)
            
            for document in documents:
                canvases = document.language_canvases
                for canvas in canvases:
                    graph = networkx_graph(canvas.items())
                    self._compiledGraph.add_nodes_from(graph.nodes())
                    self._compiledGraph.add_edges_from(graph.edges())
                
    @property
    def filenames(self):
        return self._filenames
    
    @property
    def compiled_graph(self):
        return self._compiledGraph