from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
import _pickle as pickle
from core.networkx_tools import *
import networkx as nx
from networkx.algorithms import isomorphism
from gfx.language_gfx_view import LanguageGfxView
from gfx.logical_rule_view import LogicalRuleView

class LibrarySearchThread(QThread):
   isomorphic_subgraph_match_found = pyqtSignal(dict)
   
   def __init__(self, query_items, compiled_graph:nx.MultiDiGraph):
      super().__init__()
      self._compiledGraph = compiled_graph
      self._queryGraph = nx.MultiDiGraph()
      build_networkx_graph(self._queryGraph, query_items, labels_fun=networkx_query_labels)
      
      # Debug helper code
      #import matplotlib.pyplot as plt    
      #G1 = self._compiledGraph
      #G2 = self._queryGraph
      
      #pos = nx.spring_layout(G2, scale=1)    
      #node_labels = nx.get_node_attributes(G2, 'labels')
      #nx.draw_networkx(G2, pos=pos, with_labels=True, labels=node_labels)
      ##nx.draw(G2, with_labels=True)
      #plt.show()      

   def run(self):
      subgraph_matcher = nx.isomorphism.MultiDiGraphMatcher(G1=self.library_graph, G2=self.query_graph, node_match=regex_node_match)
      
      for subgraph_match in subgraph_matcher.subgraph_isomorphisms_iter():
         for lib_node_id in subgraph_match:
            component_graph = networkx_component_induced_by_node(self.library_graph, lib_node_id)
            if nx.faster_could_be_isomorphic(G1=component_graph, G2=self.query_graph):
               if nx.is_isomorphic(G1=component_graph, G2=self.query_graph, node_match=regex_node_match):
                  self.isomorphic_subgraph_match_found.emit(subgraph_match)
            break
      
      
   @property
   def library_graph(self):
      return self._compiledGraph
   
   @property
   def query_graph(self):
      return self._queryGraph