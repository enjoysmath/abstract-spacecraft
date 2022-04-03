from core.qt_tools import SimpleBrush
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QMenu
from core.qt_tools import set_brush_color
from dialog.color_dialog import ColorDialog

class ColorFillable:
    def __init__(self):
        self._brush = SimpleBrush(Qt.red)
        self._fillColorDialog = ColorDialog(f'Set {self.__class__.__name__.lower()} fill color')
        self._fillColorDialog.setCurrentColor(Qt.red)
        self._fillColorDialog.currentColorChanged.connect(self.set_brush_color)
        
    def _setState(self, data:dict):
        self._brush = data['brush']
        self.update()

    def _getState(self, data:dict):
        data['brush'] = self._brush
        return data
        
    @property
    def brush(self):
        return self._brush
    
    def setBrush(self, brush):
        if self._brush != brush:
            self._brush = brush
            if brush.color() != self._fillColorDialog.currentColor():
                self._fillColorDialog.setCurrentColor(brush.color())
            self.update()            
          
    @property
    def brush_color(self):
        return self._brush.color()
    
    def set_brush_color(self, color):
        if self._brush.color() != color:
            self._brush = set_brush_color(self._brush, color)
            self._fillColorDialog.setCurrentColor(color)
            self.update()
    
    def show_fill_color_change_dialog(self):
        self._fillColorDialog.exec_()
    
    def build_context_menu(self, menu:QMenu):
        menu.addAction('Fill color').triggered.connect(self.show_fill_color_change_dialog)