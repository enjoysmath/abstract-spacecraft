from ui_library_search_dockwidget import Ui_LibrarySearchDockWidget
from PyQt5.QtWidgets import (QDockWidget, QGridLayout, QLabel,
                             QGraphicsView)
from PyQt5.QtCore import QRectF
from language_canvas import LanguageCanvas
from file_system_tree_view import FileSystemTreeView
from library_compiler_thread import LibraryCompilerThread
import _pickle as pickle
from arrow import Arrow
from qt_tools import filter_out_descendents

class LibrarySearchDockWidget(QDockWidget, Ui_LibrarySearchDockWidget):
    default_root_dir = 'standard_library'

    def __init__(self):
        QDockWidget.__init__(self)
        Ui_LibrarySearchDockWidget.__init__(self)
        self.setupUi(self)
        self._fileTreeView = FileSystemTreeView(self.default_root_dir)
        self.fileSystemLayout.addWidget(self._fileTreeView)
        self.recompileButton.clicked.connect(self.compile_library)
        query_layout = QGridLayout()
        self.queryDiagramTab.setLayout(query_layout)
        self._queryView = QGraphicsView()
        self._queryView.setScene(QueryPreviewCanvas())
        self._queryView.scale(0.6, 0.6)
        query_layout.addWidget(self._queryView)
        self._compilerThread = None
        self._queryItems = None
    
    def compile_library(self):
        filenames = self._fileTreeView.model().list_all_checked_filenames()
        self._compilerThread = LibraryCompilerThread(filenames)
        self._compilerThread.start()

    def set_items_as_query(self, items, view):
        items = list(filter_out_descendents(list(items)))
        self._queryItems = items
        items_copy = pickle.dumps(items)
        items_copy = pickle.loads(items_copy)
        scene = self._queryView.scene()
        scene.clear()
        scene.setBackgroundBrush(view.scene().backgroundBrush())
        rect = QRectF()
        for item in items_copy:
            if isinstance(item, Arrow):
                item.set_control_points_visible(False)            
            scene.addItem(item)
            rect = rect.united(item.mapToScene(item.boundingRect()).boundingRect())                    
        scene.setSceneRect(rect)
                       
            
class QueryPreviewCanvas(LanguageCanvas):
    def mousePressEvent(self, event):
        pass
    def mouseReleaseEvent(self, event):
        pass
    def mouseMoveEvent(self, event):
        pass
    def mouseDoubleClickEvent(self, event):
        pass
    def contextMenuEvent(self, event):
        pass