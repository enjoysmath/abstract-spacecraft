from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog, \
                             QGridLayout, QWidget)
from ui_mainwindow import Ui_MainWindow
from language_view_tabs import LanguageViewTabs
from language_view import LanguageView, LanguageCanvas
from text import Text
from PyQt5.QtCore import Qt, QRectF, QTimer
from edit_text_dockwidget import EditTextDockWidget
from library_search_dockwidget import LibrarySearchDockWidget
import _pickle as pickle
from debug_widget import DebugWidget
from object import Object
from arrow import Arrow
from text import Text

class MainWindow(QMainWindow, Ui_MainWindow):
    new_tab_base_name = '🌌'
    set_query_wait_millisecs = 750
    
    def __init__(self):
        QMainWindow.__init__(self)
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
        self.actionNew_Window.triggered.connect(lambda b: QApplication.instance().add_new_window())
        self.actionNew_Tab.triggered.connect(lambda b: self.add_new_language_view())
        self.actionClose_Diagram.triggered.connect(lambda b: self.remove_language_view())
        self.actionBack.triggered.connect(lambda b: self.navigate_back())
        self.actionForward.triggered.connect(lambda b: self.navigate_forward())
        self.language_tabs.currentChanged.connect(self.language_view_tab_changed)
        self.edit_text_dock = EditTextDockWidget()
        self.library_search_dock = LibrarySearchDockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, self.library_search_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.edit_text_dock)
        self.tabifyDockWidget(self.library_search_dock, self.edit_text_dock)
        self.actionSave_Diagram.triggered.connect(lambda b: self.save_language_view())
        self.actionSave_diagram_as.triggered.connect(lambda b: self.save_language_view_as())
        self.actionLoad_diagram.triggered.connect(lambda b: self.load_language_view())
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
                        
    def add_language_view(self, view:LanguageView):     
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
        self.language_tabs.addTab(widget,view.tab_name)
        if self.language_tabs.count() > 1:
            self.language_tabs.setCurrentWidget(view)
        view.scene().selectionChanged.connect(lambda: self.set_selected_items_as_query(view))
        return view
    
    def set_selected_items_as_query(self, view):
        self._setQueryView = view
        self._setQueryTimer.start()
        
    def _setSelectedItemsAsQuery(self):
        scene = self._setQueryView.scene()
        selected_items = scene.selectedItems()
        selected_items = filter(lambda x: isinstance(x, (Object, Arrow)), selected_items)
        self.library_search_dock.set_items_as_query(selected_items, self._setQueryView)
        
    def remove_language_view(self, view:LanguageView=None):
        if view is None:
            view = self.current_language_view
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
            self.language_tabs.removeTab(self.language_tabs.indexOf(view))
            view.scene().selectionChanged.disconnect()
        
    @property
    def current_language_view(self):
        return self.current_tab_widget.view_widget
    
    def language_views(self):
        for k in range(self.language_tabs.count()):
            yield self.language_tabs.widget(k).view_widget            
    
    @property
    def current_tab_widget(self):
        return self.language_tabs.currentWidget()
    
    def set_current_language_view(self, view:LanguageView):
        self.language_tabs.setCurrentWidget(view.parent())
    
    def undo_language_in_view(self):
        view = self.current_language_view
        if view:
            view.scene().undo_command()
            
    def redo_language_in_view(self):
        view = self.current_language_view
        if view:
            view.scene().redo_command()
            
    def delete_in_language_view(self):
        view = self.current_language_view
        if view:
            view.scene().delete_selected()            
            
    def zoom_default_view(self):
        view = self.current_language_view
        if view:
            view.zoom_100()
            
    def zoom_in_view(self):
        view = self.current_language_view
        if view:
            view.zoom_in()
            
    def zoom_out_view(self):
        view = self.current_language_view
        if view:
            view.zoom_out()
            
    def add_new_language_view(self):
        canvas = LanguageCanvas()
        view = LanguageView(canvas)           
        tabName = self.new_tab_base_name + str(self._newTabCount)
        view.set_tab_name(tabName)
        self.add_language_view(view)
        self._newTabCount += 1
        
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
        self.actionBack.setEnabled(self._navigationPos > 0)
        self.actionForward.setEnabled(self._navigationPos < len(self._navigationList) - 1)        
            
    def language_view_tab_changed(self, index:int):
        self.toggle_enable_navigate_buttons()
        self.toggle_view_graphics_debugger(self.actionGraphics_Debugger.isChecked())
        
    def navigate_to_language_view(self, view:LanguageView):
        self._navigationPos += 1
        self._navigationList = self._navigationList[:self._navigationPos]
        self._navigationList.append(view)
        self.language_tabs.setCurrentWidget(view)
                
    @property
    def place_arrow_mode(self):
        return self.actionPlace_Arrow.isChecked()
    
    @property
    def edit_text_mode(self):
        return self.actionEdit_Text.isChecked()
    
    def load_language_view(self, filename:str=None) -> LanguageCanvas:
        if filename is None:
            filenames,_ = QFileDialog.getOpenFileNames(self, 'Open Diagram(s)', './standard_library', 'Abstract Spacecraft (*.🌌)')
        for filename in filenames:            
            with open(filename, 'rb') as file:
                view = pickle.load(file)
            self.add_language_view(view)
            view.set_filename(filename)
            
    def save_language_view(self, view:LanguageView=None):
        if view is None:
            view = self.current_language_view
        if not view:
            return
        filename = view.filename
        if not filename:
            self.save_language_view_as(view)
            return                
        with open(filename, 'wb') as file:
            pickle.dump(view, file)
            
    def save_language_view_as(self, view:LanguageView=None):
        if view is None:
            view = self.current_language_view
        if not view:
            return
        filename,_ = QFileDialog.getSaveFileName(self, 'Save Diagram As', './standard_library', 'Abstract Spacecraft (*.🌌)')
        if filename:
            view.set_filename(filename)
            self.save_language_view(view)
            
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