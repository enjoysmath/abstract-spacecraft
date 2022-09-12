from PyQt5.QtWidgets import QWidget
from ui.ui_debug_widget import Ui_DebugWidget
from widget.debug_watch_widget import DebugWatchWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QCursor, QTransform

class DebugWidget(QWidget, Ui_DebugWidget):
    def __init__(self):
        super().__init__()
        super().__init__()
        self.setupUi(self)
        self._debugTimer = QTimer(self)
        self._debugTimer.setSingleShot(False)
        self._debugTimer.setInterval(self.refresh_rate_spin.value())
        self._watches = {}
        self.view = None
        self.setup()
        
    def set_view(self, view):
        if self.view is not None:
            self.view.scene().selectionChanged.disconnect(self.scene_selection_changed)
        self.view = view                       
        if view:
            self.scene().selectionChanged.connect(self.scene_selection_changed)  
            self._debugTimer.start()
        else:
            self._debugTimer.stop()
        
    def setup(self):
        self.add_parent_button.clicked.connect(lambda b: self.add_parent_watch_item())
        self.add_children_button.clicked.connect(lambda b: self.add_child_watch_items())
        self.add_watch_button.clicked.connect(lambda b: self.add_watch_item())
        self.item_watch_tabs.tabCloseRequested.connect(self.remove_watch_item)
             
        self.item_watch_tabs.currentChanged.connect(lambda i: self.update_debug_fields())
        self.pick_watch_button.clicked.connect(lambda b: self.pick_watch_item())
        self._debugTimer.timeout.connect(self.update_debug_fields)
        
    def pick_watch_item(self):
        scene = self.scene()
        scene.mouse_pressed.connect(self._watchItemPickedAt)
        #self._restoreMode = self.view.select_mode()
        #self.view.set_select_mode(True)
        
    def _watchItemPickedAt(self, pos):
        scene = self.scene()
        item = scene.itemAt(pos, QTransform())
        if item:
            self.add_watch_item(item)
        scene.mouse_pressed.disconnect(self._watchItemPickedAt)
        #self.view.set_select_mode(self._restoreMode)
        
    def set_show(self, en):
        if en:
            self.show()
        else:
            self.hide()
            
    def add_parent_watch_item(self, item=None):
        if item is None:
            item = self.current_watch_widget()
            if item:
                item = item.watched_item()
        if item:
            parent = item.parentItem()
            if parent:
                self.add_watch_item(parent)
    
    def add_child_watch_items(self, item=None):
        if item is None:
            item = self.current_watch_widget()
            if item:
                item = item.watched_item()
        if item:
            children = item.childItems()
            for child in children:
                self.add_watch_item(child)                
        
    def add_watch_item(self, item=None):
        if item is None:
            item = self.scene().selectedItems()
            if item: item = item[0]
        if item:
            tab_name = self.next_type_name(item)
            if isinstance(tab_name, int):
                tab_name = item.__class__.__name__ + (' ' + str(tab_name) if tab_name != 0 else '')
                for k in range(self.item_watch_tabs.count()):
                    if self.item_watch_tabs.tabText(k) == tab_name:
                        self.item_watch_tabs.setCurrentIndex(k)
                        return
            watch_widget = DebugWatchWidget(item)
            watch_widget.pause_debug_requested.connect(self._debugTimer.stop)
            watch_widget.play_debug_requested.connect(self._debugTimer.start)
            self.item_watch_tabs.addTab(watch_widget, tab_name)    
            self._watches[item.__class__.__name__].append(item)
    
    def remove_watch_item(self, tab_index):
        name_parts = self.item_watch_tabs.tabText(tab_index).split()
        if len(name_parts) == 2:
            name_id = int(name_parts[1])
        else:
            name_id = 0
        typename = name_parts[0]
        self._watches[typename].pop(name_id)
        if len(self._watches[typename]) == 0:
            del self._watches[typename]
        self.item_watch_tabs.removeTab(tab_index)
            
    def scene(self):
        return self.view.scene()
    
    def scene_selection_changed(self):
        selected = self.scene().selectedItems()
        en = len(selected) > 0
        self.add_watch_button.setEnabled(en)
        self.add_parent_button.setEnabled(en)
        self.add_children_button.setEnabled(en)
        
    def next_type_name(self, item):
        typename = item.__class__.__name__
        if typename not in self._watches:
            self._watches[typename] = []
            return typename
        if item in self._watches[typename]:
            return self._watches[typename].index(item)
        return typename + ' ' + str(len(self._watches[typename]))
            
    def current_watch_widget(self):
        watch_widget = self.item_watch_tabs.currentWidget()
        return watch_widget
    
    def update_debug_fields(self):
        watch_widget = self.current_watch_widget()
        if watch_widget:
            watch_widget.update_debug_fields()
    