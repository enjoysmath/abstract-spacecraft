from ui.ui_logical_rule_listing import Ui_LogicalRuleListing
from gfx.language_listing import LanguageListing

class LogicalRuleListing(LanguageListing, Ui_LogicalRuleListing):
   def __init__(self, rule_view, parent=None):
      super().__init__(parent)
      super().__init__()
      self.setupUi(self)
      self._ruleView = rule_view
      self.ruleTitleLabel.setText(rule_view.tab_name)
      rule_view.tab_name_changed.connect(self.ruleTitleLabel.setText)
      self.removeButton.clicked.connect(self.remove_requested.emit)
      self.editButton.clicked.connect(self.navigate_to_logical_rule)
      
   def __setstate__(self, data):
      self.__init__(data['rule view'])
      
   def __getstate__(self):
      return {
         'rule view': self._ruleView,
      }
      
   def navigate_to_logical_rule(self):
      if self._ruleView:
         self._ruleView.window().raise_()
         self._ruleView.window().set_current_language_view(self._ruleView)      
      
   
   
   
   