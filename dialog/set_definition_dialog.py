from PyQt5.QtWidgets import QDialog
from ui.ui_set_definition_dialog import Ui_SetDefinitionDialog
from PyQt5.QtCore import Qt

class SetDefinitionDialog(QDialog, Ui_SetDefinitionDialog):  
    def __init__(self):
        QDialog.__init__(self)
        Ui_SetDefinitionDialog.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
