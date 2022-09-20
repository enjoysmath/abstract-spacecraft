from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
import _pickle as pickle
from core.networkx_tools import networkx_graph
import networkx as nx
from gfx.language_gfx_view import LanguageGfxView
from gfx.logical_rule_view import LogicalRuleView

class LibrarySearchThread(QThread):
   def __init__(self, compiled_graph:nx.Graph):
      super().__init__()
      self._compiledGraph = compiled_graph

   def run(self):
      pass