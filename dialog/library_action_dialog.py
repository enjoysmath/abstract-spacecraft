from ui_library_action_dialog import Ui_LibraryActionDialog
from PyQt5.QtWidgets import QDialog
from mainwindow import MainWindow
from linkable import Linkable

class LibraryActionDialog(QDialog, Ui_LibraryActionDialog):
   link_created = pyqtSignal(str)
   
   def __init__(self, item:Linkable, parent=None):
      super().__init__(parent)
      super().__init__()
      self.setupUi(self)
      self._item = item
      self.newDiagramButton.clicked.connect(self.new_diagram_button_clicked)
      
   def new_diagram_button_clicked(self):
      parent = self.parentWidget()
      assert isinstance(parent, MainWindow)
      view = parent.add_new_diagram_view()
      
      
      