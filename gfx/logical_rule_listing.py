from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout
from ui.ui_logical_rule_listing import Ui_LogicalRuleListing

class LogicalRuleListing(QWidget, Ui_LogicalRuleListing):
   def __init__(self, rule_view, parent=None):
      super().__init__(parent)
      super().__init__()
      self.setupUi(self)
      self._ruleView = rule_view
   
   
   
   