from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMenu

class Linkable(QObject):
   open_link_requested = pyqtSignal(str)
   edit_link_requested = pyqtSignal(QObject)

   def __init__(self, parent=None):
      super().__init__(parent)
      self._fullpathLink = None

   def _setState(self, data:dict):
      self._fullpathLink = data['fullpath link']

   def _getState(self, data:dict):
      data['fullpath link'] = self._fullpathLink
      return data

   @property
   def full_path_to_link(self):
      return self._fullpathLink
   
   def open_link(self):
      if self._fullpathLink is not None:
         self.open_link_requested.emit(self._fullpathLink)

   def build_context_menu(self, menu:QMenu):
      menu.addAction('Edit Link').triggered.connect(self.edit_link_requested.emit(self))



