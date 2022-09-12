from PyQt5.QtWidgets import QWidget, QGridLayout
from widget.tab_widget import TabWidget

class ProofWidget(QWidget):
   def __init__(self, parent=None):
      super().__init__(parent)
      self._proofTabs = TabWidget()
      self.setLayout(QGridLayout())
      self.layout().addWidget(self._proofTabs)