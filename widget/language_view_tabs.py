from widget.tab_widget import TabWidget
from dialog.diagram_name_dialog import DiagramNameDialog
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QMenu
from gfx.language_gfx_view import LanguageGfxView

class LanguageViewTabs(TabWidget):
    def __init__(self):
        super().__init__()
        
    def show_tab_rename_dialog(self, tab_index:int):
        dialog = DiagramNameDialog()
        dialog.nameLineEdit.setText(self.tabText(tab_index))
        result = dialog.exec_()
        
        if result == dialog.Accepted:
            self.setTabText(tab_index, dialog.nameLineEdit.text())        
            
    def show_tab_context_menu(self, screen_pos:QPoint):
        menu = QMenu()
        menu.addAction("Rename").triggered.connect(
            lambda b: self.show_tab_rename_dialog(self.tab_index_under_screen_pos(screen_pos)))
        menu.exec_(screen_pos)            
        
    def language_view_widget(self, tab_index:int) -> LanguageGfxView:
        for child in self.widget(tab_index).children():
            if isinstance(child, LanguageGfxView):
                return child