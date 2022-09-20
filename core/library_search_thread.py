from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
import _pickle as pickle
from core.networkx_tools import networkx_graph, networkx_query_labels
import networkx as nx
from networkx.algorithms import isomorphism
from gfx.language_gfx_view import LanguageGfxView
from gfx.logical_rule_view import LogicalRuleView

class LibrarySearchThread(QThread):
   def __init__(self, query_items, compiled_graph:nx.MultiDiGraph):
      super().__init__()
      self._compiledGraph = compiled_graph
      self._queryGraph = networkx_graph(query_items, labels_fun=networkx_query_labels)

   def run(self):
      pass