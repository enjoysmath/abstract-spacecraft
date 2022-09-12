from PyQt5.QtWidgets import QDialog
from ui.ui_combo_box_dialog import Ui_ComboBoxDialog

class ComboBoxDialog(QDialog, Ui_ComboBoxDialog):
    def __init__(self):
        QDialog.__init__(self)
        Ui_ComboBoxDialog.__init__(self)
        self.setupUi(self)

    def exec_(self):
        previous = self.comboBox.currentText()
        result = super().exec_()
        
        if result == self.Rejected:
            self.comboBox.setCurrentText(previous)
            
        return result