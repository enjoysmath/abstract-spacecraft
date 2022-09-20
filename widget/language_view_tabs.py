from widget.tab_widget import TabWidget
from dialog.diagram_name_dialog import DiagramNameDialog
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QMenu, QApplication
from gfx.language_gfx_view import LanguageGfxView
from gfx.logical_rule_view import LogicalRuleView

class LanguageViewTabs(TabWidget):
    def __init__(self):
        super().__init__()
        
    def show_tab_rename_dialog(self, tab_index:int):
        dialog = DiagramNameDialog()
        dialog.nameLineEdit.setText(self.tabText(tab_index))
        result = dialog.exec_()
        
        if result == dialog.Accepted:
            name = dialog.nameLineEdit.text()
            self.setTabText(tab_index, name)   
            self.language_view_widget(tab_index).set_tab_name(name)
            
    def show_tab_context_menu(self, screen_pos:QPoint):
        menu = QMenu()
        tab_index = self.tab_index_under_screen_pos(screen_pos)
        menu.addAction("Rename").triggered.connect(
            lambda b: self.show_tab_rename_dialog(tab_index))
        app = QApplication.instance()
        link_requester = app.link_requester     
        if link_requester:
            menu.addAction("Set link target").triggered.connect(lambda: self.set_link_target(view=self.language_view_widget(tab_index)))
        menu.exec_(screen_pos)            
        
    def language_view_widget(self, tab_index:int) -> LanguageGfxView:
        for child in self.widget(tab_index).children():
            if isinstance(child, (LanguageGfxView, LogicalRuleView)):
                return child
            
    def set_link_target(self, view):
        app = QApplication.instance()
        link_requester = app.link_requester    
        if link_requester is not None:
            link_requester.set_link(view)            
            window = link_requester.window()
            window.set_current_language_view(link_requester)
            app.broadcast_status_message("Link was set", 3000)
            app.set_link_requester(None)
        