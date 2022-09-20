from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from core.networkx_tools import build_networkx_graph
import networkx as nx

class LibraryCompilerThread(QThread):
    
    def __init__(self, filenames:list):
        super().__init__()
        self._filenames = filenames
        self._compiledGraph = nx.MultiDiGraph()
        
    def run(self):
        app = QApplication.instance()
        graph = nx.MultiDiGraph()
        node_id = 0
        
        for filename in self._filenames:
            documents = app.documents_from_app_data(filename)
            
            for document in documents:
                canvases = document.language_canvases
                for canvas in canvases:
                    node_id = build_networkx_graph(graph, items=canvas.items(), node_id=node_id)
                    
        self._compiledGraph = graph
        
    @property
    def filenames(self):
        return self._filenames
    
    @property
    def compiled_graph(self):
        return self._compiledGraph