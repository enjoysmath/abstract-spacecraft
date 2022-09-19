from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog, \
                             QGridLayout, QWidget, QActionGroup)
from ui.ui_mainwindow import Ui_MainWindow
from widget.language_view_tabs import LanguageViewTabs
from gfx.language_gfx_view import LanguageGfxView, LanguageCanvas
from gfx.text import Text
from PyQt5.QtCore import Qt, QRectF, QTimer
#from widget.edit_text_dockwidget import EditTextDockWidget
from widget.library_search_dockwidget import LibrarySearchDockWidget
import _pickle as pickle
from widget.debug_widget import DebugWidget
from gfx.object import Object
from gfx.arrow import Arrow
from gfx.text import Text
from gfx.logical_rule_view import LogicalRuleView
from gfx.proof_view import ProofView

class MainWindow(QMainWindow, Ui_MainWindow):
    new_tab_base_name = '🌌'
    set_query_wait_millisecs = 750
    _lastActiveWindow = None
    
    DefinitionMode, TextMode, ArrowMode, MoveMode, NumEditModes = range(5)
    
    def __init__(self):
        QMainWindow.__init__(self)
        self._baseTitle = self.windowTitle()        
        Ui_MainWindow.__init__(self)        
        self.setupUi(self)
        self.language_tabs = LanguageViewTabs()
        self.setCentralWidget(self.language_tabs)
        self.actionUndo.triggered.connect(lambda b: self.undo_language_in_view())
        self.actionRedo.triggered.connect(lambda b: self.redo_language_in_view())
        self.actionDelete.triggered.connect(lambda b: self.delete_in_language_view())
        self.actionZoom_Default.triggered.connect(lambda b: self.zoom_default_view())
        self.actionZoom_In.triggered.connect(lambda b: self.zoom_in_view())
        self.actionZoom_Out.triggered.connect(lambda b: self.zoom_out_view())
        self.actionNewWindow.triggered.connect(lambda b: QApplication.instance().add_new_window())
        self.actionNewDiagram.triggered.connect(lambda b: self.add_new_diagram_view())
        self.actionNewLogicalRule.triggered.connect(lambda b: self.add_new_logical_rule_view())
        #self.actionCloseWindow.triggered.connect(lambda b: self.remove_language_view())
        self.actionCloseEntireApp.triggered.connect(lambda b: QApplication.instance().quit())
        self.actionCloseWindow.triggered.connect(lambda b: self.close())
        self.actionDeleteTab.triggered.connect(lambda b: self.remove_language_view(self.current_language_view()))
        self.actionBack.triggered.connect(lambda b: self.navigate_back())
        self.actionForward.triggered.connect(lambda b: self.navigate_forward())
        self.language_tabs.currentChanged.connect(self.language_view_tab_changed)
        #self.edit_text_dock = EditTextDockWidget()
        self.library_search_dock = LibrarySearchDockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, self.library_search_dock)
        #self.addDockWidget(Qt.RightDockWidgetArea, self.edit_text_dock)
        #self.tabifyDockWidget(self.library_search_dock, self.edit_text_dock)
        self.actionSave.triggered.connect(lambda b: QApplication.instance().save_app_data())
        self.actionSaveAs.triggered.connect(lambda b: QApplication.instance().save_app_data_as())
        self.actionOpen.triggered.connect(lambda b: QApplication.instance().load_app_data())
        self.actionApplication_font.triggered.connect(lambda b: QApplication.instance().show_app_font_dialog())
        self.actionGraphics_Debugger.toggled.connect(self.toggle_view_graphics_debugger)
        self.actionBack.setEnabled(False)
        self.actionForward.setEnabled(False)        
        self._navigationList = []
        self._navigationPos = None
        self._newTabCount = 0
        self.graphics_debugger = DebugWidget()
        self.graphics_debugger.hide()
        self._setQueryTimer = QTimer()
        self._setQueryTimer.setInterval(self.set_query_wait_millisecs)
        self._setQueryTimer.setSingleShot(True)        
        self._setQueryTimer.timeout.connect(self._setSelectedItemsAsQuery)
        self._setQueryView = None
        self._cassetteButtonGroup = QActionGroup(self)
        self._cassetteButtonGroup.addAction(self.actionMoveStuffMode)
        self._cassetteButtonGroup.addAction(self.actionPlace_Arrow)
        self._cassetteButtonGroup.addAction(self.actionEdit_Text)
        self._cassetteButtonGroup.addAction(self.actionBook_Lookup)
        self._cassetteButtonGroup.setExclusive(True)
        self._cassetteButtonGroup.triggered.connect(self.edit_mode_button_triggered)
        self._editMode = self.ArrowMode
        self.setMouseTracking(True)
        MainWindow._lastActiveWindow = self

    _windowStatesEnum = {
        0x00000000 : Qt.WindowNoState,          #		The window has no state set (in normal state).
        0x00000001 : Qt.WindowMinimized,        #		The window is minimized (i.e. iconified).
        0x00000002 : Qt.WindowMaximized,	      #      The window is maximized with a frame around it.
        0x00000004 : Qt.WindowFullScreen,	      #      The window fills the entire screen without any frame around it.
        0x00000008 : Qt.WindowActive,		      # The window is the active window, i.e. it has keyboard focus.        
    }
        
    def __setstate__(self, data):
        self.__init__()
        for widget in data['tab widgets']:
            self.add_language_view(widget)
        self.setGeometry(data['geometry'])
        self.setWindowState(self._windowStatesEnum[data['window state']])
        
    def __getstate__(self):
        return {
            'tab widgets' : list(self.language_views()),
            'geometry' : self.geometry(),
            'window state' : int(self.windowState()),
        }    
    
    def edit_mode_button_triggered(self):
        if self.actionBook_Lookup.isChecked():
            self._editMode = self.DefinitionMode
        elif self.actionEdit_Text.isChecked():
            self._editMode = self.TextMode
        elif self.actionPlace_Arrow.isChecked():
            self._editMode = self.ArrowMode
        elif self.actionMoveStuffMode.isChecked():
            self._editMode = self.MoveMode
            
    @property
    def language_edit_mode(self):
        return self._editMode
        
    def set_saved_title(self, saved:bool=True):
        add = ' *' if not saved else ''
        super().setWindowTitle(self._baseTitle + add)
        
    def setWindowTitle(self, title:str):
        if self._baseTitle != title:
            self._baseTitle = title
            self.set_saved_title(saved=QApplication.instance().is_saved())
                        
    def add_language_view(self, view:LanguageGfxView):     
        if self._navigationPos is None:
            self._navigationPos = 0
        else:
            self._navigationPos += 1
            self._navigationList = self._navigationList[:self._navigationPos]
        self._navigationList.append(view)
        widget = QWidget()
        widget.setLayout(QGridLayout())
        widget.layout().addWidget(view)
        widget.view_widget = view
        self.language_tabs.addTab(widget, view.tab_name)
        if self.language_tabs.count() > 1:
            self.language_tabs.setCurrentWidget(widget)
        return view
    
    def set_selected_items_as_query(self, view):
        self._setQueryView = view
        self._setQueryTimer.start()
        
    def _setSelectedItemsAsQuery(self):
        scene = self._setQueryView.scene()
        selected_items = scene.selectedItems()
        selected_items = filter(lambda x: isinstance(x, (Object, Arrow)), selected_items)
        self.library_search_dock.set_items_as_query(selected_items, self._setQueryView)
        
    def remove_language_view(self, view:LanguageGfxView=None):
        if view is None:
            view = self.current_language_view()
        if view:
            index = self._navigationList.index(view)
            self._navigationList.pop(index)
                        
            if index > 0:
                index -= 1
            elif self.language_tabs.count():
                index += 1
            else:
                index = None            
            self._navigationPos = index
            self.language_tabs.removeTab(self.language_tabs.indexOf(view.parentWidget()))
            try:
                view.scene().selectionChanged.disconnect()
            except:
                pass
        
    def current_language_view(self):
        tab_widget = self.current_tab_widget
        
        if tab_widget:
            return tab_widget.view_widget

    def language_views(self):
        for k in range(self.language_tabs.count()):
            yield self.language_tabs.widget(k).view_widget            
    
    @property
    def current_tab_widget(self):
        return self.language_tabs.currentWidget()
    
    def set_current_language_view(self, view:LanguageGfxView):
        self.language_tabs.setCurrentWidget(view.parent())
    
    def undo_language_in_view(self):
        view = self.current_language_view()
        if view:
            view.scene().undo_command()
            
    def redo_language_in_view(self):
        view = self.current_language_view()
        if view:
            view.scene().redo_command()
            
    def delete_in_language_view(self):
        view = self.current_language_view()
        if view:
            view.scene().delete_selected()            
            
    def zoom_default_view(self):
        view = self.current_language_view()
        if view:
            view.zoom_100()
            
    def zoom_in_view(self):
        view = self.current_language_view()
        if view:
            view.zoom_in()
            
    def zoom_out_view(self):
        view = self.current_language_view()
        if view:
            view.zoom_out()
            
    def add_new_diagram_view(self):
        canvas = LanguageCanvas()
        canvas.user_text_edited.connect(self.process_user_edited_text_item)
        view = LanguageGfxView(canvas)           
        tabName = self.new_tab_base_name + str(self._newTabCount)
        view.set_tab_name(tabName)
        self.add_language_view(view)
        #self.language_tabs.show_tab_rename_dialog(self.language_tabs.count() - 1)
        self._newTabCount += 1
        canvas.selectionChanged.connect(lambda: self.set_selected_items_as_query(view))
        return view
    
    def add_new_proof_view(self, statement:LogicalRuleView, title:str=None):
        proof_view = ProofView(statement)
        if tab_name is None:
            tab_name = self.new_tab_base_name + str(self._newTabCount)
            self._newTabCount += 1
        proof_view.set_tab_name(tab_name)
        self.add_language_view(proof_view)
        return proof_view
    
    def add_new_logical_rule_view(self):
        rule_view = LogicalRuleView()
        tabName = self.new_tab_base_name + str(self._newTabCount)
        rule_view.set_tab_name(tabName)
        self.add_language_view(rule_view)
        self._newTabCount += 1 
        return rule_view
        
    def navigate_back(self):
        if self._navigationPos is not None and self._navigationPos > 0:
            self._navigationPos -= 1
            self.language_tabs.setCurrentWidget(self._navigationList[self._navigationPos])
        self.toggle_enable_navigate_buttons()
                      
    def navigate_forward(self):
        if self._navigationPos is not None and self._navigationPos < len(self._navigationList) - 1:
            self._navigationPos += 1
            self.language_tabs.setCurrentWidget(self._navigationList[self._navigationPos])
        self.toggle_enable_navigate_buttons()
        
    def toggle_enable_navigate_buttons(self):
        if self._navigationPos is not None:
            self.actionBack.setEnabled(self._navigationPos > 0)
            self.actionForward.setEnabled(self._navigationPos < len(self._navigationList) - 1)        
            
    def language_view_tab_changed(self, index:int):
        self.toggle_enable_navigate_buttons()
        self.toggle_view_graphics_debugger(self.actionGraphics_Debugger.isChecked())
        
    def navigate_to_language_view(self, view:LanguageGfxView):
        self._navigationPos += 1
        self._navigationList = self._navigationList[:self._navigationPos]
        self._navigationList.append(view)
        self.language_tabs.setCurrentWidget(view.parentWidget())
                
    @property
    def place_arrow_mode(self):
        return self.actionPlace_Arrow.isChecked()
    
    @property
    def edit_text_mode(self):
        return self.actionEdit_Text.isChecked()
            
    def toggle_view_graphics_debugger(self, enable:bool):
        currentTab = self.language_tabs.currentWidget()
        if enable:
            if self.graphics_debugger.parent() is not currentTab:
                currentTab.layout().addWidget(self.graphics_debugger)
                self.graphics_debugger.set_view(currentTab.view_widget)
            self.graphics_debugger.show()
        else:
            self.graphics_debugger.hide()
            
    @property
    def collision_response_enabled(self):
        return self.actionCollision_response.isChecked()
    
    def set_collision_response_enabled(self, enable:bool=True):
        self.actionCollision_response.setChecked(enable)
    
    def restore_collision_response_setting(self):
        self.set_collision_response_enabled(self._collisionResponseStash)
        
    def stash_and_disable_collision_response(self):
        self._collisionResponseStash = self.actionCollision_response.isChecked()
        self.actionCollision_response.setChecked(False)
        
    @property
    def text_collision_response_enabled(self):
        return self.actionText_Collision_response.isChecked()
    
    def process_user_edited_text_item(self, text:Text):
        print(text.toPlainText())
        
    def closeEvent(self, event):
        app = QApplication.instance()
        app.remove_window(self)
        super().closeEvent(event)
        
    def mousePressEvent(self, event):
        MainWindow._lastActiveWindow = self
        super().mousePressEvent(event)
        
    @property
    def last_active_window(self):
        return MainWindow._lastActiveWindow
    
    