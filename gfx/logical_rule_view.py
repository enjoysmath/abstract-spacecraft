from ui.ui_logical_rule_view import Ui_LogicalRuleView
from PyQt5.QtWidgets import QWidget, QApplication
from gfx.logical_rule_listing import LogicalRuleListing
from gfx.language_gfx_view import LanguageGfxView
from gfx.diagram_listing import DiagramListing
from PyQt5.QtWidgets import QMenu
from collections import OrderedDict
from gfx.external_link_listing import ExternalLinkListing

class LogicalRuleView(QWidget, Ui_LogicalRuleView):
   Idle, AddingGiven, AddingResult = range(3)
   
   def __init__(self, parent=None):
      super().__init__(parent)
      super().__init__()
      self.setupUi(self)
      self._tabName = None
      self.addGivenButton.clicked.connect(lambda b: self.add_given())
      self.addResultButton.clicked.connect(lambda b: self.add_result())
      self._state = self.Idle
      self._givens = OrderedDict()
      self._results = OrderedDict()
      self._proof = None
      
   def __setstate__(self, data):
      self.__init__()
      self._tabName = data['tab name']
      for given in data['givens']:
         self.add_given(given)
      for result in data['results']:
         self.add_result(result)
      self._proof = data['proof']
      
   def __getstate__(self):
      return {
         'tab name' : self.tab_name,
         'givens' : list(self._givens.values()),
         'results' : list(self._results.values()),
         'proof' : self._proof,
      }
   
   @property
   def tab_name(self):
      return self._tabName
   
   def set_tab_name(self, name):
      self._tabName = name
      
   def add_given(self, given=None):
      if given is None:
         self._state = self.AddingGiven
         QApplication.instance().set_link_requester(self)
      else:
         if (isinstance(given, tuple) and given[0] in self._givens) or id(given) in self._givens:
            QApplication.instance().broadcast_status_message("Duplicate given already in the list.", 5000)
            return
         readonly_view = self._getListingWidget(given)
         layout = self.givensList.layout()
         layout.removeWidget(self.addGivenButton)
         layout.addWidget(readonly_view, layout.count(), 0, 1, 1)
         layout.addWidget(self.addGivenButton, layout.count(), 0, 1, 1)       
         
         if isinstance(given, tuple):
            self._givens[given[0]] = given
         else:
            self._givens[id(given)] = given 
         
         readonly_view.set_language_purpose(readonly_view.Given)
         self._state = self.Idle
         
   def add_result(self, result=None):
      if result is None:
         self._state = self.AddingResult
         QApplication.instance().set_link_requester(self)
      else:
         if (isinstance(result, tuple) and result[0] in self._results) or id(result) in self._results:
            QApplication.instance().broadcast_status_message("Duplicate result already in the list.", 5000)
            return
         readonly_view = self._getListingWidget(result)
         layout = self.resultsList.layout()
         layout.removeWidget(self.addResultButton)
         layout.addWidget(readonly_view, layout.count(), 0, 1, 1)
         layout.addWidget(self.addResultButton, layout.count(), 0, 1, 1)
         
         if isinstance(result, tuple):
            self._results[result[0]] = result
         else:
            self._results[id(result)] = result
            
         readonly_view.set_language_purpose(readonly_view.Result)
         self._state = self.Idle
         
   def remove_listing(self, listing):
      view = listing.source_view
      
      if listing.language_purpose == listing.Given:
         if isinstance(view, tuple):
            del self._givens[view[0]]
         else:
            del self._givens[id(view)]
         self.givensList.layout().removeWidget(listing)
      
      elif listing.language_purpose == listing.Result and id(view) in self._results:
         if isinstance(view, tuple):
            del self._results[view[0]]
         else:
            del self._results[id(view)]
         self.resultsList.layout().removeWidget(listing)   
      
      listing.setParent(None)
      listing.deleteLater()      
      
   def _getListingWidget(self, link):
      readonly_view = None
      
      if isinstance(link, LogicalRuleView):
         readonly_view = LogicalRuleListing(link)
         
      elif isinstance(link, LanguageGfxView):
         readonly_view = DiagramListing(link)  
         
      elif isinstance(link, tuple):
         readonly_view = ExternalLinkListing(*link)
      
      readonly_view.remove_requested.connect(lambda: self.remove_listing(readonly_view))
      return readonly_view
   
   def set_link(self, link):
      if self._state == self.AddingGiven:
         self.add_given(given=link)
      elif self._state == self.AddingResult:
         self.add_result(result=link)
         
   def contextMenuEvent(self, event):
      menu = QMenu()
      if self._proof is None:
         menu.addAction("Create Proof").triggered.connect(self.create_new_proof)
      else:
         menu.addAction("Goto Proof").triggered.connect(self.navigate_to_proof)
      menu.exec_(event.screenPos())
         
   def create_new_proof(self):
      self._proof = self.window().add_new_proof_view(statement=self, title=f"Proof. {self.tab_name}")
      
   def navigate_to_proof(self):
      if self._proof is not None:
         window = self._proof.window()
         window.set_current_language_view(self._proof)
         
   @property
   def language_canvases(self):
      canvases = []
      for given in self._givens.values():
         canvases += given.language_canvases
      for result in self._results.values():
         canvases += result.languager_canvases
      return canvases
      
   
   
   