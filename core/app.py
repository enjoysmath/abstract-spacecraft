from PyQt5.QtWidgets import QApplication, QDialog
from dialog.mainwindow import MainWindow
from to_delete.definable import Definable
from PyQt5.QtCore import Qt
from dialog.set_definition_dialog import SetDefinitionDialog
from dialog.font_dialog import FontDialog
from graphics.text import Text

class App(QApplication):    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._windows = []
        self._setDefDialog = SetDefinitionDialog()
        self._appFontDialog = FontDialog()
        self._appFontDialog.font_changed.connect(self.setFont)
        self._appFontDialog.setWindowTitle('Set app font')
        
    def show_app_font_dialog(self):
        self._appFontDialog.exec_()
        
    def show_set_definition_dialog(self, definable:Definable):
        self._setDefDialog.accepted.connect(
            lambda: definable.set_definition(self.topmost_main_window().current_language_view))
        self._setDefDialog.show()
        
    def topmost_main_window(self):
        topLevel = self.topLevelWidgets()
        for widget in topLevel:
            if isinstance(widget, MainWindow):
                return widget
        
    def add_new_window(self):
        window = MainWindow()
        self._windows.append(window)
        window.show()
        return window
        
    def setFont(self, font):
        super().setFont(font)
        for window in self._windows:
            for langView in window.language_views():
                for item in langView.scene().items():
                    if isinstance(item, Text):
                        item.setFont(font)
        self._appFontDialog.set_font(font)