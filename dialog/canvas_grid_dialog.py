from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QPointF, pyqtSignal, Qt
from ui.ui_canvas_grid_dialog import Ui_CanvasGridDialog

class CanvasGridDialog(QDialog, Ui_CanvasGridDialog):
    redraw_canvas_background = pyqtSignal()
    
    def __init__(self):
        QDialog.__init__(self)
        Ui_CanvasGridDialog.__init__(self)
        self.setupUi(self)
        self._previous = (self.xSpacingSpin.value(), self.ySpacingSpin.value(), 
                          self.enabledCheck.isChecked(), self.visibleCheck.isChecked(),
                          self.xyLockedCheck.isChecked()) 
        self.xSpacingSpin.valueChanged.connect(self.on_xspacing_changed)
        self.ySpacingSpin.valueChanged.connect(self.on_yspacing_changed)    
        self.enabledCheck.toggled.connect(lambda b: self.redraw_canvas_background.emit())
        self.visibleCheck.toggled.connect(lambda b: self.redraw_canvas_background.emit())
        
    def _setState(self, data:dict):
        self.__init__()
        self.xSpacingSpin.setValue(data['x spacing'])
        self.ySpacingSpin.setValue(data['y spacing'])
        self.enabledCheck.setChecked(data['enabled'])
        self.visibleCheck.setChecked(data['visible'])
        self.xyLockedCheck.setChecked(data['xy locked'])
        
    def _getState(self, data:dict):
        data['x spacing'] = self.xSpacingSpin.value()
        data['y spacing'] = self.ySpacingSpin.value()
        data['enabled'] = self.enabledCheck.isChecked()
        data['visible'] = self.visibleCheck.isChecked()
        data['xy locked'] = self.xyLockedCheck.isChecked()
        return data
        
    def reset_to_previous(self):
        self.xSpacingSpin.setValue(self._previous[0])
        self.ySpacingSpin.setValue(self._previous[1])
        self.enabledCheck.setChecked(self._previous[2])
        self.visibleCheck.setChecked(self._previous[3])
        self.xyLockedCheck.setChecked(self._previous[4])
        
    def on_xspacing_changed(self, xspacing):
        if self.xyLockedCheck.isChecked() and self.ySpacingSpin.value() != xspacing:
            self.ySpacingSpin.setValue(xspacing)
        self.redraw_canvas_background.emit()
            
    def on_yspacing_changed(self, yspacing):
        if self.xyLockedCheck.isChecked() and self.xSpacingSpin.value() != yspacing:
            self.xSpacingSpin.setValue(yspacing)
        self.redraw_canvas_background.emit()
            
    def exec_(self):
        self._previous = (
            self.xSpacingSpin.value(),
            self.ySpacingSpin.value(),
            self.enabledCheck.isChecked(),
            self.visibleCheck.isChecked(),
            self.xyLockedCheck.isChecked())
        return super().exec_()