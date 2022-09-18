from PyQt5.QtWidgets import QDialog, QApplication
from ui.ui_set_definition_dialog import Ui_SetDefinitionDialog
from PyQt5.QtCore import Qt
from gfx.linkable import Linkable

class SetDefinitionDialog(QDialog, Ui_SetDefinitionDialog):  
    def __init__(self):
        QDialog.__init__(self)
        Ui_SetDefinitionDialog.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.accepted.connect(self.set_link)
        self._linkable = None
        
    def show(self, linkable:Linkable):
        self._linkable = linkable
        super().show() 
        
    def set_link(self):
        if self._linkable is not None:            
            if self.internalLinkRadio.isChecked():
                app = QApplication.instance()
                link = app.topmost_main_window().current_language_view() 
            else:
                link = self.externalUrlLine.text()                
            self._linkable.set_link(link)