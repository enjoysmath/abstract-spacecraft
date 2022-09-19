from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal

class LanguageListing(QWidget):
   Given, Result, NumPurposes = range(3)
   remove_requested = pyqtSignal()
   
   def __init__(self, parent=None):
      super().__init__(parent)
      self._purpose = None
      
   def set_language_purpose(self, purpose:int):
      self._purpose = purpose
      
   @property
   def language_purpose(self):
      return self._purpose
   
   