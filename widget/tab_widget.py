from PyQt5.QtWidgets import QTabWidget, QMenu, QApplication
from PyQt5.QtCore import Qt, QPoint, QMimeData
from PyQt5.QtGui import QCursor, QPixmap, QDrag, QRegion

class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.tabBar().setMouseTracking(True)
        self.setMovable(True)
        self.tabBar().tabBarClicked.connect(self.tab_bar_clicked)
        
    def __setstate__(self, data):
        self.__init__(new=False)
        #self.setParent(data['parent'])
        for widget, tabname in data['tabs']:
            self.addTab(widget, tabname)
        TabWidget.setup(self)

    def __getstate__(self):
        data = {
          'parent' : self.parent(),
         'tabs' : [],
      }
        tab_list = data['tabs']
        for k in range(self.count()):
            tab_name = self.tabText(k)
            widget = self.widget(k)
            tab_list.append((widget, tab_name))
        return data

    def start_drag_tab_at_screen_pos(self, screen_pos:QPoint):
        tabBar = self.tabBar()
        index = self.tab_index_under_screen_pos(screen_pos)
        draggedTabWidget = self.widget(index)
        draggedTabName = self.tabText(index)
        tabRect = tabBar.tabRect(index)
        mimeData = QMimeData()
        mimeData.dragged_tab_widget = draggedTabWidget
        mimeData.dragged_tab_name = draggedTabName        
        
        drag = QDrag(tabBar)        
        pixmap = QPixmap(tabRect.size())        
        tabBar.render(pixmap, QPoint(), QRegion(tabRect))      
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)

        cursor = QCursor(Qt.OpenHandCursor)        
        drag.setHotSpot(tabBar.mapFromGlobal(screen_pos))
        drag.setDragCursor(cursor.pixmap(),Qt.MoveAction)
        drag.exec_(Qt.MoveAction)
        
    def dragEnterEvent(self, e):
        e.accept()

    def dragLeaveEvent(self,e):
        e.accept()

    def dropEvent(self, e):
        if e.source().parent() is self:
            return
        e.setDropAction(Qt.MoveAction)
        e.accept()
        mimeData = e.mimeData()        
        if hasattr(mimeData, 'dragged_tab_widget'):
            self.addTab(mimeData.dragged_tab_widget, mimeData.dragged_tab_name)

    def tab_bar_clicked(self):
        if QApplication.mouseButtons() == Qt.RightButton:
            self.show_tab_context_menu(screen_pos=QCursor.pos())
        else:
            if QApplication.keyboardModifiers() & Qt.ControlModifier:
                self.start_drag_tab_at_screen_pos(screen_pos=QCursor.pos())
            
    def show_tab_context_menu(self, screen_pos:QPoint):
        pass
    
    def tab_index_under_screen_pos(self, screen_pos:QPoint):
        return self.tab_index_under_pos(self.tabBar().mapFromGlobal(screen_pos))
        
    def tab_index_under_pos(self, pos:QPoint):
        index = self.tabBar().tabAt(pos)
        return index
        
    def show_tab_rename_dialog(self, tab_index:int):
        raise NotImplementedError
        
        
if __name__ == '__main__':
    from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout
    import sys

    class Window(QWidget):
        def __init__(self):
            super().__init__()

            self.dragged_index = None
            tabWidgetOne = TabWidget(self)
            tabWidgetTwo = TabWidget(self)
            tabWidgetOne.addTab(QWidget(), "tab1")
            tabWidgetTwo.addTab(QWidget(), "tab2")

            layout = QHBoxLayout()

            self.moveWidget = None

            layout.addWidget(tabWidgetOne)
            layout.addWidget(tabWidgetTwo)

            self.setLayout(layout)

    app = QApplication(sys.argv)
    window = Window()
    window1 = Window()
    window.show()
    window1.show()
    sys.exit(app.exec_())