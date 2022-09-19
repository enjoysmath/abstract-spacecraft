from ui.ui_logical_rule_view import Ui_LogicalRuleView
from PyQt5.QtWidgets import QWidget, QApplication
from gfx.logical_rule_listing import LogicalRuleListing
from gfx.language_gfx_view import LanguageGfxView
from gfx.diagram_listing import DiagramListing

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
      
   def __setstate__(self, data):
      self.__init__()
      self._tabName = data['tab name']
      
   def __getstate__(self):
      return {
         'tab name' : self.tab_name,
      }
   
   @property
   def tab_name(self):
      return self._tabName
   
   def set_tab_name(self, name):
      self._tabName = name
      
   def add_given(self, given=None):
      if given is None:
         self._state = self.AddingGiven
         QApplication.instance().show_set_definition_dialog(self)
   
   def set_link(self, link):
      readonly_view = None
      
      if self._state == self.AddingGiven:
         if isinstance(link, LogicalRuleView):
            readonly_view = LogicalRuleListing(link)
            
         elif isinstance(link, LanguageGfxView):
            readonly_view = DiagramListing(link)
            
         self.givensList.layout().insertWidget(0, readonly_view)
         self._state = self.Idle
         
   def add_result(self, result=None):
      pass
   
   
   